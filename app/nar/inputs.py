"""Capa anticorrupción del NAR (NAR-001).

El NAR NO importa las clases internas de otros motores (EAE/ECE/KBG/PCX). Lee sus JSON ya
persistidos —o dicts equivalentes— y los traduce a un ``NarrativeContext`` limpio. Así el
cerebro narrativo queda desacoplado: si otro motor cambia su modelo, solo cambia este
traductor. Determinista, sin red, sin IA.
"""

import json
import os
from typing import Any

from app.nar.models import CoverageDimension, NarrativeContext, RecreationCandidate


def _load(path: str | None) -> Any:
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as h:
        return json.load(h)


class NarrativeInputs:
    """Construye un ``NarrativeContext`` a partir de las salidas de los motores previos."""

    @staticmethod
    def from_sources(
        profile: dict,
        coverage: dict | None = None,
        evidence_graph: dict | None = None,
        recreation_candidates: dict | None = None,
        conflicts: dict | None = None,
        timeline: dict | None = None,
        generation_knowledge: dict | None = None,
    ) -> NarrativeContext:
        present: list[str] = []
        missing: list[str] = []

        def track(name: str, value) -> None:
            (present if value else missing).append(name)

        track("profile", profile)
        track("coverage", coverage)
        track("evidence_graph", evidence_graph)
        track("recreation_candidates", recreation_candidates)
        track("conflicts", conflicts)
        track("timeline", timeline)
        track("generation_knowledge", generation_knowledge)

        ctx = NarrativeContext(
            case_id=str(profile.get("case_id") or profile.get("id") or "case"),
            title=str(profile.get("title", "")),
            genre=str(profile.get("genre", "generic") or "generic"),
            subject=str(profile.get("subject", "")),
            people=list(profile.get("people", []) or []),
            locations=list(profile.get("locations", []) or []),
            events=list(profile.get("events", []) or []),
            time_period=str(profile.get("time_period", "")),
            inputs_present=sorted(present),
            inputs_missing=sorted(missing),
        )

        # --- coverage (ECE) ---
        if coverage:
            for dim in coverage.get("dimensions", []) or []:
                cd = CoverageDimension(
                    name=str(dim.get("name", "")),
                    required=int(dim.get("required", 0) or 0),
                    discovered=int(dim.get("discovered", 0) or 0),
                    state=str(dim.get("state", "MISSING")),
                    evidence_ids=list(dim.get("evidence_ids", []) or []),
                    detail=dict(dim.get("detail", {}) or {}),
                )
                if cd.name:
                    ctx.coverage[cd.name] = cd

        # --- evidence graph (ECE) ---
        if evidence_graph:
            ctx.graph_nodes = list(evidence_graph.get("nodes", []) or [])
            ctx.graph_relations = list(evidence_graph.get("relations", []) or [])

        # --- conflicts: explícitos o derivados de relaciones CONTRADICTS ---
        if conflicts:
            ctx.conflicts = list(conflicts.get("conflicts", conflicts) or [])
        if not ctx.conflicts and ctx.graph_relations:
            ctx.conflicts = [r for r in ctx.graph_relations
                             if str(r.get("relation", "")).upper() == "CONTRADICTS"]

        # --- recreation candidates (ECE) ---
        if recreation_candidates:
            raw = recreation_candidates.get("recreation_candidates", recreation_candidates)
            for rc in raw or []:
                if not isinstance(rc, dict):
                    continue
                fb = dict(rc.get("factual_basis", {}) or {})
                # El ECE anida la categoría dentro de factual_basis; admitimos ambas ubicaciones.
                category = str(rc.get("category") or fb.get("category") or "")
                ctx.recreation_candidates.append(RecreationCandidate(
                    category=category,
                    existing_coverage=str(rc.get("existing_coverage", "MISSING")),
                    factual_basis=fb,
                    available_evidence=list(rc.get("available_evidence", []) or []),
                ))

        # --- timeline (ECE) ---
        if timeline:
            events = timeline.get("events", []) or []
            ctx.timeline_events = [e if isinstance(e, str) else str(e.get("name", e))
                                   for e in events]
            if not ctx.events:
                ctx.events = list(ctx.timeline_events)

        # --- generation knowledge (KBG): se guarda crudo por secciones ---
        if generation_knowledge:
            ctx.knowledge = dict(generation_knowledge.get("sections", {}) or {})

        return ctx

    @staticmethod
    def from_case_dir(profile: dict, case_dir: str,
                      generation_knowledge_path: str | None = None) -> NarrativeContext:
        """Conveniencia: carga los JSON estándar de ``output/projects/<case>/`` (+ KBG)."""
        def p(name: str) -> str:
            return os.path.join(case_dir, name)

        return NarrativeInputs.from_sources(
            profile=profile,
            coverage=_load(p("coverage_report.json")),
            evidence_graph=_load(p("evidence_graph.json")),
            recreation_candidates=_load(p("recreation_candidates.json")),
            conflicts=_load(p("conflicts.json")),
            timeline=_load(p("timeline.json")),
            generation_knowledge=_load(generation_knowledge_path),
        )
