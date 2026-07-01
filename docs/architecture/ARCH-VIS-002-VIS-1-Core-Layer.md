# ARCH-VIS-002 — VIS-1: Visual Intelligence Core Layer

> Estado: **Diseño** (arquitectura + modelos + contratos + flujo). NO implementa,
> NO usa APIs ni LLM, NO toca MGL / FFmpeg / providers. Determinista por diseño.
>
> VIS-1 es el **puente** entre el análisis cinematográfico (RDA, ARCH-VIS-001) y la
> generación visual (MGL): consume un `CinematicProfile` del RDA + una `Scene`
> narrativa y produce un `VisualPlan` (secuencia de planos con directivas de
> cámara, luz y ritmo), regido por ARCH-VIS-000 y **calibrado** por las métricas
> reales del RDA.

```
RDA (CinematicProfile)  ─┐
                         ├─►  VIS-1  ─►  VisualPlan  ─►  (VIS-2 prompts) ─► MGL ─► render
Narrative (Scene/         │     │                              [futuro]      [futuro]
DirectedScene) ──────────┘     └─ reglas ARCH-VIS-000 + StyleTarget del RDA
```

---

## 1. Propósito

Convertir, de forma **determinista y trazable**, lo que el RDA *aprendió* de
referencias (cut rate, ASL, movement/lighting tendency, color) en **decisiones
de dirección** para cada escena: cuántos planos, de qué tipo, con qué cámara,
qué luz y qué duración. VIS-1 no escribe prompts finales ni genera píxeles:
decide la **estructura cinematográfica** (el "qué rodar y cómo"). El prompt
cinematográfico (VIS-2) y la generación (MGL) son capas posteriores.

Objetivo: que el look "tipo Fern / Johnny Harris / MagnatesMedia" sea
**reproducible** porque deriva de métricas medidas, no de intuición.

---

## 2. Entradas y salidas (contrato externo)

**Entradas**
1. `DirectedScene` (preferida) o `Scene` — beat narrativo: `id, title, narration,
   fact_ids` y (si DirectedScene) `tone, emphasis, duration_hint`.
2. `StyleTarget` — gramática objetivo derivada de uno o varios `CinematicProfile`
   del RDA (ver §4). Es el "ADN visual" a emular.
3. `style: str` — id global del StyleEngine (consistencia del vídeo).

**Salida**
- `VisualPlan` (por escena) — secuencia de `PlannedShot` con directivas completas
  de cámara/luz/ritmo + trazabilidad de cada decisión. Varios `VisualPlan`
  forman el plan del documental.

VIS-1 **no** depende del MGL: emite un `VisualPlan` que el MGL consumirá más
adelante (`generate_for_shot`, fuera de alcance aquí).

---

## 3. Modelos (`app/vis/models.py` — futuro)

Reutiliza los enums de ARCH-VIS (`ShotType`, `CameraMove`, `AssetType`).

