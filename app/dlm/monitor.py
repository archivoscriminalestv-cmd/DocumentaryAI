"""DashboardMonitor — agrega los eventos públicos en un ``DashboardState`` rico.

Por COMPOSICIÓN: reutiliza el ``LearningMonitor`` (DLE-003) para el progreso global/ETA
y añade salud de motores, throughput, últimos eventos, errores y estadísticas del vídeo
actual (leídas de los artefactos PÚBLICOS de ``knowledge/`` al terminar cada documental).
No inspecciona el estado interno de ningún subsistema. Determinista (reloj inyectable).
"""

import json
import os
import time
from collections import deque

from app.dle.monitor.events import FAILED, FINISHED, STARTED
from app.dle.monitor.monitor import LearningMonitor
from app.dlm.models import (
    ENGINES,
    STAGE_ORDER,
    CorpusStatistics,
    CurrentDocument,
    DashboardState,
    EngineHealth,
    GlobalStatistics,
    HealthStatus,
)
from app.dlm.statistics import ETAEstimator, SpeedEstimator, ThroughputCalculator


class DashboardMonitor:
    def __init__(self, *, clock=time.monotonic, knowledge_root: str = "knowledge",
                 max_events: int = 8) -> None:
        self._inner = LearningMonitor(clock=clock)
        self._knowledge_root = knowledge_root
        self._speed = SpeedEstimator()
        self._events: deque[str] = deque(maxlen=max_events)
        self._errors: list[str] = []
        self._cur_stage = ""
        self._item_state = "idle"          # idle | running | finished | failed
        self._completed = 0
        self._failed = 0
        self._skipped = 0
        self._shots = 0
        self._scenes = 0
        self._hours_baseline: float | None = None   # horas de vídeo al iniciar la sesión
        self._session_hours = 0.0                    # horas de vídeo aprendidas ESTA sesión
        self._current = CurrentDocument()

    # ------------------------------------------------------------------ ingest
    def handle(self, event) -> DashboardState:
        base = self._inner.handle(event)

        # Horas de vídeo aprendidas ESTA sesión (delta sobre la línea base acumulada).
        if event.metrics and "hours_learned" in event.metrics:
            current = float(event.metrics["hours_learned"])
            if self._hours_baseline is None:
                self._hours_baseline = current
            self._session_hours = max(0.0, current - self._hours_baseline)

        if event.stage == "item" and event.kind == STARTED:
            self._item_state = "running"
            self._cur_stage = ""
            self._current = CurrentDocument()
        if event.stage in STAGE_ORDER:
            self._cur_stage = event.stage
            self._item_state = "running"

        if event.kind in (FINISHED, FAILED) and event.stage == "item":
            if event.kind == FAILED:
                self._item_state = "failed"
                self._failed += 1
                if event.error:
                    self._errors.append(event.error)
            else:
                self._item_state = "finished"
                self._completed += 1
                self._speed.record_completion(base.elapsed)
                self._shots += base.shot_total
                self._scenes += base.scene_total
                self._load_video_stats(base.doc_id)

        label = f"[{_mark(event.kind)}] {event.stage}"
        if event.doc_id or event.doc_ref:
            label += f" · {event.doc_id or event.doc_ref}"
        self._events.append(label)

        self._current.doc_ref = base.doc_ref
        self._current.doc_id = base.doc_id
        self._current.position = base.position
        self._current.total = base.total
        self._current.stage = self._cur_stage
        self._current.shot_index = base.shot_index
        self._current.shot_total = base.shot_total
        self._current.scene_total = base.scene_total
        self._current.item_percent = round(base.item_fraction, 4)
        return self.snapshot()

    # ------------------------------------------------------------------ stats
    def _load_video_stats(self, doc_id: str) -> None:
        path = os.path.join(self._knowledge_root, "documentaries", doc_id or "", "statistics.json")
        if not doc_id or not os.path.exists(path):
            return
        try:
            with open(path, encoding="utf-8") as h:
                st = json.load(h)
        except (OSError, json.JSONDecodeError):
            return
        self._current.avg_shot_length = st.get("average_shot_length", 0.0)
        self._current.cuts_per_minute = st.get("cuts_per_minute", 0.0)
        self._current.dominant_movement = _dominant(st.get("movement_distribution", {}))
        self._current.dominant_color_temperature = _dominant(st.get("color_temperature_distribution", {}))
        self._current.audio_seconds = st.get("time_with_audio", 0.0)
        self._current.narration_seconds = st.get("time_with_narration", 0.0)

    def _corpus(self, base) -> CorpusStatistics:
        c = CorpusStatistics(documentaries=base.docs_learned, hours=round(base.hours_learned, 3),
                             videos=base.docs_learned, knowledge_bytes=base.kb_size_bytes)
        path = os.path.join(self._knowledge_root, "learning_statistics.json")
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as h:
                    ls = json.load(h)
                c.documentaries = ls.get("documentaries_learned", c.documentaries)
                c.videos = c.documentaries
                c.shots = ls.get("shots_analyzed", 0)
                c.scenes = ls.get("scenes", 0)
                c.hours = round(ls.get("hours_learned", c.hours), 3)
            except (OSError, json.JSONDecodeError):
                pass
        return c

    def _engine_health(self) -> list[EngineHealth]:
        out: list[EngineHealth] = []
        cur_idx = STAGE_ORDER.index(self._cur_stage) if self._cur_stage in STAGE_ORDER else -1
        for name, stage in ENGINES:
            e_idx = STAGE_ORDER.index(stage)
            if self._inner.state.finished:
                status = HealthStatus.FINISHED
            elif self._item_state == "idle":
                status = HealthStatus.WAITING
            elif self._item_state == "finished":
                status = HealthStatus.FINISHED
            elif self._item_state == "failed":
                status = (HealthStatus.FINISHED if e_idx < cur_idx
                          else HealthStatus.FAILED if e_idx == cur_idx
                          else HealthStatus.WAITING)
            else:  # running
                status = (HealthStatus.FINISHED if e_idx < cur_idx
                          else HealthStatus.RUNNING if e_idx == cur_idx
                          else HealthStatus.WAITING)
            out.append(EngineHealth(name=name, stage=stage, status=status))
        return out

    def snapshot(self) -> DashboardState:
        base = self._inner.state
        elapsed = base.elapsed
        corpus = self._corpus(base)
        g = GlobalStatistics(
            elapsed=round(elapsed, 3),
            eta_queue=round(base.eta, 3),
            eta_video=ETAEstimator.remaining(elapsed, base.item_fraction),
            global_percent=round(base.global_percent, 4),
            videos_per_hour=ThroughputCalculator.per_hour(self._completed, elapsed),
            video_hours_per_hour=ThroughputCalculator.per_hour(self._session_hours, elapsed),
            shots_per_minute=ThroughputCalculator.per_minute(self._shots, elapsed),
            scenes_per_minute=ThroughputCalculator.per_minute(self._scenes, elapsed),
            knowledge_mb_per_hour=ThroughputCalculator.mb_per_hour(corpus.knowledge_bytes, elapsed),
            completed=self._completed, failed=self._failed, skipped=self._skipped,
        )
        return DashboardState(
            finished=base.finished, queue_total=base.total, queue_position=base.position,
            corpus=corpus, current=self._current, globals=g,
            engines=self._engine_health(), last_events=list(self._events),
            errors=list(self._errors),
        )


def _mark(kind: str) -> str:
    return {"FINISHED": "OK", "FAILED": "ERR", "STARTED": ">>", "PROGRESS": ".."}.get(kind, kind)


def _dominant(dist: dict) -> str:
    if not dist:
        return "—"
    return max(dist.items(), key=lambda kv: kv[1])[0]
