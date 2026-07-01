"""Modelos del Reference Documentary Analyzer (RDA).

Solo GRAMÁTICA audiovisual (estadística visual), NUNCA contenido narrativo: no
hay transcripción, ni reconocimiento de objetos, ni descripción del relato. Las
métricas son agregados numéricos por fotograma/plano que describen CÓMO está
construido el vídeo (montaje, ritmo, luz, color, movimiento).

Todos los modelos son dataclasses puras, serializables a JSON.
"""

from dataclasses import dataclass, field


@dataclass
class FrameFeatures:
    """Rasgos numéricos de un fotograma muestreado (sin contenido semántico)."""

    t: float                       # segundos desde el inicio
    brightness: float              # luma media 0..255
    contrast: float                # desviación típica de luma
    warmth: float                  # mean(R) - mean(B), -255..255
    colorfulness: float            # Hasler-Süsstrunk (saturación percibida)
    signature: tuple[float, ...]   # mini-huella gris 8x8 (para diferencia de planos)


@dataclass
class ShotProfile:
    """Agregado por plano (entre dos cortes). Sin semántica del contenido."""

    index: int
    start: float
    end: float
    duration: float
    brightness: float
    contrast: float
    warmth: float
    colorfulness: float
    motion: float                  # diferencia media intra-plano (0..1)


@dataclass
class CinematicProfile:
    """Conocimiento reutilizable: la gramática audiovisual de una referencia.

    Alimenta ARCH-VIS-000 (Cinematic Language Spec) y el futuro VIS. NO contiene
    ni un fotograma ni texto del vídeo original: solo estadísticas y su mapeo al
    vocabulario cinematográfico.
    """

    reference: str
    source_type: str               # "local" | "youtube" | ...
    width: int
    height: int
    aspect_ratio: str
    fps: float
    duration: float
    sample_fps: float

    # Montaje / ritmo
    shot_count: int
    avg_shot_length: float
    median_shot_length: float
    min_shot_length: float
    max_shot_length: float
    shot_length_stddev: float
    cuts_per_minute: float
    pacing_tier: str               # very_fast | fast | moderate | slow
    shot_length_variety: str       # metronomic | moderate | varied

    # Iluminación
    brightness_mean: float
    contrast_mean: float
    lighting_tendency: str         # p.ej. "low-key high-contrast"

    # Color / grade
    warmth_mean: float
    colorfulness_mean: float
    color_temperature: str         # warm | cool | neutral
    saturation_tendency: str       # vivid | moderate | muted

    # Cámara / movimiento
    motion_mean: float
    movement_tendency: str         # dynamic | moderate | mostly_static

    grammar_notes: list[str] = field(default_factory=list)
    spec_alignment: dict = field(default_factory=dict)
    shots: list[ShotProfile] = field(default_factory=list)
