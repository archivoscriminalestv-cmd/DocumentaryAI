"""Persistencia del DLE: escribe la base de conocimiento permanente.

Por documental:  documentary.json, scenes.json, shots.json, statistics.json,
transcript.json, report.md. Reproducible (``sort_keys``, sin marcas de tiempo dentro
del conocimiento). Nunca sobrescribe un documental distinto: el id es estable.
"""

import json
import os

from app.dle.models import DocumentaryKnowledge


def _dump(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_knowledge(doc_dir: str, k: DocumentaryKnowledge) -> dict[str, str]:
    os.makedirs(doc_dir, exist_ok=True)
    full = k.to_dict()
    paths = {
        "documentary": os.path.join(doc_dir, "documentary.json"),
        "scenes": os.path.join(doc_dir, "scenes.json"),
        "shots": os.path.join(doc_dir, "shots.json"),
        "statistics": os.path.join(doc_dir, "statistics.json"),
        "transcript": os.path.join(doc_dir, "transcript.json"),
        "report": os.path.join(doc_dir, "report.md"),
    }
    # documentary.json: índice (metadatos + recuentos + errores), sin los arrays grandes.
    _dump(paths["documentary"], {
        "schema_version": full["schema_version"],
        "documentary_id": full["documentary_id"],
        "metadata": full["metadata"],
        "counts": {"scenes": len(full["scenes"]), "shots": len(full["shots"]),
                   "narrative_blocks": len(full["narrative_blocks"]),
                   "errors": len(full["errors"])},
        "narrative_blocks": full["narrative_blocks"],
        "errors": full["errors"],
    })
    _dump(paths["scenes"], full["scenes"])
    _dump(paths["shots"], full["shots"])
    _dump(paths["statistics"], full["statistics"])
    _dump(paths["transcript"], full["transcript"])
    with open(paths["report"], "w", encoding="utf-8") as handle:
        handle.write(render_report(k))
    return paths


def _dist(title: str, dist: dict) -> list[str]:
    rows = [f"- **{k}:** {v}" for k, v in dist.items()]
    return [f"### {title}", "", *(rows or ["- (none)"]), ""]


def render_report(k: DocumentaryKnowledge) -> str:
    m, s = k.metadata, k.statistics
    lines = [
        f"# Documentary knowledge — {k.documentary_id}",
        "",
        f"- **Source:** {m.source_type} (`{m.source_ref}`)",
        f"- **Duration:** {m.duration:.1f}s  ·  **Resolution:** {m.width}x{m.height} @ {m.fps}fps  "
        f"·  **Audio:** {'yes' if m.has_audio else 'no'}",
        f"- **Shots:** {s.shot_count}  ·  **Scenes:** {s.scene_count}  ·  **Cuts:** {s.cut_count}",
        f"- **Avg shot length:** {s.average_shot_length:.2f}s (median {s.median_shot_length:.2f}s, "
        f"min {s.min_shot_length:.2f}, max {s.max_shot_length:.2f})  ·  **Pacing:** {s.pacing_tier}",
        f"- **Cuts/min:** {s.cuts_per_minute:.2f}  ·  **Close-up freq:** {s.close_up_frequency:.0%}",
        f"- **Time with audio/narration/music:** {s.time_with_audio:.1f}s / "
        f"{s.time_with_narration:.1f}s / {s.time_with_music:.1f}s",
        f"- **Transcript:** {k.transcript.provider} "
        f"({'available' if k.transcript.available else 'unavailable'})",
        f"- **Analysis errors:** {len(k.errors)}",
        "",
        *_dist("Shot size distribution", s.shot_size_distribution),
        *_dist("Movement distribution", s.movement_distribution),
        *_dist("Lighting distribution", s.lighting_distribution),
        *_dist("Color temperature distribution", s.color_temperature_distribution),
        *_dist("Dominant color distribution", s.dominant_color_distribution),
        "## Narrative blocks (structural; categories UNKNOWN until semantic analysis)",
        "",
        "| # | Start | End | Category | Label |",
        "|---|------:|----:|----------|-------|",
        *[f"| {b.index + 1} | {b.start:.1f} | {b.end:.1f} | {b.category} | {b.label} |"
          for b in k.narrative_blocks],
        "",
    ]
    if k.errors:
        lines += ["## Errors", "", *[f"- **{e.stage}:** {e.message}" for e in k.errors], ""]
    return "\n".join(lines)
