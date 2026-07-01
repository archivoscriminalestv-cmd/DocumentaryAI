"""StatusService (DAS-001) — lee el estado YA EXISTENTE. Nunca recalcula estadísticas.

Consume ``knowledge/learning_statistics.json`` (cifras que ya produce el DLE) y
``knowledge/learning_queue.json`` (para el vídeo en curso). Combinado con el estado de proceso
de LearningService, entrega un ``StatusSnapshot`` de solo texto para la UI.
"""

import json
import os

from app.studio import config
from app.studio.services.learning_service import LearningService
from app.studio.services.models import StatusSnapshot

# Estados de la cola que significan "vídeo en curso" (copiado como constante para no acoplar
# Studio al DLE; equivale a QueueStatus.IN_FLIGHT).
_IN_FLIGHT = ("DOWNLOADING", "ANALYZING", "LEARNING", "STORING")


def _read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as h:
            return json.load(h)
    except (OSError, ValueError):
        return {}


class StatusService:
    def __init__(self, root: str | None = None, learning_service: LearningService | None = None) -> None:
        self._root = config.project_root(root)
        self._learning = learning_service or LearningService(self._root)

    def snapshot(self) -> StatusSnapshot:
        stats = _read_json(config.stats_path(self._root))
        state = self._learning.learning_state()
        return StatusSnapshot(
            learning=state.running,
            learned=int(stats.get("documentaries_learned", 0) or 0),
            pending=int(stats.get("pending", 0) or 0),
            failed=int(stats.get("failed", 0) or 0),
            skipped=int(stats.get("skipped", 0) or 0),
            hours_learned=float(stats.get("hours_learned", 0.0) or 0.0),
            shots_analyzed=int(stats.get("shots_analyzed", 0) or 0),
            scenes=int(stats.get("scenes", 0) or 0),
            current_video=self._current_video(),
            runtime_seconds=state.runtime_seconds,
            source=state.source)

    def _current_video(self) -> str:
        data = _read_json(config.queue_path(self._root))
        items = data.get("items", []) if isinstance(data, dict) else []
        for item in items:
            if item.get("status") in _IN_FLIGHT:
                return item.get("video_id") or item.get("url") or ""
        return ""
