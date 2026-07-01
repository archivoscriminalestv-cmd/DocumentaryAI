"""Pipeline de aprendizaje automático por lotes (DLE-002).

Convierte el DLE en un sistema que aprende de cientos/miles de documentales sin
intervención humana: cola persistente + gestor + jobs desacoplados. Mantiene los
principios del DLE (observe-only, determinista, provider-agnóstico, aditivo) y NO
modifica el pipeline de generación.
"""

QUEUE_SCHEMA_VERSION = "1.0"

from app.dle.queue.index import KnowledgeIndex
from app.dle.queue.manager import LearningQueueManager
from app.dle.queue.models import QueueItem, QueueStatus
from app.dle.queue.store import QueueStore

__all__ = [
    "QUEUE_SCHEMA_VERSION",
    "LearningQueueManager",
    "QueueStore",
    "KnowledgeIndex",
    "QueueItem",
    "QueueStatus",
]
