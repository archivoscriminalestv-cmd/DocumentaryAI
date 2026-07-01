"""Roadmap determinista (DCA) — prioriza por reglas objetivas, sin IA ni scoring subjetivo.

Cada hueco/cuello de botella genera una mejora con señales objetivas (tipo, nº de
consumidores afectados, estado del motor). El orden se decide por reglas fijas, no por
puntuaciones inventadas.
"""

from app.dca.analyzer import consumers_count
from app.dca.models import Improvement, Recommendation, Roadmap, Status, Subsystem

# Prioridad por tipo de hueco (menor = antes). Objetivo, no subjetivo.
_KIND_PRIORITY = {"missing_capability": 0, "knowledge_unused": 1, "not_integrated": 2,
                  "unused": 3, "duplicate": 4}


def _status_rank(subsystems, name) -> int:
    s = next((x for x in subsystems if x.name == name), None)
    return Status.RANK.get(s.status, 9) if s else 9


def build_roadmap(subsystems: list[Subsystem], gaps) -> Roadmap:
    items: list[Improvement] = []
    for gap in gaps:
        target = gap.related[0] if gap.related else gap.id.split(":")[-1]
        consumers = (len(gap.related) if gap.kind in ("missing_capability", "knowledge_unused",
                                                      "duplicate")
                     else consumers_count(subsystems, target))
        items.append(Improvement(
            id=f"improve:{gap.id.split(':', 1)[-1]}", target=target,
            rationale=gap.description,
            metrics={"gap_kind": gap.kind, "consumers": consumers,
                     "status_rank": _status_rank(subsystems, target),
                     "kind_priority": _KIND_PRIORITY.get(gap.kind, 9)}))

    items.sort(key=lambda i: (i.metrics["kind_priority"], -i.metrics["consumers"],
                              i.metrics["status_rank"], i.id))
    for rank, item in enumerate(items, start=1):
        item.priority_rank = rank
    return Roadmap(items=items)


def recommendations(roadmap: Roadmap, limit: int = 10) -> list[Recommendation]:
    out = []
    for item in roadmap.items[:limit]:
        out.append(Recommendation(
            id=f"rec:{item.id.split(':', 1)[-1]}", title=f"Priorizar {item.target}",
            target=item.target, rationale=item.rationale, priority_rank=item.priority_rank))
    return out
