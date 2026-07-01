# ARCH-VIS — Visual Intelligence System (VIS)

> Estado: **Diseño (solo arquitectura)**. Esta capa todavía NO se implementa.
> Objetivo del documento: módulos, responsabilidades, interfaces, modelos, flujo
> completo e integración con el Media Generation Layer (MGL) existente.
> Restricción: 100 % aditivo. No modifica el pipeline, el compositor, FFmpeg, los
> providers ni la arquitectura ya construida.

---

## 1. Propósito

Hoy una escena narrativa produce **una imagen estática** durante toda su
narración → resultado tipo *PowerPoint*. El VIS convierte cada escena en una
**secuencia audiovisual rica** (varios microplanos con movimiento de cámara,
duraciones variables y distintos tipos de asset), acercando el resultado a
canales como MagnatesMedia, Johnny Harris, Fern, RealLifeLore, Neo o James Jani.

El VIS **piensa como un director de fotografía**: no describe objetos, planifica
**planos, óptica, luz, movimiento y ritmo**. No genera nada: **planifica**. La
generación real sigue siendo responsabilidad del MGL (en sprints posteriores).

```
Narrative Engine  →  Visual Intelligence System (VIS)  →  Media Generation Layer (MGL)
   (Scene/                 (VisualTimeline =                 (Asset real por Shot:
 DirectedScene)             Shot[] con metadata)              imagen/vídeo/reuse/stock)
```

El VIS es una **capa de planificación pura** entre el guion y la generación de
media. Entrada: una `Scene`/`DirectedScene`. Salida: una `VisualTimeline`
(secuencia de `Shot` con metadata completa). Determinista primero; sustituible
por IA (LLM) después, sin cambiar el resto del sistema.

---

## 2. Principios de diseño

1. **Planifica, no genera.** El VIS no llama a APIs, no crea ficheros, no toca
   FFmpeg. Produce una descripción declarativa (la `VisualTimeline`).
2. **Puertos + adaptadores (ARCH-0002 AP-006).** Cada etapa es un `Protocol`;
   habrá una implementación **determinista** (reglas) y, más adelante, una
   implementación **LLM** (vía el `LLMProvider` existente) — intercambiables.
3. **Aditivo y desacoplado.** Paquete nuevo `app/vis/`. No importa hacia atrás:
   el VIS conoce el dominio narrativo (Scene) y emite su propio modelo (Shot);
   el MGL consumirá Shots, pero el VIS no depende del MGL.
4. **Trazabilidad.** Cada `Shot` conserva `scene_id` y `fact_ids` de origen.
5. **Reutilización por sujeto, no por boilerplate.** El VIS calcula un
   `reuse_key` basado en el SUJETO del plano (no en el prompt estilizado), lo que
   resuelve el colapso "todas las escenas comparten una imagen" que provoca hoy
   la interacción Style Engine + Reuse Engine.

---

## 3. Modelos de dominio (`app/vis/models.py`)

Dataclasses puras + enums (sin lógica). Todo serializable a JSON.

### 3.1 Enumeraciones

```python
class ShotType(StrEnum):           # qué muestra el microplano
    ESTABLISHING = "establishing"  # gran plano de contexto
    WIDE         = "wide"
    MEDIUM       = "medium"
    CLOSEUP      = "closeup"        # detalle
    ACTION       = "action"         # algo ocurre/se mueve
    IMPACT       = "impact"         # momento clave / clímax
    AFTERMATH    = "aftermath"      # consecuencia
    REACTION     = "reaction"
    MAP          = "map"            # mapa / infografía geográfica
    INFOGRAPHIC  = "infographic"    # dato / cifra / diagrama
    TRANSITION   = "transition"

class AssetType(StrEnum):           # de dónde sale el píxel
    AI_IMAGE   = "ai_image"
    AI_VIDEO   = "ai_video"
    REUSABLE   = "reusable"         # ya existe en el Asset Store
    STOCK      = "stock"            # banco gratuito (futuro)
    ANIMATION  = "animation"        # animación generada (futuro)

class CameraMove(StrEnum):          # lenguaje de cámara
    STATIC      = "static"
    PUSH_IN     = "push_in"
    PULL_OUT    = "pull_out"
    ZOOM_IN     = "zoom_in"
    ZOOM_OUT    = "zoom_out"
    PAN_LEFT    = "pan_left"
    PAN_RIGHT   = "pan_right"
    TILT_UP     = "tilt_up"
    TILT_DOWN   = "tilt_down"
    DRONE       = "drone"
    TRACKING    = "tracking"
    PARALLAX    = "parallax"
    ORBITAL     = "orbital"
    KEN_BURNS   = "ken_burns"
```

