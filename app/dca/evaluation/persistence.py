"""Persistencia del Self Evaluation (DCA-003) — escribe SOLO en ``output/dca/``.

Reproducible (``sort_keys``). NUNCA escribe en ``knowledge/``.
"""

import json
import os


def _dump(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_evaluation_outputs(out_dir: str, result) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = {name: os.path.join(out_dir, name) for name in (
        "evaluation.json", "generation_vs_corpus.json", "improvement_plan.json",
        "system_health.json", "evaluation_report.md")}

    _dump(paths["evaluation.json"], result.to_dict())
    _dump(paths["generation_vs_corpus.json"], result.generation_vs_corpus())
    _dump(paths["improvement_plan.json"], {"roadmap": [i.to_dict() for i in result.roadmap]})
    _dump(paths["system_health.json"], result.health.to_dict())
    with open(paths["evaluation_report.md"], "w", encoding="utf-8") as handle:
        handle.write(_render_report(result))
    return paths


def _render_report(result) -> str:
    h = result.health.to_dict()
    lines = [
        "# DocumentaryAI — Self Evaluation (DCA)",
        "",
        f"- versión: `{result.eval_version}`",
        "",
        "## Generación vs Corpus",
        "",
        "| dimensión | corpus | generado | desviación | estado |",
        "|---|---|---|---|---|",
    ]
    for c in result.comparisons:
        dev = "—" if c.deviation is None else f"{round(c.deviation * 100)}%"
        lines.append(f"| {c.dimension} | {c.corpus_value} | {c.generated_value} | {dev} | {c.status} |")

    lines += ["", "## Huecos (hechos, no opiniones)"]
    for g in result.gaps:
        lines.append(f"- [{g.owner}] {g.description}")
    if not result.gaps:
        lines.append("- —")

    lines += ["", "## Roadmap (prioridad objetiva)"]
    for item in result.roadmap:
        m = item.metrics
        lines.append(f"{item.priority_rank}. **{item.target}** — "
                     f"{m.get('consumers_affected', 0)} consumidores afectados · "
                     f"magnitud {m.get('max_gap_magnitude', 0)}")
        if item.rationale:
            lines.append(f"    - {item.rationale}")

    lines += [
        "", "## System Health (indicadores objetivos)",
        f"- knowledge_utilization: {h['knowledge_utilization']}",
        f"- generation_coverage: {h['generation_coverage']}",
        f"- corpus_alignment: {h['corpus_alignment']}",
        f"- evidence_coverage: {h['evidence_coverage']}",
        f"- unknown_decisions: {h['unknown_decisions']}",
        f"- integrated_capabilities: {h['integrated_capabilities']} · "
        f"missing_capabilities: {h['missing_capabilities']}",
        "",
        "> DCA Self Evaluation: solo mide hechos (sin IA, sin opinión). Mide la distancia de "
        "la generación respecto al corpus y propone, por reglas objetivas, el siguiente motor "
        "a mejorar.",
        "",
    ]
    return "\n".join(lines)
