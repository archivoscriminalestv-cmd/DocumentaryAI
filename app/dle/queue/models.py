"""Modelos de la cola de aprendizaje (DLE-002)."""

from dataclasses import asdict, dataclass, field
from typing import Any


class QueueStatus:
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    ANALYZING = "ANALYZING"
    LEARNING = "LEARNING"
    STORING = "STORING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

    TERMINAL = {FINISHED, SKIPPED}
    IN_FLIGHT = {DOWNLOADING, ANALYZING, LEARNING, STORING}
    ALL = {PENDING, DOWNLOADING, ANALYZING, LEARNING, STORING, FINISHED, FAILED, SKIPPED}


# Etapa del DLE (on_stage) -> estado de la cola.
STAGE_TO_STATUS = {
    "downloading": QueueStatus.DOWNLOADING,
    "analyzing": QueueStatus.ANALYZING,
    "learning": QueueStatus.LEARNING,
    "storing": QueueStatus.STORING,
}


@dataclass
class QueueItem:
    url: str                       # URL canónica o ruta local
    order: int
    kind: str = "unknown"          # youtube | local | unknown
    video_id: str = ""             # id derivado de la fuente (sin descargar, si se puede)
    documentary_id: str = ""       # id en knowledge/ (cuando se conoce)
    status: str = QueueStatus.PENDING
    attempts: int = 0
    error: str = ""
    schema_version: str = ""       # versión DLE con la que se aprendió

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QueueItem":
        known = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in known})
