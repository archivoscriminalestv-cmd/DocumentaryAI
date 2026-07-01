"""Documentary Learning Monitor (DLM) — Sprint DLM-001.

Centro de control del aprendizaje: observa en TIEMPO REAL todo el proceso del DLE/Queue
consumiendo ÚNICAMENTE los eventos públicos (``ProgressEvent``) ya existentes y leyendo
los artefactos públicos de ``knowledge/``. 100% aditivo y por composición: NO modifica
DLE/Queue/YIE/DKS/VIS/VAI/VSC/VPL/Composer/FFmpeg ni inspecciona su estado interno.

Determinista: el mismo flujo de eventos + el mismo reloj inyectable producen el mismo
estado y el mismo render.
"""

SCHEMA_VERSION = "1.0"

from app.dlm.models import (
    CorpusStatistics,
    CurrentDocument,
    DashboardState,
    EngineHealth,
    GlobalStatistics,
    HealthStatus,
    StageState,
)
from app.dlm.monitor import DashboardMonitor

__all__ = [
    "SCHEMA_VERSION",
    "DashboardMonitor",
    "DashboardState",
    "StageState",
    "EngineHealth",
    "HealthStatus",
    "CurrentDocument",
    "CorpusStatistics",
    "GlobalStatistics",
]
