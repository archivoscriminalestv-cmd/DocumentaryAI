"""Modelos del Visual Scene Compiler (VSC).

El VSC convierte un ``ShotExecutionRequest`` (VAI) + un ``SceneVisualContext`` en
un ``VisualGenerationRequest`` normalizado e INDEPENDIENTE DEL PROVEEDOR
(Imagen/Flux/Midjourney/SDXL/Runway/Veo/Pika/…). Su responsabilidad termina cuando
existe una petición de generación normalizada.

- ``SceneVisualContext`` es INMUTABLE (frozen): la identidad visual de una escena.
  Todos los planos de la escena la heredan -> consistencia/continuidad.
- ``VisualGenerationRequest`` es la salida serializable (capas global/escena/plano).
- ``GeneratedAsset`` es el resultado (placeholder) de un proveedor.
"""

from dataclasses import dataclass, field

_DEFAULT_GLOBAL_NEGATIVES = (
    "cartoon", "anime", "illustration", "cgi", "3d render", "video game",
    "low quality", "blurry", "deformed", "text", "watermark", "logo",
    "oversaturated", "duplicate", "flat image",
)


@dataclass(frozen=True)
class GlobalStyle:
    """Identidad visual GLOBAL del canal (capa superior, estable)."""

    name: str = "DocumentaryAI"
    style: str = "cinematic documentary"
    realism: str = "photorealistic, ultra detailed, physically based"
    quality: str = "8k, high detail, sharp focus, natural lighting"
    base_negatives: tuple[str, ...] = _DEFAULT_GLOBAL_NEGATIVES


@dataclass(frozen=True)
class SceneVisualContext:
    """Identidad visual INMUTABLE de una escena (continuidad).

    Cada plano de la escena hereda estas propiedades. Ningún plano cambia cámara,
    clima, paleta o iluminación salvo override explícito.
    """

    scene_id: str
    identity: str                 # id de continuidad / nombre de localización
    location: str
    season: str
    time_of_day: str
    weather: str
    color_palette: str
    camera_package: str           # p.ej. "Sony FX6"
    lens_family: str              # p.ej. "35mm prime"
    lighting_language: str
    documentary_style: str
    realism_level: str = "high"   # standard | high | ultra
    provider_constraints: dict = field(default_factory=lambda: {
        "width": 1280, "height": 720, "aspect_ratio": "16:9",
    })
    negative_prompts: tuple[str, ...] = ()
    seed_strategy: str = "per_scene"   # per_scene | per_shot | fixed
    seed: int = 0
    reuse_policy: str = "shot"         # shot | off


@dataclass
class VisualGenerationRequest:
    """Petición de generación NORMALIZADA y provider-agnóstica (salida del VSC)."""

    shot_id: str
    scene_id: str
    media_type: str
    # Prompt compilado por capas (global -> escena -> plano) + negativo.
    prompt: str
    negative_prompt: str
    # Capas explícitas (auditables/recompilables por cualquier adaptador).
    global_style: str
    scene_style: str
    shot_style: str
    # Campos estructurados (para proveedores con parámetros).
    camera: str
    lens: str
    lighting: str
    composition: str
    color: str
    environment: str
    subject: str
    provider_constraints: dict
    reuse_key: str
    seed: int
    seed_strategy: str
    motion_hint: str


@dataclass(frozen=True)
class GeneratedAsset:
    """Resultado (placeholder) de un proveedor visual. Real en el próximo sprint."""

    shot_id: str
    reuse_key: str
    provider: str
    uri: str
    prompt: str
    cached: bool = False
