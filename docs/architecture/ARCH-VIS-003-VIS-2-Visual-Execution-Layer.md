# ARCH-VIS-003 — VIS-2: Visual Execution Layer

> Estado: **Diseño** (arquitectura + modelos + reglas de transformación +
> contrato con MGL). NO implementa, NO usa LLM/APIs. NO modifica RDA, VIS-1,
> providers ni FFmpeg. Determinista.
>
> VIS-2 toma el `VisualPlan` de VIS-1 (`PlannedShot[]` con directivas de cámara/
> luz/ritmo) y lo convierte en **decisiones de generación ejecutables**
> (`ShotExecutionRequest`) que consumirá el MGL. Su misión: **eliminar la
> repetición visual y el "PowerPoint effect"** garantizando que cada plano sea
> visualmente único.

```
VIS-1 (VisualPlan / PlannedShot)
        │   VIS-2: ensamblar prompt + variación obligatoria + unicidad
        ▼
ExecutionPlan (ShotExecutionRequest[])  ──►  MGL.generate_for_shot(req)  [futuro, aditivo]
                                                   │ ProviderRegistry (media_type)
                                                   │ ReuseEngine (reuse_key)  ← sin modificar
                                                   ▼ Asset único por plano
```

---

## 1. Propósito

VIS-1 decide **qué rodar y con qué dirección** (shot_type, cámara, luz, ritmo).
VIS-2 decide **cómo materializarlo**: el prompt ejecutable real, la lente, el
ángulo y la composición concretos, y las **reglas duras** que impiden que dos
planos se parezcan. Es la última capa antes del MGL.

Problema que resuelve (medido en sprints anteriores): el MGL + StyleEngine +
ReuseEngine colapsaban todas las escenas a **una sola imagen** (el boilerplate de
estilo dominaba el prompt → el ReuseEngine los veía iguales). VIS-2 lo elimina de
raíz: hace cada prompt **genuinamente distinto** (lente/ángulo/composición/sujeto)
y **controla la clave de reutilización**, sin tocar el ReuseEngine.

---

## 2. Entradas y salidas

**Entrada:** `VisualPlan` (VIS-1) — `PlannedShot[]` con `shot_type`, `camera`
(CameraDirective), `lighting` (LightingDirective), `duration`, `grade`,
`asset_type`, `reuse_key`, `fact_ids`, y el `StyleTarget`/`style`.

**Salida:** `ExecutionPlan` — `ShotExecutionRequest[]`: el objeto exacto que el
MGL ejecutará (prompt, negative prompt, media_type, dimensiones, reuse_key,
variation_seed, motion, grade, style). Más un `variation_report` auditable.

---

## 3. Modelos (`app/vis/execution/models.py` — futuro)

VIS-2 introduce los **ejes de variación** (vocabulario propio, alineado con
ARCH-VIS-000 §3/§5) y el contrato de ejecución.

```python
class Lens(StrEnum):                 # §3
    ULTRA_WIDE = "ultra-wide 18mm"
    WIDE       = "wide 35mm"
    NORMAL     = "normal 50mm"
    TELE       = "tele 100mm"
    SUPER_TELE = "super-tele 200mm"
    MACRO      = "macro"

class Angle(StrEnum):                # ángulo de cámara
    EYE_LEVEL = "eye-level"
    LOW       = "low-angle"
    HIGH      = "high-angle"
    DUTCH     = "dutch-angle"
    AERIAL    = "aerial top-down"
    OTS       = "over-the-shoulder"
    WORMS_EYE = "worm's-eye"

class Composition(StrEnum):          # §5
    THIRDS        = "rule of thirds"
    CENTERED      = "centered symmetry"
    LEADING_LINES = "leading lines"
    FRAME_IN_FRAME= "frame within a frame"
    NEGATIVE_SPACE= "negative space"
    LAYERED       = "foreground occlusion / layered depth"

@dataclass
class VisualChoices:                 # decisiones de "look" por plano (ejes de variación)
    lens: Lens
    angle: Angle
    composition: Composition
    depth_of_field: str              # "shallow" | "deep"

@dataclass
class ShotPrompt:                    # prompt ejecutable (texto que ve el provider)
    prompt: str                      # gramática §12 ensamblada
    negative_prompt: str             # anti-clichés + anti-powerpoint (§12.4)

@dataclass
class ShotExecutionRequest:          # CONTRATO con el MGL
    shot_id: str
    scene_id: str
    media_type: str                  # "image" | "video"  (de asset_type)
    prompt: str
    negative_prompt: str
    width: int
    height: int
    aspect_ratio: str                # "16:9"
    grade: str
    style: str
    reuse_key: str                   # SUJETO recurrente (motivo) o "" => único
    variation_seed: int              # diversidad generativa determinista por plano
    motion: dict                     # CameraDirective serializada (para render/vídeo)
    provider_hint: str
    fingerprint: str                 # huella de unicidad (auditoría)

@dataclass
class ExecutionPlan:
    scene_id: str
    requests: list[ShotExecutionRequest] = field(default_factory=list)
    variation_report: dict = field(default_factory=dict)
```

