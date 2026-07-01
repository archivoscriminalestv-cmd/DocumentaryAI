"""Grafo de dependencias entre subsistemas (DCA).

Detecta dependencias directas e indirectas (cierre transitivo), ciclos, componentes
aislados y motores sin dependientes. Determinista; derivado del registry.
"""

from app.dca.models import Dependency, Subsystem


def direct_dependencies(subsystems: list[Subsystem]) -> list[Dependency]:
    names = {s.name for s in subsystems}
    edges = []
    for s in subsystems:
        for dep in s.dependencies:
            if dep in names:
                edges.append(Dependency(source=s.name, target=dep, kind="direct"))
    edges.sort(key=lambda e: (e.source, e.target))
    return edges


def _adjacency(subsystems: list[Subsystem]) -> dict[str, list[str]]:
    names = {s.name for s in subsystems}
    return {s.name: sorted(d for d in s.dependencies if d in names) for s in subsystems}


def transitive_closure(subsystems: list[Subsystem]) -> dict[str, list[str]]:
    adj = _adjacency(subsystems)
    out: dict[str, list[str]] = {}
    for node in adj:
        seen: set[str] = set()
        stack = list(adj[node])
        while stack:
            cur = stack.pop()
            if cur in seen or cur == node:
                continue
            seen.add(cur)
            stack.extend(adj.get(cur, []))
        out[node] = sorted(seen)
    return out


def find_cycles(subsystems: list[Subsystem]) -> list[list[str]]:
    adj = _adjacency(subsystems)
    cycles: list[list[str]] = []
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in adj}

    def dfs(node, path):
        color[node] = GRAY
        path.append(node)
        for nxt in adj.get(node, []):
            if color.get(nxt) == GRAY:
                cycle = path[path.index(nxt):] + [nxt]
                cycles.append(cycle)
            elif color.get(nxt) == WHITE:
                dfs(nxt, path)
        path.pop()
        color[node] = BLACK

    for node in sorted(adj):
        if color[node] == WHITE:
            dfs(node, [])
    # normaliza/dedup
    uniq = sorted({tuple(c) for c in cycles})
    return [list(c) for c in uniq]


def analyze_dependencies(subsystems: list[Subsystem]) -> dict:
    adj = _adjacency(subsystems)
    dependents: dict[str, list[str]] = {s.name: [] for s in subsystems}
    for src, deps in adj.items():
        for d in deps:
            dependents[d].append(src)
    roots = sorted(n for n, deps in adj.items() if not deps)            # no dependen de nadie
    leaves = sorted(n for n in adj if not dependents.get(n))            # nadie depende de ellos
    isolated = sorted(n for n in adj if not adj[n] and not dependents.get(n))
    return {
        "edges": [d.to_dict() for d in direct_dependencies(subsystems)],
        "transitive": transitive_closure(subsystems),
        "dependents": {k: sorted(v) for k, v in sorted(dependents.items())},
        "cycles": find_cycles(subsystems),
        "roots": roots,
        "leaves": leaves,
        "isolated": isolated,
    }
