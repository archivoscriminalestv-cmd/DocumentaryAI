"""Persistencia del DCA: escribe el modelo arquitectónico en ``output/dca/``.

Reproducible (``sort_keys``). NUNCA escribe en ``knowledge/``.
"""

import json
import os

from app.dca.capability_graph import capability_edges


def _dump(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_outputs(out_dir: str, architect) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    snapshot = architect.snapshot()
    caps = architect.capabilities()
    deps = architect.dependencies()
    roadmap = architect.roadmap()
    recs = architect.recommend()
    analysis = architect.analyze()

    paths = {name: os.path.join(out_dir, name) for name in (
        "architecture.json", "capability_graph.json", "dependency_graph.json",
        "roadmap.json", "recommendations.json", "architecture_report.md")}

    _dump(paths["architecture.json"], snapshot.to_dict())
    _dump(paths["capability_graph.json"], {
        "capabilities": [c.to_dict() for c in caps],
        "edges": capability_edges(caps)})
    _dump(paths["dependency_graph.json"], deps)
    _dump(paths["roadmap.json"], roadmap.to_dict())
    _dump(paths["recommendations.json"], {"recommendations": [r.to_dict() for r in recs]})

    with open(paths["architecture_report.md"], "w", encoding="utf-8") as handle:
        handle.write(_render_report(snapshot, analysis, roadmap))
    return paths


def _render_report(snapshot, analysis, roadmap) -> str:
    arch = snapshot.architecture
    cov = arch.coverage
    lines = [
        "# DocumentaryAI — Architecture report (DCA)",
        "",
        f"- subsistemas: **{snapshot.totals['subsystems']}** · dominios: "
        f"{snapshot.totals['domains']} · capacidades: {snapshot.totals['capabilities']}",
        f"- implementados: {cov.get('implemented', 0)}/{cov.get('total_subsystems', 0)} "
        f"({cov.get('implemented_percent', 0) * 100:.0f}%)",
        f"- dependencias: {snapshot.totals['dependencies']} · ciclos: "
        f"{snapshot.totals['cycles']} · aislados: {snapshot.totals['isolated']} · "
        f"huecos: {snapshot.totals['gaps']}",
        "",
        "## Dominios",
    ]
    for d in arch.domains:
        lines.append(f"- **{d.name}**: {', '.join(d.subsystems)}")

    lines += ["", "## Objetivos arquitectónicos"]
    for g in arch.goals:
        lines.append(f"- [{g.status}] {g.name}")

    lines += ["", "## Huecos detectados"]
    for gap in analysis["gaps"]:
        lines.append(f"- [{gap['kind']}] {gap['description']}")
    if not analysis["gaps"]:
        lines.append("- —")

    lines += ["", "## Roadmap (prioridad objetiva)"]
    for item in roadmap.items[:15]:
        m = item.metrics
        lines.append(f"{item.priority_rank}. **{item.target}** — {m['gap_kind']} "
                     f"(consumidores afectados: {m['consumers']})")

    lines += [
        "",
        "## Aislados / ciclos",
        f"- aislados: {', '.join(analysis['isolated']) or '—'}",
        f"- ciclos: {analysis['cycles'] or '—'}",
        "",
        "> DCA: solo lectura, determinista, sin IA. Modelo arquitectónico de DocumentaryAI; "
        "no ejecuta ni modifica ningún motor.",
        "",
    ]
    return "\n".join(lines)
