"""Modelos del Documentary Learning Engine (DLE).

Conocimiento cinematográfico estructurado, serializable y versionado. Los campos que
no se pueden determinar con confianza valen ``UNKNOWN`` (nunca se inventan). No hay
marcas de tiempo dentro del conocimiento (reproducibilidad); la traza temporal vive en
el manifest/report.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.dle import SCHEMA_VERSION, UNKNOWN

# Taxonomía narrativa canónica (para el futuro; hoy se etiqueta UNKNOWN si no hay confianza).
NARRATIVE_CATEGORIES = (
    "HOOK", "INTRODUCTION", "PRESENTATION", "CONFLICT", "INVESTIGATION",
    "REVELATIONS", "RESOLUTION", "CONCLUSION", "UNKNOWN",
)


@dataclass
class AnalysisError:
    stage: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Metadata:
    source_type: str = UNKNOWN        # youtube | local
    source_ref: str = ""              # url o ruta (no se almacena contenido protegido)
    video_id: str = ""
    duration: float = 0.0
    width: int = 0
    height: int = 0
    fps: float = 0.0
    has_audio: bool = False
    container: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    provider: str = "none"
    language: str = UNKNOWN
    available: bool = False
    segments: list[TranscriptSegment] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider, "language": self.language, "available": self.available,
            "segments": [asdict(s) for s in self.segments],
        }


@dataclass
class ShotAnalysis:
    index: int
    scene_index: int
    start: float
    end: float
    duration: float
    # visual (determinista cuando es posible; UNKNOWN si no)
    shot_size: str = UNKNOWN
    composition: str = UNKNOWN
    movement: str = UNKNOWN
    motion_magnitude: float = 0.0
    lighting: str = UNKNOWN
    color_temperature: str = UNKNOWN
    contrast: float = 0.0
    brightness: float = 0.0
    dominant_color: str = UNKNOWN
    face_present: str = UNKNOWN         # requiere detector -> UNKNOWN
    num_people: str = UNKNOWN
    interior_exterior: str = UNKNOWN
    day_night: str = UNKNOWN
    # audio
    audio_present: str = UNKNOWN        # bool-as-str o UNKNOWN
    narration_present: str = UNKNOWN
    music_present: str = UNKNOWN
    effects_present: str = UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SceneSegment:
    index: int
    start: float
    end: float
    duration: float
    shot_indices: list[int] = field(default_factory=list)
    dominant_color: str = UNKNOWN
    color_temperature: str = UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NarrativeBlock:
    index: int
    start: float
    end: float
    category: str = UNKNOWN
    confidence: float = 0.0
    label: str = ""                    # etiqueta estructural (p.ej. "segment 1/3")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Statistics:
    shot_count: int = 0
    scene_count: int = 0
    cut_count: int = 0
    average_shot_length: float = 0.0
    median_shot_length: float = 0.0
    min_shot_length: float = 0.0
    max_shot_length: float = 0.0
    cuts_per_minute: float = 0.0
    pacing_tier: str = UNKNOWN
    shot_size_distribution: dict = field(default_factory=dict)
    movement_distribution: dict = field(default_factory=dict)
    lighting_distribution: dict = field(default_factory=dict)
    color_temperature_distribution: dict = field(default_factory=dict)
    dominant_color_distribution: dict = field(default_factory=dict)
    close_up_frequency: float = 0.0
    time_with_audio: float = 0.0
    time_with_narration: float = 0.0
    time_with_music: float = 0.0
    embedding: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentaryKnowledge:
    documentary_id: str
    schema_version: str = SCHEMA_VERSION
    metadata: Metadata = field(default_factory=Metadata)
    scenes: list[SceneSegment] = field(default_factory=list)
    shots: list[ShotAnalysis] = field(default_factory=list)
    narrative_blocks: list[NarrativeBlock] = field(default_factory=list)
    statistics: Statistics = field(default_factory=Statistics)
    transcript: Transcript = field(default_factory=Transcript)
    errors: list[AnalysisError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "documentary_id": self.documentary_id,
            "metadata": self.metadata.to_dict(),
            "scenes": [s.to_dict() for s in self.scenes],
            "shots": [s.to_dict() for s in self.shots],
            "narrative_blocks": [b.to_dict() for b in self.narrative_blocks],
            "statistics": self.statistics.to_dict(),
            "transcript": self.transcript.to_dict(),
            "errors": [e.to_dict() for e in self.errors],
        }
