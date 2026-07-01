"""Modelos de VAI (Visual AI Director).

VAI es el Director de Fotografía: convierte un ``Shot`` de VIS en una
``VisualSpecification`` (decisiones fotográficas estructuradas) y, finalmente, en
un ``ShotExecutionRequest`` listo para el MGL. NO genera imágenes, NO llama a
proveedores: solo especifica.

Diseño clave (independencia de proveedor): el request lleva DOS representaciones —
la ``specification`` ESTRUCTURADA (para proveedores que acepten parámetros) y el
``prompt``/``negative_prompt`` de TEXTO (universal, válido para cualquier
proveedor: Leonardo, Flux, Ideogram, SDXL, Midjourney, Runway, OpenAI…).

Todo dataclass puro, serializable a JSON. Determinista.
"""

from dataclasses import dataclass, field


@dataclass
class VisualContext:
    """Contexto visual de un plano (lo que VAI necesita además del Shot).

    Se deriva de la escena + estilo + tendencias (p.ej. del RDA), pero son
    cadenas planas: VAI NO depende de RDA ni de VIS, solo de estos hints.
    """

    subject: str
    style: str = "documentary"          # documentary | cinematic | investigative | nature | ...
    color_temperature: str = "neutral"  # warm | cool | neutral
    saturation: str = "moderate"        # vivid | moderate | muted
    lighting_key: str = "balanced"      # low-key | balanced | high-key
    realism_level: str = "high"         # standard | high | ultra
    mood: str = ""                      # libre (p.ej. "ominous", "hopeful")


@dataclass
class VisualSpecification:
    """Especificación fotográfica estructurada (salida de los motores)."""

    shot_id: str
    scene_id: str
    media_type: str
    subject: str
    style: str
    composition: list[str] = field(default_factory=list)
    camera_language: list[str] = field(default_factory=list)
    lens: list[str] = field(default_factory=list)
    lighting: list[str] = field(default_factory=list)
    atmosphere: list[str] = field(default_factory=list)
    color_grade: list[str] = field(default_factory=list)
    realism: list[str] = field(default_factory=list)
    quality: list[str] = field(default_factory=list)
    negatives: list[str] = field(default_factory=list)


@dataclass
class ShotExecutionRequest:
    """Contrato con el MGL (compatible con ``MGL.generate_for_shot``).

    ``prompt``/``negative_prompt`` son universales; ``specification`` permite a
    proveedores futuros usar parámetros estructurados sin re-parsear texto.
    """

    shot_id: str
    scene_id: str
    media_type: str
    prompt: str
    negative_prompt: str
    reuse_key: str = ""
    variation_seed: int = 0
    motion: dict = field(default_factory=dict)
    # Representativos (compatibilidad/reporte):
    lens: str = ""
    angle: str = ""
    composition: str = ""
    specification: VisualSpecification | None = None
