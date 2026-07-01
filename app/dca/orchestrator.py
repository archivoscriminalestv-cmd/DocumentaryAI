"""DocumentaryChiefArchitect (DCA) — coordinación de solo lectura.

Compone el modelo arquitectónico completo a partir del registry y la documentación pública.
No ejecuta motores, no modifica nada, no usa IA. Determinista.
"""

from app.dca import DCA_VERSION, SCHEMA_VERSION
from app.dca.analyzer import detect_bottlenecks, detect_gaps
from app.dca.architecture_reader import ArchitectureReader
from app.dca.capability_graph import build_capabilities, capability_edges
from app.dca.dependency_graph import analyze_dependencies, direct_dependencies
from app.dca.models import (
    ArchitectureSnapshot,
    Goal,
    Status,
    SystemArchitecture,
)
from app.dca.registry import build_domains, build_pipelines, build_subsystems
from app.dca.roadmap import build_roadmap, recommendations


def _gk_field(gk, key, default=None):
    if isinstance(gk, dict):
        return gk.get(key, default)
    return getattr(gk, key, default)


class DocumentaryChiefArchitect:
    def __init__(self, root: str = ".", reader: ArchitectureReader | None = None) -> None:
        self._subsystems = build_subsystems()
        self._reader = reader or ArchitectureReader(root)

    # ------------------------------------------------------------------ vistas
    def capabilities(self):
        return build_capabilities(self._subsystems)

    def dependencies(self) -> dict:
        return analyze_dependencies(self._subsystems)

    def architecture(self) -> SystemArchitecture:
        caps = self.capabilities()
        gaps = detect_gaps(self._subsystems)
        return SystemArchitecture(
            domains=build_domains(self._subsystems),
            subsystems=self._subsystems,
            capabilities=caps,
            dependencies=direct_dependencies(self._subsystems),
            pipelines=build_pipelines(),
            goals=self._goals(gaps),
            coverage=self._coverage(),
            docs_index=self._reader.docs_index(),
        )

    def analyze(self) -> dict:
        gaps = detect_gaps(self._subsystems)
        deps = analyze_dependencies(self._subsystems)
        return {
            "engines": [{"name": s.name, "domain": s.domain, "status": s.status,
                         "responsibility": s.responsibility} for s in self._subsystems],
            "gaps": [g.to_dict() for g in gaps],
            "bottlenecks": [b.to_dict() for b in detect_bottlenecks(self._subsystems)],
            "duplicates": [g.to_dict() for g in gaps if g.kind == "duplicate"],
            "unused": [g.related[0] for g in gaps if g.kind in ("unused", "not_integrated")],
            "isolated": deps["isolated"],
            "cycles": deps["cycles"],
            "knowledge_unused": [g.to_dict() for g in gaps if g.kind == "knowledge_unused"],
        }

    def roadmap(self):
        return build_roadmap(self._subsystems, detect_gaps(self._subsystems))

    def recommend(self):
        return recommendations(self.roadmap())

    # ------------------------------------------------------------------ DCA-003
    def evaluate(self, *, production_context, visual_plans, ece_coverage=None,
                 recreation_candidates=None, composer_used=None, recreation_used=None,
                 generation_knowledge=None):
        """Autoevaluación (DCA-003): mide la distancia generación↔corpus, deriva huecos con
        dueño, construye el roadmap y los indicadores de salud. Solo lectura, determinista."""
        from app.dca.analyzer import detect_gaps
        from app.dca.evaluation.comparator import build_comparisons
        from app.dca.evaluation.gap_analyzer import analyze_gaps
        from app.dca.evaluation.models import EvaluationResult, MetricStatus, SystemHealth
        from app.dca.evaluation.roadmap_generator import build_roadmap

        comparisons = build_comparisons(
            production_context, visual_plans, ece_coverage=ece_coverage,
            recreation_candidates=recreation_candidates, composer_used=composer_used,
            recreation_used=recreation_used)
        gaps = analyze_gaps(comparisons)
        roadmap = build_roadmap(self._subsystems, gaps)
        health = self._health(comparisons, generation_knowledge)
        summary = {
            "comparisons": len(comparisons),
            "aligned": sum(1 for c in comparisons if c.status == MetricStatus.ALIGNED),
            "differs": sum(1 for c in comparisons if c.status == MetricStatus.DIFFERS),
            "unknown": sum(1 for c in comparisons if c.status == MetricStatus.UNKNOWN),
            "gaps": len(gaps),
            "next_improvement": roadmap[0].target if roadmap else "UNKNOWN",
        }
        return EvaluationResult(comparisons=comparisons, gaps=gaps, roadmap=roadmap,
                               health=health, summary=summary)

    def _health(self, comparisons, generation_knowledge):
        from app.dca.analyzer import detect_gaps
        from app.dca.evaluation.models import MetricStatus, SystemHealth

        measured = [c for c in comparisons if c.status != MetricStatus.UNKNOWN]
        aligned = [c for c in measured if c.status == MetricStatus.ALIGNED]
        cov = self._coverage()
        gaps = detect_gaps(self._subsystems)
        missing = sum(1 for g in gaps if g.kind in ("not_integrated", "missing_capability"))

        health = SystemHealth(
            generation_coverage=round(len(measured) / len(comparisons), 4) if comparisons else "UNKNOWN",
            corpus_alignment=round(len(aligned) / len(measured), 4) if measured else "UNKNOWN",
            integrated_capabilities=cov.get("implemented"),
            missing_capabilities=missing,
        )
        ev = next((c for c in comparisons if c.dimension == "evidence_coverage"), None)
        if ev is not None and ev.deviation is not None:
            health.evidence_coverage = round(1 - ev.deviation, 4)
        if generation_knowledge is not None:
            s = _gk_field(generation_knowledge, "summary", {})
            if isinstance(s, dict) and "known_ratio" in s:
                health.knowledge_utilization = s.get("known_ratio")
                health.unknown_decisions = s.get("unknown")
        return health

    # ------------------------------------------------------------------ DCA-004
    def _backlog_orchestrator(self, path: str | None = None):
        """BacklogOrchestrator perezoso y cacheado (por composición; no toca analyzer.py)."""
        from app.dca.backlog.orchestrator import DEFAULT_BACKLOG_PATH, BacklogOrchestrator
        target = path or DEFAULT_BACKLOG_PATH
        cached = getattr(self, "_backlog_cache", None)
        if cached is None or cached[0] != target:
            self._backlog_cache = (target, BacklogOrchestrator(path=target))
        return self._backlog_cache[1]

    def backlog(self, path: str | None = None):
        """Carga el Architectural Backlog (DCA-004) en modelos internos. Solo lectura."""
        return self._backlog_orchestrator(path).load(refresh=True)

    def validate_backlog(self, path: str | None = None):
        """Valida la coherencia del backlog (estados/prioridades/hipótesis/ids/related)."""
        return self._backlog_orchestrator(path).validate()

    def review_backlog(self, sprint_review: dict, path: str | None = None):
        """Tras un sprint, PROPONE cambios al backlog (no reescribe el documento humano).

        sprint_review: {sprint, resolved[], status_changes[], new_ideas[], related_to_add[], notes[]}.
        Devuelve un BacklogProposal que el desarrollador aprueba e integra a mano."""
        return self._backlog_orchestrator(path).review(sprint_review)

    def backlog_summary(self, path: str | None = None) -> dict:
        return self._backlog_orchestrator(path).summary()

    def snapshot(self) -> ArchitectureSnapshot:
        arch = self.architecture()
        deps = analyze_dependencies(self._subsystems)
        gaps = detect_gaps(self._subsystems)
        totals = {
            "subsystems": len(self._subsystems),
            "domains": len(arch.domains),
            "capabilities": len(arch.capabilities),
            "dependencies": len(arch.dependencies),
            "gaps": len(gaps),
            "cycles": len(deps["cycles"]),
            "isolated": len(deps["isolated"]),
            **arch.coverage,
        }
        return ArchitectureSnapshot(architecture=arch, totals=totals)

    # ------------------------------------------------------------------ helpers
    def _coverage(self) -> dict:
        by_status: dict[str, int] = {}
        for s in self._subsystems:
            by_status[s.status] = by_status.get(s.status, 0) + 1
        total = len(self._subsystems)
        implemented = by_status.get(Status.IMPLEMENTED, 0)
        return {
            "total_subsystems": total,
            "implemented": implemented,
            "implemented_percent": round(implemented / total, 4) if total else 0.0,
            "by_status": {k: by_status[k] for k in sorted(by_status)},
        }

    def _goals(self, gaps) -> list[Goal]:
        kinds = {g.kind for g in gaps}
        def _state(bad: bool) -> str:
            return "partial" if bad else "complete"
        return [
            Goal("goal:knowledge_driven_generation", "La generación aprovecha el conocimiento aprendido",
                 _state("knowledge_unused" in kinds),
                 "VUE/DKS/YIE producen conocimiento aún no consumido por la generación."),
            Goal("goal:full_integration", "Todos los motores integrados en el pipeline",
                 _state("not_integrated" in kinds), "Hay motores implementados sin integrar."),
            Goal("goal:no_orphans", "Sin motores aislados ni capacidades huérfanas",
                 _state(bool({"unused", "missing_capability"} & kinds)),
                 "Existen capacidades sin productor o motores sin consumidores."),
        ]
