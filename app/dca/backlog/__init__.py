"""Architectural Backlog (DCA-004) — `app/dca/backlog/`.

La MEMORIA ESTRATÉGICA permanente de DocumentaryAI. Registra mejoras, ideas, hipótesis y deuda
arquitectónica detectadas durante el desarrollo, y responde a la pregunta oficial:

    "¿Qué sabemos hoy que debemos mejorar en DocumentaryAI?"

El documento humano vive en ``docs/roadmap/ARCHITECTURAL-BACKLOG.md``. Este paquete lo carga en
modelos internos, lo valida y PROPONE cambios tras cada sprint. Es una capacidad NUEVA del DCA,
aditiva y por composición: NO modifica ningún motor ni ``analyzer.py``. El backlog nunca se
reescribe automáticamente — solo el desarrollador lo edita tras aprobar la propuesta.
"""

BACKLOG_SCHEMA_VERSION = "0.1"
BACKLOG_VERSION = "DCA-004"

from app.dca.backlog.models import (
    ArchitecturalBacklog,
    BacklogEntry,
    BacklogProposal,
    EntryStatus,
    HypothesisStatus,
    Priority,
    Section,
    ValidationIssue,
)
from app.dca.backlog.orchestrator import DEFAULT_BACKLOG_PATH, BacklogOrchestrator

__all__ = [
    "BACKLOG_SCHEMA_VERSION",
    "BACKLOG_VERSION",
    "DEFAULT_BACKLOG_PATH",
    "BacklogOrchestrator",
    "ArchitecturalBacklog",
    "BacklogEntry",
    "BacklogProposal",
    "EntryStatus",
    "Priority",
    "HypothesisStatus",
    "Section",
    "ValidationIssue",
]