```python
# --- ADN visual derivado del RDA (lo que VIS-1 "emula") ----------------------
@dataclass
class StyleTarget:
    source_refs: list[str]          # qué CinematicProfile(s) lo originan
    # Ritmo (de cut_rate / ASL / variety)
    target_asl: float               # duración de plano objetivo (s)
    pacing_tier: str                # very_fast | fast | moderate | slow
    variety: str                    # metronomic | moderate | varied
    # Cámara (de movement_tendency)
    movement_bias: float            # 0..1 probabilidad/energía de movimiento
    intensity_bias: float           # 0..1 amplitud media del movimiento
    preferred_moves: list[str]      # subconjunto de CameraMove preferidos
    # Luz (de lighting_tendency)
    lighting_key: str               # low-key | balanced | high-key
    contrast_level: str             # flat | normal | high
    # Color/grade (de color_temperature / saturation)
    color_temperature: str          # warm | cool | neutral
    saturation: str                 # vivid | moderate | muted

# --- Directivas (decisiones atómicas con su porqué) --------------------------
@dataclass
class CameraDirective:
    move: CameraMove
    speed: float                    # 0.5 lento … 1.6 rápido
    intensity: float                # 0..1
    rationale: str                  # métrica RDA + regla ARCH-VIS-000 (Rx.y)

@dataclass
class LightingDirective:
    key: str                        # low-key | balanced | high-key
    contrast: str                   # flat | normal | high
    descriptor: str                 # p.ej. "low-key chiaroscuro, rim light"
    rationale: str

@dataclass
class PacingDecision:
    duration: float
    rationale: str

# --- Plano planificado + plan de escena --------------------------------------
@dataclass
class PlannedShot:
    id: str                         # "scene-03::shot-02"
    scene_id: str
    index: int
    shot_type: ShotType
    camera: CameraDirective
    lighting: LightingDirective
    duration: float
    grade: str                      # "teal-orange, muted" (para VIS-2)
    asset_type: AssetType
    reuse_key: str                  # por SUJETO (no por prompt estilizado)
    fact_ids: list[str] = field(default_factory=list)
    prompt: str = ""                # se rellena en VIS-2 (no en VIS-1)

@dataclass
class VisualPlan:
    scene_id: str
    style: str
    style_target: StyleTarget
    shots: list[PlannedShot] = field(default_factory=list)
    decisions_log: list[str] = field(default_factory=list)  # trazabilidad global

    @property
    def total_duration(self) -> float:
        return round(sum(s.duration for s in self.shots), 2)
```

> `VisualPlan` es un superconjunto del `VisualTimeline` de ARCH-VIS: añade
> **directivas con rationale** (cámara/luz/ritmo) y el `StyleTarget` que las rige.

---

## 4. Contratos (puertos — `Protocol`)

```python
class StyleTargetMapper(Protocol):
    """RDA → VIS: traduce métricas medidas en un objetivo de estilo."""
    def from_profile(self, profile: CinematicProfile) -> StyleTarget: ...
    def from_profiles(self, profiles: list[CinematicProfile]) -> StyleTarget: ...  # media de un canal

class ShotSequencer(Protocol):
    """Escena + StyleTarget → secuencia de tipos de plano (cuántos y cuáles)."""
    def sequence(self, scene, target: StyleTarget) -> list[ShotType]: ...

class CameraDirector(Protocol):
    def direct(self, shot_type: ShotType, target: StyleTarget, *, tone: str, index: int, prev: CameraMove | None) -> CameraDirective: ...

class LightingDirector(Protocol):
    def light(self, shot_type: ShotType, target: StyleTarget, *, tone: str) -> LightingDirective: ...

class PacingPlanner(Protocol):
    def duration(self, shot_type: ShotType, target: StyleTarget, *, emphasis: float, index: int) -> PacingDecision: ...

class AssetStrategy(Protocol):
    def decide(self, shot_type: ShotType, scene) -> tuple[AssetType, str]: ...  # (asset_type, reuse_key)

class VisualPlanner(Protocol):
    """Fachada VIS-1: orquesta los anteriores en un VisualPlan determinista."""
    def plan(self, scene, target: StyleTarget, *, style: str) -> VisualPlan: ...
```

Implementaciones de VIS-1 (deterministas, **sin LLM**): `RuleStyleTargetMapper`,
`RuleShotSequencer`, `RuleCameraDirector`, `RuleLightingDirector`,
`RulePacingPlanner`, `RuleAssetStrategy`, `DeterministicVisualPlanner`. Más
adelante, variantes `LLM*` con la **misma firma** (swap sin tocar el resto).

---

## 5. Mapeo explícito RDA → decisiones VIS (el núcleo del puente)

### 5.1 Ritmo — `cut_rate` / `avg_shot_length` / `shot_length_variety` → pacing

| Métrica RDA | Decisión VIS |
|-------------|--------------|
| `avg_shot_length` | `StyleTarget.target_asl` (clamp 1.5–8 s) |
| `pacing_tier` | sesgo del nº de planos por escena |
| `shot_length_variety` | jitter de duración entre planos (anti-metrónomo §13.4) |

