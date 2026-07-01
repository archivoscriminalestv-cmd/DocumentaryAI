"""Roadmap Generator (DCA-003) — prioriza mejoras por reglas objetivas.

Combina los huecos de GENERACIÓN (con su dueño) con los huecos ARQUITECTÓNICOS del DCA
(motores no integrados / conocimiento no aprovechado) y ordena por señales objetivas: número
de consumidores afectados (del grafo de capacidades) y magnitud del hueco. Sin IA, sin
intuición, sin scoring subjetivo.
"""

from app.dca.analyzer import consumers_count, detect_gaps
from app.dca.evaluation.models import Gap, ImprovementItem

# Capacidad arquitectónica -> subsistema dueño (para sumar consumidores afectados).
_ARCH_OWNER = {"visual_attributes": "VUE", "cinematographic_knowledge": "DLE",
               "style_patterns": "DKS", "youtube_intelligence": "YIE",
               "production_gaps": "Advisor"}


def _arch_gaps_to_targets(subsystems) -> dict[str, dict]:
    """{subsistema: {reason, consumers}} a partir de los huecos arquitectónicos del DCA."""
    out: dict[str, dict] = {}
    for g in detect_gaps(subsystems):
        target = None
        if g.kind == "not_integrated" and g.related:
            target = g.related[0]
        elif g.kind == "knowledge_unused":
            cap = g.id.split(":")[-1]
            target = _ARCH_OWNER.get(cap)
        if not target:
            continue
        consumers = consumers_count(subsystems, target)
        cur = out.setdefault(target, {"reasons": [], "consumers": consumers})
        cur["consumers"] = max(cur["consumers"], consumers)
        cur["reasons"].append(g.kind)
    return out


def build_roadmap(subsystems, gaps: list[Gap]) -> list[ImprovementItem]:
    # agrega por subsistema dueño
    targets: dict[str, dict] = {}
    for g in gaps:
        if g.owner == "UNKNOWN":
            continue
        t = targets.setdefault(g.owner, {"magnitude": 0.0, "reasons": [], "consumers": 0})
        t["magnitude"] = max(t["magnitude"], g.magnitude)
        t["reasons"].append(g.description)
        t["consumers"] = consumers_count(subsystems, g.owner)

    for target, info in _arch_gaps_to_targets(subsystems).items():
        t = targets.setdefault(target, {"magnitude": 0.0, "reasons": [], "consumers": 0})
        t["consumers"] = max(t["consumers"], info["consumers"])
        t["reasons"].extend(info["reasons"])

    items: list[ImprovementItem] = []
    for target, info in targets.items():
        items.append(ImprovementItem(
            id=f"improve:{target}", target=target,
            rationale="; ".join(info["reasons"][:4]),
            metrics={"consumers_affected": info["consumers"],
                     "max_gap_magnitude": round(info["magnitude"], 4),
                     "reason_count": len(info["reasons"])}))

    # prioridad objetiva: más consumidores afectados, luego mayor magnitud, luego nombre
    items.sort(key=lambda i: (-i.metrics["consumers_affected"],
                              -i.metrics["max_gap_magnitude"], i.target))
    for rank, item in enumerate(items, start=1):
        item.priority_rank = rank
    return items
