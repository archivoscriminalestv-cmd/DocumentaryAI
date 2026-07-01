"""Persistencia del dashboard: dashboard_history.json + session_statistics.json."""

import json
import os

from app.dlm import SCHEMA_VERSION
from app.dlm.models import DashboardState


def session_statistics(state: DashboardState, *, started_at: float = 0.0,
                       finished_at: float = 0.0) -> dict:
    g, c = state.globals, state.corpus
    return {
        "schema_version": SCHEMA_VERSION,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": round(g.elapsed, 3),
        "documentaries_learned": g.completed,
        "failed": g.failed,
        "skipped": g.skipped,
        "hours_video": c.hours,
        "shots": c.shots,
        "scenes": c.scenes,
        "videos_per_hour": g.videos_per_hour,
        "knowledge_bytes": c.knowledge_bytes,
        "errors": list(state.errors),
    }


def write_outputs(knowledge_root: str, state: DashboardState, *,
                  started_at: float = 0.0, finished_at: float = 0.0) -> dict[str, str]:
    os.makedirs(knowledge_root, exist_ok=True)
    stats = session_statistics(state, started_at=started_at, finished_at=finished_at)
    paths = {
        "history": os.path.join(knowledge_root, "dashboard_history.json"),
        "session": os.path.join(knowledge_root, "session_statistics.json"),
    }
    # history: append-only de sesiones (acumulativo).
    history = {"sessions": []}
    if os.path.exists(paths["history"]):
        try:
            with open(paths["history"], encoding="utf-8") as h:
                history = json.load(h)
        except (OSError, json.JSONDecodeError):
            history = {"sessions": []}
    history.setdefault("sessions", []).append(stats)
    with open(paths["history"], "w", encoding="utf-8") as h:
        json.dump(history, h, ensure_ascii=False, indent=2)
    with open(paths["session"], "w", encoding="utf-8") as h:
        json.dump(stats, h, ensure_ascii=False, indent=2)
    return paths
