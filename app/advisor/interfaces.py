"""Interfaces públicas del Production Advisor.

Permiten enchufar lectores/analizadores/recomendadores sin tocar el orquestador. En
este sprint hay implementaciones por defecto mínimas (esqueleto determinista).
"""

from typing import Protocol

from app.advisor.models import (
    AdvisorReport,
    CorpusSnapshot,
    GapFinding,
    Recommendation,
)


class KnowledgeSource(Protocol):
    """Lee artefactos PÚBLICOS de knowledge/ y produce un ``CorpusSnapshot``.

    Debe ser de SOLO LECTURA y tolerante a escrituras concurrentes (ficheros a medio
    escribir → se tratan como no disponibles; nunca lanza)."""

    def snapshot(self) -> CorpusSnapshot:
        ...


class GapAnalyzer(Protocol):
    """Compara el corpus con el pipeline propio y produce hallazgos (gaps)."""

    def analyze(self, snapshot: CorpusSnapshot) -> list[GapFinding]:
        ...


class Recommender(Protocol):
    """Convierte los gaps en recomendaciones priorizadas."""

    def recommend(self, snapshot: CorpusSnapshot, gaps: list[GapFinding]) -> list[Recommendation]:
        ...


class ReportSink(Protocol):
    """Persiste un ``AdvisorReport`` (fuera de knowledge/)."""

    def write(self, report: AdvisorReport) -> dict[str, str]:
        ...