- **Nº de planos por escena** = `round(duración_escena / target_asl)`, acotado a
  **[3, 8]** (ARCH-VIS-000 R1.1 mínimo 3; tope para evitar microplanos).
- **Duración por plano** = `target_asl × factor(shot_type)` (IMPACT ×1.3,
  DETAIL ×0.7, etc., tabla §6 de ARCH-VIS-000) × `modulador(emphasis)`, con
  **jitter** según `variety` (`metronomic`→±5 %, `moderate`→±20 %, `varied`→±40 %).
  Regla dura: no >2 planos consecutivos con la misma duración (R13.4).

### 5.2 Cámara — `movement_tendency` → directivas de cámara

| `movement_tendency` (RDA) | `movement_bias` | `intensity_bias` | `preferred_moves` |
|---------------------------|-----------------|------------------|-------------------|
| `dynamic` | 0.9 | 0.7 | tracking, push_in, drone, orbital |
| `moderate` | 0.6 | 0.5 | push_in, parallax, pan, ken_burns |
| `mostly_static` | 0.4 | 0.35 | ken_burns, parallax, subtle push_in |

- `CameraDirector` elige un `CameraMove` de `preferred_moves` adecuado al
  `shot_type` (IMPACT→push_in rápido; ESTABLISHING→drone/orbital;
  CLOSEUP→push_in lento), con `intensity≈intensity_bias` (alta solo en
  ACTION/IMPACT, R11.3) y **nunca repite el move del plano anterior** (R13.2).
- **Nunca `static` por defecto** (R2.1): incluso en `mostly_static` se usa
  ken_burns/parallax suave.

### 5.3 Luz — `lighting_tendency` → decisiones de iluminación

| `lighting_tendency` (RDA) | `lighting_key` | `contrast_level` | descriptor base |
|---------------------------|----------------|------------------|-----------------|
| `low-key high-contrast` | low-key | high | "low-key chiaroscuro, hard rim light" |
| `balanced` / `… normal` | balanced | normal | "soft natural light" |
| `high-key …` | high-key | low/normal | "bright high-key, soft fill" |

- El `tone` de la escena (Director C-08) **modula** la luz dentro del objetivo
  (R7.1): `dramatic`/`investigative` empujan a más contraste/low-key aunque la
  referencia sea balanced; `conclusive` hacia golden/soft.

### 5.4 Color/grade — `color_temperature` + `saturation_tendency` → grade

| RDA | `grade` (para VIS-2) |
|-----|----------------------|
| `warm` + `vivid` | "warm, vivid teal-and-amber grade" |
| `cool` + `muted` | "cool, desaturated grade" |
| `neutral` + `moderate` | "neutral natural grade" |

El `grade` viaja en `PlannedShot.grade` y lo consumirá VIS-2 al construir el
prompt (ARCH-VIS-000 §12), garantizando consistencia con la referencia.

