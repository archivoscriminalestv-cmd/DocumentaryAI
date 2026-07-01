"""Production Advisor (advisor) — Sprint ADV-001 (scaffold).

Subsistema completamente DESACOPLADO que, más adelante, analizará el conocimiento ya
aprendido (``knowledge/``) para responder preguntas estratégicas: qué le falta a
DocumentaryAI para alcanzar la calidad del corpus, qué diferencias hay con los
documentales de éxito, qué capacidades aportarían más impacto y qué desarrollar después.

NO genera documentales. NO modifica ningún otro subsistema. Solo CONSUME artefactos
PÚBLICOS de ``knowledge/`` (lectura defensiva, tolerante a escrituras concurrentes) y
escribe sus informes en ``output/advisor/`` (nunca en ``knowledge/``).

Este primer sprint aporta solo la arquitectura: modelos, interfaces públicas, lector,
orquestador y persistencia. La lógica de análisis (gaps/recomendaciones) queda como
esqueleto determinista con puntos de extensión claros (sin lógica compleja todavía).
"""

SCHEMA_VERSION = "0.1"
UNKNOWN = "UNKNOWN"

from app.advisor.interfaces import GapAnalyzer, KnowledgeSource, Recommender
from app.advisor.models import (
    AdvisorReport,
    CapabilityUsage,
    CorpusSnapshot,
    Dimension,
    Effort,
    GapFinding,
    Impact,
    Recommendation,
    Severity,
)
from app.advisor.orchestrator import ProductionAdvisor

__all__ = [
    "SCHEMA_VERSION",
    "UNKNOWN",
    "ProductionAdvisor",
    "KnowledgeSource",
    "GapAnalyzer",
    "Recommender",
    "CorpusSnapshot",
    "CapabilityUsage",
    "GapFinding",
    "Recommendation",
    "AdvisorReport",
    "Dimension",
    "Severity",
    "Impact",
    "Effort",
]
