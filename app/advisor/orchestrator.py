"""ProductionAdvisor — orquestador del Advisor (scaffold).

Compone lector + analizador + recomendador y produce un ``AdvisorReport``. Solo lee
artefactos públicos de knowledge/ (vía el lector) y, opcionalmente, escribe el informe
en output/advisor/. No modifica ningún otro subsistema.
"""

import os

from app.advisor.analysis import (
    CorpusGapAnalyzer,
    CorpusRecommender,
    analyze_completeness,
    build_capability_matrix,
    confidence_notes,
    find_discoveries,
    rank_gaps,
)
from app.advisor.knowledge_reader import KnowledgeReader
from app.advisor.models import AdvisorReport
from app.advisor.persistence import ReportWriter


class ProductionAdvisor:
    def __init__(self, *, source=None, analyzer=None, recommender=None, sink=None,
                 knowledge_root: str = "knowledge") -> None:
        self.knowledge_root = knowledge_root
        self.source = source or KnowledgeReader(knowledge_root)
        self.analyzer = analyzer or CorpusGapAnalyzer()
        self.recommender = recommender or CorpusRecommender()
        self.sink = sink   # opcional; None = no persistir

    def advise(self) -> AdvisorReport:
        snapshot = self.source.snapshot()
        matrix = build_capability_matrix(snapshot)
        gaps = rank_gaps(self._analyze(snapshot, matrix))
        recommendations = self.recommender.recommend(snapshot, gaps)
        completeness = analyze_completeness(snapshot)
        discoveries = find_discoveries(snapshot)
        roadmap = [r.title for r in recommendations]
        notes = [
            "ADV-002: comparación determinista corpus↔pipeline (sin IA, sin scoring subjetivo).",
            "Impacto = frecuencia observada; confianza = tamaño muestral. UNKNOWN si no hay evidencia.",
            "Solo lectura de knowledge/; informes en output/advisor/ (nunca en knowledge/).",
        ]
        return AdvisorReport(
            generated_from=self.knowledge_root, snapshot=snapshot, capability_matrix=matrix,
            gaps=gaps, recommendations=recommendations, completeness=completeness,
            discoveries=discoveries, roadmap=roadmap,
            confidence_notes=confidence_notes(snapshot), notes=notes)

    def _analyze(self, snapshot, matrix):
        # El analizador puede aceptar la matriz (ADV-002) o solo el snapshot (Protocol).
        try:
            return self.analyzer.analyze(snapshot, matrix)
        except TypeError:
            return self.analyzer.analyze(snapshot)

    def advise_and_write(self, out_dir: str | None = None):
        report = self.advise()
        sink = self.sink or ReportWriter(out_dir=out_dir or os.path.join("output", "advisor"))
        paths = sink.write(report)
        return report, paths
