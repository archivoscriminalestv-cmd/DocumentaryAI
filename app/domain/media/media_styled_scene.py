"""MediaStyledScene — capa de identidad audiovisual (Sprint C-09).

Objeto de dominio puro y aditivo: una ``DirectedScene`` enriquecida con metadatos
de MEDIA (voz, estilo visual, prompt de imagen, música, intro). NO modifica
``narration``/``title``/``fact_ids`` ni inventa hechos. Serializable a JSON con
``dataclasses.asdict`` (``intro`` es null o un objeto anidado).
"""

from dataclasses import dataclass, field


@dataclass
class VoiceProfile:
    language: str = "es"
    tone: str = "documentary"
    gender: str = "neutral"
    pace: str = "moderate"  # calm | moderate | intense
    emotion: str = "neutral-authoritative"
    accent: str = ""
    narration_style: str = "cinematic documentary narration"


@dataclass
class VisualStyle:
    style: str = "cinematic documentary"
    realism: str = "high"
    lighting: str = "natural cinematic"
    camera: str = "slow pans, zooms, archival feel"
    composition: str = "centered subject focus"
    color_palette: str = "muted"


@dataclass
class IntroInjection:
    type: str = "video"
    asset: str = "channel_intro.mp4"
    duration: float = 5.0
    transition: str = "fade_to_scene"


@dataclass
class MediaStyledScene:
    id: str
    title: str
    narration: str
    fact_ids: list[str] = field(default_factory=list)
    voice_profile: VoiceProfile = field(default_factory=VoiceProfile)
    visual_style: VisualStyle = field(default_factory=VisualStyle)
    image_prompt: str = ""
    music_style: str = ""
    intro: IntroInjection | None = None