---

## 4. Contratos (puertos — `Protocol`)

```python
class VariationEngine(Protocol):
    """Asigna lens/angle/composition garantizando variación entre planos."""
    def choose(self, shot, *, index: int, used: "VariationLedger") -> VisualChoices: ...

class CinematicPromptAssembler(Protocol):
    """PlannedShot + VisualChoices → ShotPrompt (gramática §12). Determinista."""
    def assemble(self, shot, choices: VisualChoices, *, style: str) -> ShotPrompt: ...

class UniquenessGuard(Protocol):
    """Garantiza que cada plano sea visualmente único dentro del plan."""
    def fingerprint(self, shot, choices: VisualChoices) -> str: ...
    def ensure_unique(self, fp: str, choices: VisualChoices, used: "VariationLedger") -> VisualChoices: ...

class ExecutionCompiler(Protocol):
    """Fachada VIS-2: VisualPlan → ExecutionPlan (lista de requests al MGL)."""
    def compile(self, visual_plan) -> ExecutionPlan: ...

# Contrato que el MGL expondrá (FUTURO, aditivo; no modifica providers/reuse):
class ShotExecutor(Protocol):
    def generate_for_shot(self, request: ShotExecutionRequest): ...  # -> Asset
```

`VariationLedger` = registro interno de combinaciones ya usadas (lentes, ángulos,
composiciones, fingerprints) para imponer variación. Implementaciones VIS-2
deterministas (`Rule*`); una variante `LLM*` (prompt más rico) podrá sustituir
solo `CinematicPromptAssembler` con la misma firma.

---

## 5. Reglas de transformación PlannedShot → prompt ejecutable

### 5.1 Ensamblaje del prompt (gramática ARCH-VIS-000 §12)

Orden canónico, todos los componentes **obligatorios** (regla dura R12.1):

```
[shot_type/encuadre] + [sujeto + acción] + [entorno] +
[VisualChoices.lens + DoF] + [VisualChoices.composition] + [VisualChoices.angle] +
[LightingDirective.descriptor] + [grade] + [style/medio] + [calidad/atmósfera]
```

- **shot_type, lighting, grade, style** vienen de `PlannedShot` (VIS-1).
- **lens, angle, composition, DoF** los aporta VIS-2 (`VariationEngine`).
- **sujeto+acción+entorno** se derivan del `PlannedShot` (foco) — sin contenido
  inventado fuera de los `fact_ids`.

### 5.2 Constraints duros (cámara/lente/luz/composición)

Reglas que VIS-2 **valida y repara** (un `ShotPrompt` que las incumpla se rechaza):

- **HARD-1 (MUST)** El prompt incluye SIEMPRE lente, iluminación, composición y
  grade (R12.1). Falta cualquiera → inválido.
- **HARD-2 (MUST)** El `negative_prompt` incluye SIEMPRE: `text, watermark, logo,
  low quality, deformed, oversaturated, generic stock photo, **static, flat,
  slideshow, powerpoint, identical framing, duplicate**`.
- **HARD-3 (MUST)** La lente es coherente con el `shot_type` (R3.2): no macro en
  establishing, no ultra-wide en detalle íntimo.
