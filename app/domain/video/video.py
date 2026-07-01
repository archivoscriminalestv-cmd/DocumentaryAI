"""Video — documental final ensamblado a partir de imágenes y locución.

Última capa de producción del MVP. ``VideoScene`` es la especificación de una
escena para el compositor (imagen + audio opcional + duración). ``Documentary``
es el artefacto final con la ruta del vídeo generado.
"""

from dataclasses import dataclass


@dataclass
class VideoScene:
    image_path: str
    audio_path: str | None  # WAV real, o None para escena en silencio
    duration: float  # segundos


@dataclass
class Documentary:
    id: str
    narrative_id: str
    video_path: str
    rendered: bool
