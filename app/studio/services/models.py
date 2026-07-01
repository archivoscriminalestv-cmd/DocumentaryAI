"""Modelos de datos de los servicios de Studio (DAS-001). Sin Qt, sin lógica de motor."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class QueueAddResult:
    """Resultado de añadir un fichero de URLs a la cola (vía el flujo existente queue_add)."""

    source: str = ""
    found: int = 0
    added: int = 0
    duplicates: int = 0
    invalid: int = 0
    ok: bool = True
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearningState:
    """Estado del proceso de aprendizaje (learn_queue)."""

    running: bool = False
    pid: int = 0
    source: str = "none"            # studio | external | none
    started_at: float = 0.0
    runtime_seconds: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StartResult:
    started: bool = False
    already_running: bool = False
    state: LearningState = field(default_factory=LearningState)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.to_dict()
        return d


@dataclass
class StatusSnapshot:
    """Fotografía de estado para la UI. Consume datos ya existentes; nunca recalcula."""

    learning: bool = False
    learned: int = 0
    pending: int = 0
    failed: int = 0
    skipped: int = 0
    hours_learned: float = 0.0
    shots_analyzed: int = 0
    scenes: int = 0
    current_video: str = ""
    runtime_seconds: int = 0
    source: str = "none"

    @property
    def indicator_label(self) -> str:
        return "🟢 Modo Aprendizaje" if self.learning else "⚪ Inactivo"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["indicator_label"] = self.indicator_label
        return d