- **HARD-4 (MUST)** El movimiento (`motion`) nunca es `static` por defecto (R2.1);
  imágenes 2D → ken_burns/parallax; vídeo → movimiento real.

### 5.3 Mapeo grade/luz al texto

`grade` (de VIS-1) y `LightingDirective.descriptor` se insertan literalmente para
mantener consistencia con la referencia (RDA) y la emoción (§7). No se recalculan.

---

## 6. Variación visual obligatoria (anti-PowerPoint) — el corazón de VIS-2

VIS-2 rota tres **ejes de variación** (lente, ángulo, composición) por plano,
con invariantes duros sobre el `ExecutionPlan`:

- **VAR-1 (MUST)** Dos planos **consecutivos** NO comparten la **misma lente**.
- **VAR-2 (MUST)** Dos planos consecutivos NO comparten el **mismo ángulo**.
- **VAR-3 (MUST)** Dos planos consecutivos NO comparten la **misma composición**.
- **VAR-4 (MUST)** La terna `(lens, angle, composition)` es **única dentro de la
  escena**; si se agota el espacio, se varía un eje secundario (DoF, distancia
  focal, hora/luz) o se permite repetir el menos perceptible.
- **VAR-5 (MUST)** Alternar escala (wide ↔ tele) entre planos contiguos (R3.3/R13.3).
- **VAR-6 (SHOULD)** Evitar repetir la terna también entre **escenas adyacentes**
  (continuidad sin monotonía).

La selección es **determinista**: para el plano `i`, `VariationEngine` elige de los
candidatos compatibles con su `shot_type` el primero que respete VAR-1..5 dado el
`VariationLedger` (orden estable por índice). Sin aleatoriedad real; reproducible.

---

## 7. Garantía de unicidad visual (cada asset único)

Cadena de defensa, de lo estructural a lo generativo:

1. **Fingerprint de unicidad** = hash determinista de
   `(subject_core, shot_type, lens, angle, composition, lighting_key)`.
   `UniquenessGuard.ensure_unique` exige que sea **único** en el `ExecutionPlan`;
   ante colisión, perturba un eje (VAR-4) hasta lograr unicidad.
2. **Prompt genuinamente distinto** → el `ReuseEngine` existente NO los confunde
   (los tokens distintivos —lente/ángulo/composición/sujeto— dominan, no el
   boilerplate de estilo). Esto **elimina** el colapso "una imagen por vídeo".
3. **Control de `reuse_key`** (clave del contrato con el MGL):
   - **Motivo recurrente** (mismo sujeto a propósito, p.ej. el logo de un país que
     reaparece) → `reuse_key` compartido ⇒ el MGL **reutiliza** (coste/coherencia).
   - **Plano normal** → `reuse_key = ""` (o único por shot) ⇒ el MGL **NO reutiliza**
     ⇒ generación **única garantizada**.
4. **variation_seed** determinista por `shot_id` → diversidad generativa adicional
   en el provider aunque dos prompts queden parecidos (defensa en profundidad).

> Resultado: la unicidad se garantiza **sin modificar el ReuseEngine ni los
> providers**: VIS-2 solo les entrega prompts distintos y `reuse_key` correctos.

---

## 8. Contrato con el MGL

VIS-2 produce `ShotExecutionRequest`; el MGL expondrá (FUTURO, **aditivo**, sin
cambiar providers/reuse internos):

```
MGL.generate_for_shot(request: ShotExecutionRequest) -> Asset
   1. media_type  → ProviderRegistry.select(media_type)  (image/video ya existen)
   2. reuse_key   → ReuseEngine: si != "" y hay match por SUJETO -> reutiliza;
                    si "" -> genera nuevo (unicidad)
   3. prompt/negative_prompt/seed/dims → provider
   4. persiste Asset en el Asset Store (con shot_id/scene_id)
```

Puntos del contrato:

- **C-1** VIS-2 NO llama a providers ni genera: solo emite requests. La ejecución
  es del MGL.
- **C-2** `reuse_key` es la **única** palanca de reutilización; VIS-2 la fija por
  sujeto (motivo) o la vacía (único). El ReuseEngine no cambia.
