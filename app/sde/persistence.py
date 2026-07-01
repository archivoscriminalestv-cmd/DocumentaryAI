"""Persistencia del SDE: shot_history.json + shot_diversity_report.md.

Reproducible (mismo documental → mismo plan visual → mismos ficheros).
"""

import json
import os


def write_outputs(out_dir: str, engine) -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    history_path = os.path.join(out_dir, "shot_history.json")
    report_path = os.path.join(out_dir, "shot_diversity_report.md")

    with open(history_path, "w", encoding="utf-8") as handle:
        json.dump(engine.history.to_dict(), handle, ensure_ascii=False, indent=2, sort_keys=True)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(render_report(engine))

    return {"history": history_path, "report": report_path}


def _dist_block(title: str, dist: dict) -> list[str]:
    rows = [f"- **{k}:** {v}" for k, v in sorted(dist.items(), key=lambda kv: (-kv[1], str(kv[0])))]
    return [f"### {title}", "", *(rows or ["- (none)"]), ""]


def render_report(engine) -> str:
    s = engine.stats()
    records = engine.history.all()
    lines = [
        "# Shot Diversity report",
        "",
        f"- **Total shots:** {s['total_shots']}",
        f"- **Average diversity score:** {s['average_diversity']:.2f} (0=idéntico, 1=máxima variedad)",
        f"- **Repetitions detected (diversity < 0.5):** {s['repetitions_detected']}",
        f"- **Variations applied (field changes):** {s['variations_applied']}",
        "",
        *_dist_block("Shot sizes used", s["by_shot_size"]),
        *_dist_block("Lens distribution (mm)", s["by_lens"]),
        *_dist_block("Composition distribution", s["by_composition"]),
        *_dist_block("Camera angle distribution", s["by_angle"]),
        *_dist_block("Camera height distribution", s["by_height"]),
        "## Per-shot decisions",
        "",
        "| # | Shot | Mode | Size | Angle | Height | Lens | Composition | Pos | Diversity | Changes |",
        "|---|------|------|------|-------|--------|-----:|-------------|-----|----------:|--------:|",
    ]
    for r in records:
        fp = r.fingerprint
        lines.append(
            f"| {r.index + 1} | {r.shot_id} | {r.narrative_mode} | {fp.shot_size} | "
            f"{fp.camera_angle} | {fp.camera_height} | {fp.lens} | {fp.composition} | "
            f"{fp.subject_position} | {r.diversity_score:.2f} | {len(r.changes)} |"
        )
    return "\n".join(lines) + "\n"
