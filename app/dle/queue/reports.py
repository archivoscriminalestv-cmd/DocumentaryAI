"""Informes del aprendizaje por lotes (learning_report.md / _statistics.json / _history.json)."""

import json
import os

from app.dle.queue.models import QueueStatus


def _read_stats(knowledge_root: str, documentary_id: str) -> dict:
    path = os.path.join(knowledge_root, "documentaries", documentary_id, "statistics.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as h:
            return json.load(h)
    except (OSError, json.JSONDecodeError):
        return {}


def _read_meta_duration(knowledge_root: str, documentary_id: str) -> float:
    path = os.path.join(knowledge_root, "documentaries", documentary_id, "documentary.json")
    if not os.path.exists(path):
        return 0.0
    try:
        with open(path, encoding="utf-8") as h:
            return float(json.load(h).get("metadata", {}).get("duration", 0.0))
    except (OSError, json.JSONDecodeError, TypeError):
        return 0.0


def build_statistics(store, knowledge_root: str) -> dict:
    items = store.ordered()
    counts: dict[str, int] = {s: 0 for s in QueueStatus.ALL}
    for i in items:
        counts[i.status] = counts.get(i.status, 0) + 1

    total_shots = total_scenes = 0
    total_duration = 0.0
    learned = [i for i in items if i.status == QueueStatus.FINISHED]
    for i in learned:
        st = _read_stats(knowledge_root, i.documentary_id)
        total_shots += int(st.get("shot_count", 0))
        total_scenes += int(st.get("scene_count", 0))
        total_duration += _read_meta_duration(knowledge_root, i.documentary_id)

    pending = counts.get(QueueStatus.PENDING, 0)
    return {
        "total_in_queue": len(items),
        "documentaries_learned": len(learned),
        "skipped": counts.get(QueueStatus.SKIPPED, 0),
        "failed": counts.get(QueueStatus.FAILED, 0),
        "pending": pending,
        "remaining": pending + counts.get(QueueStatus.FAILED, 0),
        "shots_analyzed": total_shots,
        "scenes": total_scenes,
        "total_duration_seconds": round(total_duration, 3),
        "hours_learned": round(total_duration / 3600.0, 3),
        "status_counts": counts,
    }


def write_reports(store, history: list[dict], knowledge_root: str) -> dict[str, str]:
    os.makedirs(knowledge_root, exist_ok=True)
    stats = build_statistics(store, knowledge_root)
    paths = {
        "statistics": os.path.join(knowledge_root, "learning_statistics.json"),
        "history": os.path.join(knowledge_root, "learning_history.json"),
        "report": os.path.join(knowledge_root, "learning_report.md"),
    }
    with open(paths["statistics"], "w", encoding="utf-8") as h:
        json.dump(stats, h, ensure_ascii=False, indent=2, sort_keys=True)
    with open(paths["history"], "w", encoding="utf-8") as h:
        json.dump({"events": history}, h, ensure_ascii=False, indent=2)
    with open(paths["report"], "w", encoding="utf-8") as h:
        h.write(_render_report(stats, store))
    return paths


def _render_report(s: dict, store) -> str:
    lines = [
        "# Learning report",
        "",
        f"- **Documentaries in queue:** {s['total_in_queue']}",
        f"- **Learned:** {s['documentaries_learned']}  ·  **Skipped:** {s['skipped']}  ·  "
        f"**Failed:** {s['failed']}  ·  **Pending:** {s['pending']}  ·  **Remaining:** {s['remaining']}",
        f"- **Hours learned:** {s['hours_learned']:.2f}h ({s['total_duration_seconds']:.0f}s)",
        f"- **Shots analyzed:** {s['shots_analyzed']}  ·  **Scenes:** {s['scenes']}",
        f"- **Queue paused:** {'yes' if store.is_paused() else 'no'}",
        "",
        "## Status counts",
        "",
        *[f"- **{k}:** {v}" for k, v in s["status_counts"].items() if v],
        "",
        "## Queue",
        "",
        "| # | Status | Kind | Documentary | URL |",
        "|---|--------|------|-------------|-----|",
    ]
    for i in store.ordered():
        lines.append(f"| {i.order} | {i.status} | {i.kind} | {i.documentary_id or '—'} | {i.url} |")
    return "\n".join(lines) + "\n"
