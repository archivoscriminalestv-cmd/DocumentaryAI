"""Reference Documentary Analyzer (RDA).

Motor que extrae la GRAMÁTICA audiovisual (montaje, ritmo, luz, color, movimiento)
de cualquier vídeo de referencia y la almacena como conocimiento reutilizable
(`CinematicProfile`) que alimenta ARCH-VIS-000 y el futuro VIS. Nunca extrae
contenido narrativo.
"""

from app.rda.analyzer import ReferenceDocumentaryAnalyzer
from app.rda.library import ReferenceLibrary
from app.rda.models import CinematicProfile, FrameFeatures, ShotProfile

__all__ = [
    "ReferenceDocumentaryAnalyzer",
    "ReferenceLibrary",
    "CinematicProfile",
    "FrameFeatures",
    "ShotProfile",
]