> **Trazabilidad:** cada directiva lleva `rationale` con la métrica RDA y la
> regla ARCH-VIS-000 aplicada (p.ej. *"push_in intensity 0.7 — RDA
> movement_tendency=dynamic; R2.1/R11.3"*). El `VisualPlan` es auditable.

---

## 6. Flujo completo (determinista)

```
ReferenceLibrary (RDA)
   │  StyleTargetMapper.from_profiles → StyleTarget   (ADN visual del canal)
   ▼
Scene/DirectedScene + StyleTarget + style
   │  VisualPlanner.plan:
   │    1) ShotSequencer.sequence  → [ShotType…]  (nº calibrado por target_asl)
   │    2) por cada plano (index):
   │         PacingPlanner.duration   → PacingDecision   (§5.1)
   │         CameraDirector.direct     → CameraDirective  (§5.2, evita repetir)
   │         LightingDirector.light    → LightingDirective(§5.3, modula por tone)
   │         AssetStrategy.decide       → (AssetType, reuse_key por sujeto)
   │         grade ← StyleTarget        (§5.4)
   │    3) aplicar invariantes anti-repetición (§13: no shot_type/move/duración
   │       repetidos consecutivos; variar escala)
   ▼
VisualPlan(shots=[PlannedShot…], decisions_log=[…])
   │  (futuro) VIS-2: rellena PlannedShot.prompt (gramática §12)
   ▼  (futuro) MGL.generate_for_shot(shot) por asset_type + reuse_key
```

---

## 7. Ejemplo (referencia "tráiler rápido, dinámico, low-key, teal-orange")

RDA `CinematicProfile`: `avg_shot_length=2.3`, `pacing_tier=fast`,
`movement_tendency=dynamic`, `lighting_tendency="low-key high-contrast"`,
`color_temperature=warm`, `saturation=vivid`.

→ `StyleTarget`: target_asl 2.3, fast, movement_bias 0.9, low-key/high,
warm/vivid.

Escena (duración ~12 s, tone=dramatic) → VIS-1 `VisualPlan`:

| # | shot_type | cámara | duración | luz | grade |
|---|-----------|--------|----------|-----|-------|
| 1 | ESTABLISHING | drone, int 0.6 | 3.0 s | low-key chiaroscuro | warm vivid teal-amber |
| 2 | DETAIL | push_in, int 0.5 | 1.8 s | low-key hard rim | " |
| 3 | ACTION | tracking, int 0.8 | 2.4 s | low-key | " |
| 4 | IMPACT | push_in, int 0.9 | 3.0 s | hard rim, deep shadows | " |
| 5 | AFTERMATH | pull_out, int 0.4 | 2.0 s | low-key | " |

5 planos (~12 s ≈ 12/2.3), cámara dinámica, sin moves repetidos, duraciones
variadas, low-key + teal-orange — la **gramática de la referencia, aplicada a
nuestro contenido** (no su contenido).

---

## 8. Determinismo, additividad y límites

- **Determinista:** mismas entradas → mismo `VisualPlan`. Sin LLM, sin red, sin
  aleatoriedad (el "jitter" es determinista en función de index/variety).
- **Aditivo:** paquete nuevo `app/vis/` (futuro). Consume `app.rda` (modelos) y la
  `Scene` narrativa. No toca MGL, providers, FFmpeg, ReuseEngine, StyleEngine.
- **No hace (VIS-1):** prompts finales (VIS-2), generación (MGL), aplicación real
  de la cámara/movimiento (render), descarga/analisis (RDA).
- **reuse_key por sujeto** (no por prompt) — resuelve el colapso reuse+style.

---

## 9. Roadmap

1. **VIS-1.0 (este doc):** arquitectura + modelos + contratos + flujo + mapeo.
2. **VIS-1.1 (impl):** `app/vis/` con modelos + `Rule*` deterministas +
   `DeterministicVisualPlanner` + tests (sin red/LLM). Entrada: `CinematicProfile`
   real del RDA → `VisualPlan`.
3. **VIS-2:** `CinematicPromptDirector` rellena `PlannedShot.prompt` (§12).
4. **VIS-3:** `MGL.generate_for_shot(shot)` (aditivo) por `asset_type`+`reuse_key`.
5. **VIS-4:** render de movimiento (cámara) → Normalizer/Composer existentes.
6. **VIS-5:** variantes `LLM*` (mismos contratos) para decisiones más ricas.

---

## 10. Decisiones abiertas (validar antes de VIS-1.1)

- **Duración de escena** para el cálculo de nº de planos: ¿`DirectedScene.duration_hint`
  o estimación por palabras de la narración, re-escalada luego al audio real?
  Propuesto: hint si existe, si no estimación; re-escalado en render.
- **Origen del `StyleTarget`:** ¿un perfil único, o la media de varios perfiles de
  un mismo canal en la `ReferenceLibrary`? Propuesto: ambos (`from_profile` /
  `from_profiles`); por defecto la media del canal de referencia elegido.
- **Tope de planos por escena:** [3, 8] propuesto; ajustable por `pacing_tier`.
```