### 3.2 Modelos

```python
@dataclass
class VisualInterpretation:        # "qué ocurre visualmente" en la escena
    scene_id: str
    subject: str                   # sujeto principal ("an asteroid")
    action: str                    # qué pasa ("impacts the Earth")
    setting: str                   # dónde ("outer space, then atmosphere")
    mood: str                      # tono visual ("dramatic, ominous")
    entities: list[str]            # elementos visibles (asteroid, Earth, dust...)
    keywords: list[str]            # términos visuales para prompts/reuse
    fact_ids: list[str]

@dataclass
class CameraSpec:                  # movimiento + parámetros
    move: CameraMove
    speed: float = 1.0             # 0.5 lento … 2.0 rápido
    intensity: float = 0.5         # 0..1 amplitud del movimiento

@dataclass
class ShotIntent:                  # microplano ANTES de la metadata completa
    index: int
    shot_type: ShotType
    description: str               # qué muestra ("space view of the asteroid")
    focus: str                     # sujeto/foco del plano
    emphasis: float = 0.5          # heredado de la escena (Director C-08)

@dataclass
class Shot:                        # microplano COMPLETO (unidad de la timeline)
    id: str                        # p.ej. "scene-03::shot-02"
    scene_id: str
    index: int
    shot_type: ShotType
    prompt: str                    # prompt CINEMATOGRÁFICO (fotografía, no objeto)
    camera: CameraSpec
    lighting: str
    style: str                     # style_id (consistencia visual del vídeo)
    duration: float                # segundos
    asset_type: AssetType
    provider_hint: str = ""        # sugerencia ("ai_image"/"stock"/...); decide el MGL
    reuse_key: str = ""            # clave de reutilización por SUJETO
    fact_ids: list[str] = field(default_factory=list)   # procedencia

@dataclass
class VisualTimeline:              # salida del VIS para una escena
    scene_id: str
    style: str
    shots: list[Shot] = field(default_factory=list)

    @property
    def total_duration(self) -> float:
        return round(sum(s.duration for s in self.shots), 2)
```

> Nota: `Shot` reúne exactamente la metadata pedida (prompt, camera, lighting,
> style, duration, asset_type, provider, reuse_key) más trazabilidad.

---

## 4. Módulos y responsabilidades (`app/vis/`)

Paquete nuevo. Una etapa por módulo; cada una con su **puerto** (Protocol) y una
implementación **determinista** inicial (`Rule…`); más adelante una **LLM**.

| Módulo | Puerto | Responsabilidad |
|--------|--------|-----------------|
| `models.py` | — | Dataclasses + enums (sección 3). |
| `scene_understanding.py` | `SceneInterpreter` | `Scene → VisualInterpretation`. Comprende qué ocurre visualmente (sujeto, acción, entorno, mood, entidades). |
| `shot_decomposer.py` | `ShotDecomposer` | `VisualInterpretation → list[ShotIntent]`. Divide la escena en microplanos (la "secuencia": establishing → detalle → acción → impacto → aftermath…). |
| `camera_director.py` | `CameraDirector` | `ShotIntent → CameraSpec`. Asigna movimiento de cámara por tipo de plano. |
| `pacing.py` | `PacingPlanner` | `ShotIntent → duration`. Decide cuánto dura cada plano según tipo y énfasis. |
| `prompt_director.py` | `CinematicPromptDirector` | `ShotIntent → prompt`. Genera prompts de FOTOGRAFÍA (óptica, luz, film stock, atmósfera). Extiende el `StyleEngine` existente. |
| `asset_strategy.py` | `AssetStrategy` | `ShotIntent → (AssetType, provider_hint, reuse_key)`. Elige la mejor fuente del píxel y calcula la clave de reutilización por sujeto. |
| `timeline_builder.py` | — | Orquesta las etapas y ensambla los `Shot` en una `VisualTimeline`. |
| `visual_intelligence.py` | `VisualIntelligenceSystem` (facade) | Punto de entrada: `plan(scene) → VisualTimeline`. Inyecta las implementaciones de cada etapa. |

---

## 5. Interfaces (puertos)

```python
class SceneInterpreter(Protocol):
    def interpret(self, scene) -> VisualInterpretation: ...

class ShotDecomposer(Protocol):
    def decompose(self, interpretation: VisualInterpretation) -> list[ShotIntent]: ...

class CameraDirector(Protocol):
    def choreograph(self, intent: ShotIntent) -> CameraSpec: ...

class PacingPlanner(Protocol):
    def duration(self, intent: ShotIntent) -> float: ...

class CinematicPromptDirector(Protocol):
    def write(self, intent: ShotIntent, interpretation: VisualInterpretation, *, style: str) -> tuple[str, str]:
        """Devuelve (prompt_cinematográfico, lighting)."""
        ...

class AssetStrategy(Protocol):
    def decide(self, intent: ShotIntent, interpretation: VisualInterpretation) -> "AssetDecision": ...

@dataclass
class AssetDecision:
    asset_type: AssetType
    provider_hint: str
    reuse_key: str
```

