"""Evidence Investigation Planner (EAE-002).

Antes de descargar nada, DocumentaryAI construye un PLAN DE INVESTIGACIÓN documental:
"¿qué material necesito realmente para producir este documental?". El planner se comporta
como un investigador profesional: planifica antes de ejecutar, minimiza descargas y exige
que cada recurso responda a una necesidad concreta.

Determinista, serializable, versionado. NO consulta Internet, NO descarga, NO usa IA.
Solo construye el plan (output/eae/plans/).
"""

PLANNER_SCHEMA_VERSION = "0.1"

from app.eae.planner.models import (
    AcquisitionTask,
    CaseProfile,
    CoverageRequirement,
    EvidenceCategory,
    EvidenceManifest,
    EvidenceNeed,
    EvidencePriority,
    ExpectedEvidence,
    InvestigationPlan,
    InvestigationTarget,
    ResearchStage,
    SearchTask,
)
from app.eae.planner.planner import EvidenceInvestigationPlanner

__all__ = [
    "PLANNER_SCHEMA_VERSION",
    "EvidenceInvestigationPlanner",
    "InvestigationPlan",
    "EvidenceManifest",
    "InvestigationTarget",
    "EvidenceNeed",
    "EvidencePriority",
    "EvidenceCategory",
    "ExpectedEvidence",
    "SearchTask",
    "AcquisitionTask",
    "CoverageRequirement",
    "ResearchStage",
    "CaseProfile",
]
