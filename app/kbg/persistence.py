"""Persistencia del KBG: escribe ``GenerationKnowledge`` en ``output/kbg/``.

Reproducible (``sort_keys``). NUNCA escribe en ``knowledge/``.
"""

import json
import os

from app.kbg.models import GenerationKnowledge


def write_outputs(out_dir: str, gk: GenerationKnowledge) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = {
        "generation_knowledge": os.path.join(out_dir, "GenerationKnowledge.json"),
        "report": os.path.join(out_dir, "generation_knowledge_report.md"),
    }
    with open(paths["generation_knowledge"], "w", encoding="utf-8") as handle:
        json.dump(gk.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)
    with open(paths["report"], "w", encoding="utf-8") as handle:
        handle.write(_render_report(gk))
    return paths


def _render_report(gk: GenerationKnowledge) -> str:
    s = gk.summary
    lines = [
        f"# Generation Knowledge — género: {gk.genre}",
        "",
        f"- versión: `{gk.kbg_version}`",
        f"- decisiones conocidas: {s.get('known', 0)}/{s.get('total_decisions', 0)} "
        f"({s.get('known_ratio', 0) * 100:.0f}%)",
        "- fuentes aplicadas: " + (", ".join(s.get("applied_sources", [])) or "—"),
        "",
        "> KBG = frontera entre Learning y Generation. Cada decisión es trazable "
        "(origen/confianza/fuentes/motivo); `UNKNOWN` cuando no hay conocimiento suficiente.",
    ]
    for section, decisions in gk.sections.items():
        lines += ["", f"## {section}"]
        for d in decisions:
            val = d.value if d.known else "UNKNOWN"
            lines.append(f"- **{d.key}**: {val}  ·  conf {d.confidence}  ·  {d.origin}")
            if d.reason:
                lines.append(f"    - {d.reason}")
    lines.append("")
    return "\n".join(lines)