Facade:

```python
class VisualIntelligenceSystem:
    def __init__(self, interpreter, decomposer, camera, pacing, prompt, strategy, *, style: str): ...
    def plan(self, scene) -> VisualTimeline: ...
```

Implementaciones previstas (sprints siguientes):

- **Deterministas** (sin IA): `RuleSceneInterpreter`, `RuleShotDecomposer` (plantillas por tipo de acción: impacto, viaje, retrato, mapa…), `RuleCameraDirector` (mapa shot_type→movimiento), `RulePacingPlanner` (tabla shot_type→segundos), `TemplatePromptDirector` (extiende `StyleEngine`), `RuleAssetStrategy`.
- **IA** (después): `LLMSceneInterpreter`, `LLMShotDecomposer`, `LLMPromptDirector` usando el `LLMProvider` ya existente. Misma firma de puerto → swap sin tocar el resto.

---

## 6. Flujo completo (ejemplo: *"Un asteroide impacta contra la Tierra"*)

```
Scene(narration="Un asteroide impacta contra la Tierra")
  │
  ▼  SceneInterpreter.interpret
VisualInterpretation(
  subject="a massive asteroid", action="impacts the Earth",
  setting="outer space → atmosphere → surface", mood="cataclysmic",
  entities=["asteroid","Earth","atmosphere","explosion","dust cloud"])
  │
  ▼  ShotDecomposer.decompose   → secuencia de microplanos
[ ShotIntent(0, ESTABLISHING, "space view of the asteroid"),
  ShotIntent(1, WIDE,        "approach to the planet"),
  ShotIntent(2, ACTION,      "asteroid entering the atmosphere"),
  ShotIntent(3, IMPACT,      "the impact"),
  ShotIntent(4, ACTION,      "explosion"),
  ShotIntent(5, AFTERMATH,   "dust cloud"),
  ShotIntent(6, WIDE,        "view from space") ]
  │
  ▼  por cada intent (en paralelo conceptual):
  │     CameraDirector.choreograph → CameraSpec
  │     PacingPlanner.duration     → segundos
  │     CinematicPromptDirector.write → (prompt, lighting)
  │     AssetStrategy.decide       → (asset_type, provider_hint, reuse_key)
  ▼
VisualTimeline(scene_id, style, shots=[Shot…])  ← 7 shots, ~24 s
```

Ejemplo de un `Shot` resultante (Plano 3 — impacto):

```python
Shot(
  id="scene-03::shot-03", scene_id="scene-03", index=3, shot_type=IMPACT,
  prompt="Ultra realistic cinematic shot of a massive asteroid striking Earth's "
         "surface, volumetric lighting, shockwave, dramatic clouds, 35mm lens, "
         "IMAX, documentary photography, high detail, atmospheric perspective",
  camera=CameraSpec(move=PUSH_IN, speed=1.4, intensity=0.8),
  lighting="hard rim light, fiery key, deep shadows",
  style="cinematic", duration=5.0, asset_type=AI_VIDEO,
  provider_hint="ai_video", reuse_key="asteroid|impact|earth-surface",
  fact_ids=["f12"])
```

Mapeo orientativo **shot_type → cámara → duración** (lo define el `RuleCameraDirector`/`RulePacingPlanner`, configurable):

| shot_type | cámara típica | duración |
|-----------|---------------|----------|
| ESTABLISHING / WIDE | slow push-in / drone | 4–5 s |
| MEDIUM | parallax / slow zoom | 3–4 s |
| CLOSEUP / DETAIL | slow push-in | 2–3 s |
| ACTION | tracking / pan | 3–4 s |
| IMPACT | fast push-in | 4–5 s |
| AFTERMATH | slow pull-out | 3–4 s |
| MAP / INFOGRAPHIC | ken burns / pan | 4–6 s |

---

## 7. Integración con el Media Generation Layer (futuro, aditivo)

El VIS produce la `VisualTimeline`; el **MGL** la consume **plano a plano**. Hoy
el MGL expone `generate_for_scene(scene, media_type)`. La integración futura
añade un punto de entrada a nivel de **Shot** (aditivo, sin romper el actual):

