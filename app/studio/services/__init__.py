"""Servicios de DocumentaryAI Studio (DAS-001) — la capa de orquestación, libre de Qt.

La UI solo habla con estos servicios; los servicios llaman a las CLIs/motores existentes. Aquí
NO vive lógica de negocio de aprendizaje/generación: solo se compone lo que ya existe.
"""

from app.studio.services.learning_service import LearningService
from app.studio.services.log_tail import LogTail
from app.studio.services.models import (
    LearningState,
    QueueAddResult,
    StartResult,
    StatusSnapshot,
)
from app.studio.services.status_service import StatusService

__all__ = [
    "LearningService",
    "StatusService",
    "LogTail",
    "QueueAddResult",
    "LearningState",
    "StartResult",
    "StatusSnapshot",
]
