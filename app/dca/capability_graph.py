"""Grafo de capacidades (DCA): quién PRODUCE y quién CONSUME cada capacidad.

Determinista (ordenado). Derivado únicamente de los contratos del registry.
"""

from app.dca.models import Capability, Subsystem


def build_capabilities(subsystems: list[Subsystem]) -> list[Capability]:
    producers: dict[str, list[str]] = {}
    consumers: dict[str, list[str]] = {}
    for s in subsystems:
        for cap in s.produces:
            producers.setdefault(cap, []).append(s.name)
        for cap in s.consumes:
            consumers.setdefault(cap, []).append(s.name)
    names = sorted(set(producers) | set(consumers))
    return [Capability(name=c, producers=sorted(producers.get(c, [])),
                       consumers=sorted(consumers.get(c, []))) for c in names]


def capability_edges(capabilities: list[Capability]) -> list[dict]:
    """Aristas producer -> consumer por capacidad (para el grafo de flujo)."""
    edges = []
    for cap in capabilities:
        for producer in cap.producers:
            for consumer in cap.consumers:
                edges.append({"source": producer, "capability": cap.name, "target": consumer})
    edges.sort(key=lambda e: (e["source"], e["capability"], e["target"]))
    return edges
