"""Persistencia del CME: motion_history.json + motion_manifest.json + motion_report.md.

Reproducible (mismo documental → mismo plan de cámara → mismos ficheros).
"""

import json
import os


def write_outputs(out_dir: str, engine, *, project: str = "") -> dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    history_path = os.path.join(out_dir, "motion_history.json")
    manifest_path = os.path.join(out_dir, "motion_manifest.json")
    report_path = os.path.join(out_dir, "motion_report.md")

    with open(history_path, "w", encoding="utf-8") as handle:
        json.dump({"project": project, "shots": engine.history()}, handle,
                  ensure_ascii=False, indent=2, sort_keys=True)
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump({"project": project, "total_duration": engine.timeline.total_duration,
                   "shots": engine.manifest()}, handle, ensure_ascii=False, indent=2)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(render_report(engine))

    return {"history": history_path, "manifest": manifest_path, "report": report_path}


def _dist_block(title: str, dist: dict) -> list[str]:
    rows = [f"- **{k}:** {v}" for k, v in sorted(dist.items(), key=lambda kv: (-kv[1], str(kv[0])))]
    return [f"### {title}", "", *(rows or ["- (none)"]), ""]


def render_report(engine) -> str:
    s = engine.stats()
    lines = [
        "# Motion report",
        "",
        f"- **Total shots:** {s['total_shots']}",
        f"- **Motion diversity score:** {s['average_diversity']:.2f} (0=monótono, 1=máxima variedad)",
        f"- **Repetitions (diversity < 0.5):** {s['repetitions']}",
        f"- **Average speed:** {s['average_speed']}",
        f"- **Average duration:** {s['average_duration']:.2f}s",
        f"- **Total timeline duration:** {s['total_duration']:.2f}s",
        f"- **Cinematic energy (avg):** {s['cinematic_energy']:.2f}",
        "",
        *_dist_block("Motion distribution", s["by_motion_type"]),
        *_dist_block("Camera family (continuity)", s["by_family"]),
        *_dist_block("Direction distribution", s["by_direction"]),
        "## Per-shot motion plan",
        "",
        "| # | Shot | Asset | Motion | Family | Dir | Dur (s) | Energy | Purpose |",
        "|---|------|-------|--------|--------|-----|--------:|-------:|---------|",
    ]
    for i, sh in enumerate(engine.shots, start=1):
        lines.append(
            f"| {i} | {sh.shot_id} | {sh.asset_id or '—'} | {sh.motion_type} | {sh.family} | "
            f"{sh.direction} | {sh.duration:.1f} | {sh.fingerprint.camera_energy:.2f} | {sh.purpose} |"
        )
    return "\n".join(lines) + "\n"
