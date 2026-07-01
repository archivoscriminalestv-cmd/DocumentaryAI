"""Analizadores por defecto (ESQUELETO determinista, sin lógica compleja todavía).

Son implementaciones mínimas de ``GapAnalyzer`` y ``Recommender`` con puntos de
extensión claros. La comparación real corpus↔pipeline y la priorización por impacto se
desarrollarán en sprints posteriores; aquí solo se fija la estructura.
"""

from app.advisor import UNKNOWN
from app.advisor.models import (
    CorpusSnapshot,
    Dimension,
    Effort,
    GapFinding,
    Impact,
    Recommendation,
    Severity,
)


class BaselineGapAnalyzer:
    """Esqueleto: marca como gap toda capacidad que el pipeline NO soporta hoy.

    No infiere nada del corpus (su cobertura es UNKNOWN en este sprint): solo enumera
    capacidades ausentes en nuestro pipeline como huecos a estudiar más adelante."""

    def analyze(self, snapshot: CorpusSnapshot) -> list[GapFinding]:
        gaps: list[GapFinding] = []
        if not snapshot.available:
            gaps.append(GapFinding(
                id="corpus.empty", title="Aún no hay corpus legible",
                dimension=Dimension.CAPABILITY, severity=Severity.INFO,
                rationale="No se encontraron artefactos públicos en knowledge/."))
            return gaps

        for cap in snapshot.capabilities:
            if cap.pipeline_supported == "no":
                gaps.append(GapFinding(
                    id=f"capability.{cap.capability}",
                    title=f"El pipeline no produce '{cap.capability}'",
                    dimension=Dimension.CAPABILITY, severity=Severity.MINOR,
                    corpus_value=UNKNOWN, pipeline_value="no",
                    rationale="Capacidad ausente en la generación; "
                              "su cobertura en el corpus está pendiente de señal pública."))
        return gaps


class BaselineRecommender:
    """Esqueleto: una recomendación por gap, con prioridad determinista por orden."""

    def recommend(self, snapshot: CorpusSnapshot, gaps: list[GapFinding]) -> list[Recommendation]:
        recs: list[Recommendation] = []
        for i, gap in enumerate(gaps):
            if gap.dimension != Dimension.CAPABILITY or gap.id == "corpus.empty":
                continue
            cap = gap.id.split(".", 1)[-1]
            recs.append(Recommendation(
                id=f"add.{cap}", title=f"Desarrollar capacidad: {cap}",
                impact=Impact.MEDIUM, effort=Effort.MEDIUM,
                priority=round(1.0 - i * 0.01, 4),     # determinista; afinará el futuro
                rationale="Punto de extensión: medir cobertura real en el corpus y "
                          "estimar impacto antes de priorizar.",
                addresses=[gap.id]))
        return recs
