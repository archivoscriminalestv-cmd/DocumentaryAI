"""Modelos del Dashboard de aprendizaje (DLM)."""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.dlm import SCHEMA_VERSION


class HealthStatus:
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# Orden de etapas observables públicamente (las únicas señales reales del pipeline).
STAGE_ORDER = ("downloading", "analyzing", "learning", "storing")

# Motores del dashboard mapeados a la etapa pública que los ejercita (granularidad de
# etapa: los eventos son por etapa, no por motor). El YIE corre en la fase de descarga.
ENGINES = (
    ("Downloader", "downloading"),
    ("YouTube Intelligence", "downloading"),
    ("SEO", "downloading"),
    ("Thumbnail", "downloading"),
    ("Competitive Intelligence", "downloading"),
    ("Scene Detection", "analyzing"),
    ("Visual Analysis", "analyzing"),
    ("Motion Analysis", "analyzing"),
    ("Audio Analysis", "analyzing"),
    ("Narration", "analyzing"),
    ("Embeddings", "learning"),
    ("Knowledge Store", "storing"),
    ("Knowledge Index", "storing"),
)


@dataclass
class EngineHealth:
    name: str
    stage: str
    status: str = HealthStatus.WAITING

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StageState:
    stage: str
    status: str = HealthStatus.WAITING


@dataclass
class CurrentDocument:
    doc_ref: str = ""
    doc_id: str = ""
    position: int = 0
    total: int = 0
    stage: str = ""
    shot_index: int = 0
    shot_total: int = 0
    scene_total: int = 0
    item_percent: float = 0.0
    # Estadísticas del vídeo (de knowledge/<id>/statistics.json al terminar; "—" antes).
    avg_shot_length: float = 0.0
    cuts_per_minute: float = 0.0
    dominant_movement: str = "—"
    dominant_color_temperature: str = "—"
    avg_brightness: float = 0.0
    avg_contrast: float = 0.0
    audio_seconds: float = 0.0
    narration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CorpusStatistics:
    documentaries: int = 0
    hours: float = 0.0
    shots: int = 0
    scenes: int = 0
    channels: int = 0
    videos: int = 0
    knowledge_bytes: int = 0
    views: int = 0
    likes: int = 0
    comments: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GlobalStatistics:
    elapsed: float = 0.0
    eta_queue: float = 0.0
    eta_video: float = 0.0
    global_percent: float = 0.0
    videos_per_hour: float = 0.0
    video_hours_per_hour: float = 0.0
    shots_per_minute: float = 0.0
    scenes_per_minute: float = 0.0
    knowledge_mb_per_hour: float = 0.0
    completed: int = 0
    failed: int = 0
    skipped: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DashboardState:
    schema_version: str = SCHEMA_VERSION
    finished: bool = False
    queue_total: int = 0
    queue_position: int = 0
    corpus: CorpusStatistics = field(default_factory=CorpusStatistics)
    current: CurrentDocument = field(default_factory=CurrentDocument)
    globals: GlobalStatistics = field(default_factory=GlobalStatistics)
    engines: list[EngineHealth] = field(default_factory=list)
    last_events: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data
