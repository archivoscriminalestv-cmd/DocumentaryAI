"""Infrastructure Protection & Backup Foundation (INF-001) — `app/infra/`.

Subsistema INDEPENDIENTE cuyo único objetivo es que DocumentaryAI sobreviva a un fallo de disco,
una reinstalación de Windows, un cambio de ordenador, una corrupción o un error humano.

NO genera contenido, NO modifica ningún motor, NO sube nada a Internet, NO usa Git ni conoce
GitHub. Solo PREPARA la infraestructura de protección: describe qué copiar, qué no copiar, qué
conocimiento existe, qué estado tiene el proyecto y si está listo para un backup. Solo lectura
del proyecto; escribe únicamente en ``output/system/`` (nunca en ``knowledge/``). Determinista.

Filosofía: el conocimiento es permanente; los binarios temporales (renders, workspaces,
descargas) son desechables y NUNCA se respaldan.
"""

INFRA_SCHEMA_VERSION = "0.1"
INFRA_VERSION = "INF-001"
UNKNOWN = "UNKNOWN"

from app.infra.models import (
    BackupEntry,
    BackupPlan,
    IntegrityIssue,
    IntegrityReport,
    KnowledgeSnapshot,
    ProjectManifest,
    ProjectSnapshot,
    RestorePlan,
)

__all__ = [
    "INFRA_SCHEMA_VERSION",
    "INFRA_VERSION",
    "UNKNOWN",
    "ProjectManifest",
    "KnowledgeSnapshot",
    "ProjectSnapshot",
    "BackupPlan",
    "BackupEntry",
    "IntegrityReport",
    "IntegrityIssue",
    "RestorePlan",
]
