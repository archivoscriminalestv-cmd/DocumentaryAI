"""Orquestador del Evidence Correlation Engine (ECE).

Combina correlación (grafo + conflictos), análisis de cobertura y detección de candidatos
de recreación en un único ``CorrelationResult``. Solo análisis; determinista.
"""

from app.ece.correlator import EvidenceCorrelationEngine
from app.ece.coverage import analyze_coverage
from app.ece.models import CorrelationResult
from app.ece.recreation import detect_recreation_candidates


class CaseCorrelationEngine:
    def analyze(self, plan, discovery_plan) -> CorrelationResult:
        graph, conflicts = EvidenceCorrelationEngine().correlate(plan, discovery_plan)
        coverage = analyze_coverage(plan, discovery_plan)
        candidates = detect_recreation_candidates(plan, discovery_plan)
        return CorrelationResult(
            case_id=plan.case_id, graph=graph, coverage=coverage,
            conflicts=conflicts, recreation_candidates=candidates)
