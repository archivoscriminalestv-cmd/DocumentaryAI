"""LearningMonitor — agrega eventos públicos en un estado observable (DLE-003).

Escucha ``ProgressEvent`` y mantiene un ``MonitorState`` (documental actual, posición,
porcentaje global, etapa, plano/escena, ETA, horas/documentales aprendidos, tamaño de
la base de conocimiento). Determinista: el mismo flujo de eventos + el mismo reloj
producen el mismo estado. El reloj es inyectable para los tests.
"""

import time
from dataclasses import dataclass

from app.dle.monitor.events import FAILED, FINISHED, STARTED

# Fracción de avance del documental actual por etapa (para el porcentaje global).
_STAGE_BASE = {"downloading": 0.05, "analyzing": 0.10, "learning": 0.85, "storing": 0.95}


@dataclass
class MonitorState:
    total: int = 0
    position: int = 0
    doc_ref: str = ""
    doc_id: str = ""
    stage: str = ""
    shot_index: int = 0
    shot_total: int = 0
    scene_total: int = 0
    completed: int = 0
    item_fraction: float = 0.0
    global_percent: float = 0.0
    docs_learned: int = 0
    hours_learned: float = 0.0
    kb_size_bytes: int = 0
    last_error: str = ""
    elapsed: float = 0.0
    eta: float = 0.0
    finished: bool = False


class LearningMonitor:
    def __init__(self, clock=time.monotonic) -> None:
        self._clock = clock
        self._start: float | None = None
        self.state = MonitorState()

    def handle(self, event) -> MonitorState:
        s = self.state
        if self._start is None:
            self._start = self._clock()

        # Solo los campos presentes (no None) actualizan el estado.
        if event.total is not None:
            s.total = event.total
        if event.position is not None:
            s.position = event.position
        if event.doc_ref is not None:
            s.doc_ref = event.doc_ref
        if event.doc_id is not None:
            s.doc_id = event.doc_id
        if event.shot_total is not None:
            s.shot_total = event.shot_total
        if event.shot_index is not None:
            s.shot_index = event.shot_index
        if event.scene_total is not None:
            s.scene_total = event.scene_total
        if event.metrics:
            s.docs_learned = event.metrics.get("documentaries_learned", s.docs_learned)
            s.hours_learned = event.metrics.get("hours_learned", s.hours_learned)
            s.kb_size_bytes = event.metrics.get("kb_size_bytes", s.kb_size_bytes)

        # Inicio de un documental: reinicia el progreso intra-documental.
        if event.stage == "item" and event.kind == STARTED:
            s.item_fraction = 0.0
            s.stage = "starting"
            s.shot_index = s.shot_total = s.scene_total = 0

        # Avance por etapa del pipeline.
        if event.stage in _STAGE_BASE:
            s.stage = event.stage
            base = _STAGE_BASE[event.stage]
            if event.stage == "analyzing" and event.percent is not None:
                base = 0.10 + 0.70 * event.percent
            s.item_fraction = max(s.item_fraction, base)

        # Fin (o fallo) de un documental: cuenta como completado.
        if event.kind in (FINISHED, FAILED) and event.stage == "item":
            s.completed += 1
            s.item_fraction = 0.0
            if event.kind == FAILED and event.error:
                s.last_error = event.error

        if event.kind == FINISHED and event.stage == "queue":
            s.finished = True

        # Porcentaje global y ETA.
        if s.total > 0:
            done = min(float(s.total), s.completed + s.item_fraction)
            s.global_percent = min(1.0, done / s.total)
        if s.finished:
            s.global_percent = 1.0
        s.elapsed = self._clock() - self._start
        s.eta = (
            s.elapsed * (1.0 - s.global_percent) / s.global_percent
            if 0.0 < s.global_percent < 1.0 and not s.finished else 0.0
        )
        return s