- **C-3** `media_type` se deriva de `asset_type` (AI_IMAGE→image, AI_VIDEO→video;
  STOCK/ANIMATION → futuros media_type, ya soportados por el registry declarativo).
- **C-4** `motion` (CameraDirective) viaja en el request para la etapa de render de
  movimiento (futuro), no para el provider de imagen.

---

## 9. Invariantes verificables (criterio de aceptación)

Un `ExecutionPlan` es válido si, de forma comprobable:

1. Todo `ShotExecutionRequest` cumple HARD-1..4 (prompt completo + negatives + lente
   coherente + movimiento no estático).
2. Se cumplen VAR-1..5 (no repetición de lente/ángulo/composición consecutivos;
   ternas únicas por escena; alternancia de escala).
3. Los `fingerprint` son **únicos** dentro del plan (salvo motivos con `reuse_key`
   compartido a propósito).
4. Ningún `reuse_key` vacío comparte fingerprint con otro (no hay reutilización
   accidental).
5. El `variation_report` documenta lentes/ángulos/composiciones usados y cualquier
   perturbación aplicada (auditoría).

---

## 10. Determinismo, additividad y límites

- **Determinista:** mismas entradas → mismo `ExecutionPlan` (variación por índice/
  hash; seeds derivadas de ids). Sin LLM, sin red.
- **Aditivo:** paquete nuevo `app/vis/execution/` (futuro). Consume el `VisualPlan`
  de VIS-1; emite requests para el MGL. NO modifica RDA, VIS-1, providers, FFmpeg
  ni el ReuseEngine. El `generate_for_shot` del MGL será un añadido posterior.
- **VIS-2 NO hace:** generar imágenes/vídeo (MGL), aplicar la cámara (render),
  decidir ritmo/estructura (VIS-1), descargar/analizar (RDA).

---

## 11. Ejemplo

`PlannedShot` (VIS-1): IMPACT, camera push_in int 0.9, lighting low-key high,
grade "warm vivid teal-amber", asset_type AI_IMAGE, reuse_key="" (no motivo).

VIS-2 (plano i, previo usó WIDE/eye-level/thirds):
- `VariationEngine` → lens TELE (≠ previo), angle LOW (≠ previo), composition
  LEADING_LINES (≠ previo), DoF shallow → terna única.
- `CinematicPromptAssembler` →
  `"Cinematic close impact shot of <subject> <action>, <setting>, tele 100mm
  shallow depth of field, leading lines, low-angle, low-key chiaroscuro hard rim
  light, warm vivid teal-amber grade, IMAX documentary photography, hyper-detailed,
  atmospheric, 8k"`,
  negative = `"text, watermark, low quality, deformed, oversaturated, generic
  stock photo, static, flat, slideshow, powerpoint, identical framing, duplicate"`.
- `reuse_key=""` → el MGL genera **nuevo** (único). `variation_seed=hash(shot_id)`.
- `motion = {move: push_in, speed: 1.4, intensity: 0.9}` para el render.

Resultado: aunque la escena tenga 5 planos del mismo tema, cada uno usa lente/
ángulo/composición distintos y prompt distinto ⇒ **5 imágenes únicas**, no una.

---

## 12. Roadmap y decisiones abiertas

**Roadmap:** VIS-2.0 (este doc) → VIS-2.1 (impl `Rule*` + tests, sin red) →
VIS-3 (MGL `generate_for_shot`, aditivo) → render de movimiento → variante `LLM*`
del `CinematicPromptAssembler`.

**Decisiones abiertas:**
- **Sujeto del prompt:** ¿VIS-2 extrae `subject_core` del `PlannedShot.focus`/
  `fact_ids` con plantillas, o se delega a la variante LLM en VIS-2.x? Propuesto:
  plantilla determinista ahora; LLM opcional después (mismo contrato).
- **Política de motivos (`reuse_key`):** ¿quién marca un plano como "motivo
  recurrente"? Propuesto: VIS-1 lo indica (sujeto estable) y VIS-2 lo respeta; por
  defecto todo es único.
- **Espacio de variación:** nº de combinaciones (6 lentes × 7 ángulos × 6 comp. =
  252) suficiente para escenas de 3–8 planos; definir prioridad de ejes al agotar.
```