```
VisualTimeline.shots → para cada Shot:
   MGL.generate_for_shot(shot) -> Asset
```

Donde `generate_for_shot` (futuro) mapea de forma declarativa:

| `Shot.asset_type` | Ruta en el MGL (ya existente o futura) |
|-------------------|----------------------------------------|
| `AI_IMAGE` | ProviderRegistry `media_type="image"` (RealImageProvider) |
| `AI_VIDEO` | ProviderRegistry `media_type="video"` (FfmpegVideoProvider hoy; APIs reales después) |
| `REUSABLE` | ReuseEngine con `shot.reuse_key` (no regenerar) |
| `STOCK` | nuevo provider `media_type="stock"` (futuro) |
| `ANIMATION` | nuevo provider `media_type="animation"` (futuro) |

Puntos clave del contrato:

1. **El prompt ya viene cinematográfico** desde el VIS → el MGL solo lo enruta al
   provider. (El `StyleEngine` se mantiene; el VIS lo usa internamente para la
   consistencia del vídeo, no lo duplica.)
2. **`reuse_key` por sujeto** → el ReuseEngine deduplica por sujeto del plano, no
   por el prompt estilizado. Esto **corrige** el colapso actual (todas las
   escenas comparten una imagen): dos planos del mismo asteroide se reutilizan;
   planos distintos generan assets distintos.
3. **El movimiento de cámara** (`CameraSpec`) NO lo aplica el MGL: lo aplicará una
   etapa de render de movimiento (Ken Burns/zoom/pan sobre stills, o clip de
   vídeo nativo) **downstream**, alimentando el `MediaNormalizer`/`FfmpegVideoComposer`
   ya existentes. El VIS solo lo **declara**; nada de esto se toca ahora.
4. **El ensamblador** (`DocumentaryAssembler`) evolucionará para iterar
   `timeline.shots` en lugar de una imagen por escena — aditivo, en un sprint
   posterior.

```
Narrative Engine → VIS(plan) → VisualTimeline
                                   │  (futuro)
                                   ▼
                       MGL.generate_for_shot(shot)  → Asset por plano
                                   │
                                   ▼
                  Motion render (cámara) → Normalizer → Composer → .mp4
                  (todo esto ya existe / futuro; el VIS no lo toca)
```

---

## 8. Qué NO toca este diseño (additividad)

- **No** modifica `Scene`/`DirectedScene` ni el Narrative Engine.
- **No** modifica el MGL, el `ProviderRegistry`, el `ReuseEngine`, el `StyleEngine`,
  el Asset Store ni los providers.
- **No** toca `MediaNormalizer`, `FfmpegVideoComposer` ni el pipeline de vídeo.
- **No** conecta APIs ni genera píxeles.
- Es un **paquete nuevo** `app/vis/` + (más adelante) **un** punto de entrada
  aditivo en el MGL (`generate_for_shot`). Nada existente cambia de comportamiento.

---

## 9. Roadmap de implementación (sprints siguientes)

1. **VIS-1 — Esqueleto:** `app/vis/models.py` + puertos (Protocols), sin lógica.
2. **VIS-2 — Deterministas:** `Rule*` de cada etapa + `VisualIntelligenceSystem.plan`
   → produce `VisualTimeline` real (sin IA, sin red). Tests deterministas.
3. **VIS-3 — Integración MGL:** `MGL.generate_for_shot(shot)` (aditivo) + routing por
   `asset_type` + `reuse_key` por sujeto.
4. **VIS-4 — Render de movimiento:** aplicar `CameraSpec` (Ken Burns/zoom/pan sobre
   stills; clips de vídeo) hacia el `Normalizer`/`Composer` existentes.
5. **VIS-5 — IA:** `LLM*` para interpretación/decomposición/prompt (vía `LLMProvider`),
   y providers reales nuevos (stock, animación, vídeo IA) registrados en el orquestador.

---

## 10. Decisiones abiertas (para validar antes de implementar)

- **Entrada del VIS:** ¿`DirectedScene` (con `emphasis`/`tone`/`duration_hint`)
  como entrada preferida para heredar el ritmo del Director (C-08)? Propuesto: sí.
- **Nº de planos por escena:** rango objetivo (p.ej. 3–8) y cómo escalar con la
  longitud/énfasis de la narración. Propuesto: derivado del tipo de acción + énfasis.
- **`reuse_key`:** formato canónico (p.ej. `subject|shot_type|setting` normalizado).
- **Sincronía narración↔planos:** ¿la suma de duraciones de planos debe ajustarse
  a la duración del audio de la escena? Propuesto: el VIS planifica duraciones
  "ideales"; una etapa de ajuste posterior las re-escala al audio real.
```
