"""Tests del Live Learning Monitor (DLE-003) — deterministas, sin red ni ffmpeg.

Eventos públicos → estado del monitor → render. Incluye el cableado real con el
LearningQueueManager usando un motor DLE falso.
"""

import os

from app.dle.monitor.events import (
    FAILED,
    FINISHED,
    PROGRESS,
    STARTED,
    ProgressEvent,
    with_context,
)
from app.dle.monitor.monitor import LearningMonitor
from app.dle.monitor.render import render
from app.dle.queue import LearningQueueManager
from app.dle.queue.index import KnowledgeIndex
from app.dle.queue.store import QueueStore


class _Clock:
    """Reloj inyectable y determinista."""
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


# --- estado del monitor ------------------------------------------------------
def test_monitor_tracks_position_stage_and_shots():
    m = LearningMonitor(clock=_Clock())
    m.handle(ProgressEvent(STARTED, "queue", total=3))
    m.handle(ProgressEvent(STARTED, "item", position=1, total=3, doc_ref="https://y/1"))
    m.handle(ProgressEvent(STARTED, "downloading"))
    m.handle(ProgressEvent(PROGRESS, "analyzing", shot_index=3, shot_total=10, percent=0.3))
    s = m.state
    assert s.position == 1 and s.total == 3
    assert s.doc_ref == "https://y/1"
    assert s.stage == "analyzing"
    assert s.shot_index == 3 and s.shot_total == 10
    assert 0.0 < s.global_percent < 1.0


def test_monitor_global_percent_progresses_and_completes():
    m = LearningMonitor(clock=_Clock())
    m.handle(ProgressEvent(STARTED, "queue", total=2))
    m.handle(ProgressEvent(STARTED, "item", position=1, total=2))
    m.handle(ProgressEvent(FINISHED, "item"))
    assert abs(m.state.global_percent - 0.5) < 1e-9      # 1 de 2 completado
    m.handle(ProgressEvent(STARTED, "item", position=2, total=2))
    m.handle(ProgressEvent(FINISHED, "item"))
    m.handle(ProgressEvent(FINISHED, "queue"))
    assert m.state.global_percent == 1.0 and m.state.finished is True


def test_monitor_eta_uses_injected_clock():
    clk = _Clock()
    m = LearningMonitor(clock=clk)
    m.handle(ProgressEvent(STARTED, "queue", total=4))
    clk.t = 10.0
    m.handle(ProgressEvent(FINISHED, "item", position=1, total=4))   # 25% en 10s
    # quedan 30s estimados (3x lo transcurrido)
    assert abs(m.state.eta - 30.0) < 1e-6
    assert m.state.elapsed == 10.0


def test_monitor_reads_metrics_and_records_errors():
    m = LearningMonitor(clock=_Clock())
    m.handle(ProgressEvent(STARTED, "queue", total=1))
    m.handle(ProgressEvent(PROGRESS, "queue",
                           metrics={"documentaries_learned": 7, "hours_learned": 1.5,
                                    "kb_size_bytes": 2048}))
    m.handle(ProgressEvent(FAILED, "item", error="boom"))
    assert m.state.docs_learned == 7 and m.state.hours_learned == 1.5
    assert m.state.kb_size_bytes == 2048
    assert m.state.last_error == "boom"


def test_monitor_is_deterministic():
    events = [
        ProgressEvent(STARTED, "queue", total=2),
        ProgressEvent(STARTED, "item", position=1, total=2, doc_ref="a"),
        ProgressEvent(PROGRESS, "analyzing", shot_index=1, shot_total=4, percent=0.25),
        ProgressEvent(FINISHED, "item"),
    ]
    a, b = LearningMonitor(clock=_Clock()), LearningMonitor(clock=_Clock())
    for e in events:
        a.handle(e)
        b.handle(e)
    assert a.state == b.state


# --- render ------------------------------------------------------------------
def test_render_is_pure_and_contains_key_fields():
    m = LearningMonitor(clock=_Clock())
    m.handle(ProgressEvent(STARTED, "queue", total=3))
    m.handle(ProgressEvent(STARTED, "item", position=2, total=3, doc_ref="https://y/2"))
    m.handle(ProgressEvent(PROGRESS, "analyzing", shot_index=5, shot_total=20, percent=0.25))
    out = render(m.state)
    assert render(m.state) == out                 # puro (sin estado oculto)
    assert "https://y/2" in out and "2/3" in out
    assert "analyzing" in out and "5/20" in out
    assert "%" in out and "ETA" in out


# --- with_context ------------------------------------------------------------
def test_with_context_fills_only_missing_fields():
    captured = []
    sink = with_context(captured.append, position=4, total=9, doc_ref="ctx")
    sink(ProgressEvent(PROGRESS, "analyzing", shot_index=1, shot_total=2))
    ev = captured[0]
    assert ev.position == 4 and ev.total == 9 and ev.doc_ref == "ctx"
    # no pisa lo que el emisor ya puso
    sink(ProgressEvent(STARTED, "item", position=1))
    assert captured[1].position == 1


# --- cableado real con el manager (motor DLE falso) --------------------------
class _FakeEngine:
    def __init__(self):
        self.store = _FakeStore()

    def learn(self, *, youtube=None, video=None, force=False, on_stage=None,
              work_dir=None, on_event=None):
        ref = youtube or video
        if on_event:
            on_event(ProgressEvent(STARTED, "downloading"))
            on_event(ProgressEvent(STARTED, "analyzing"))
            on_event(ProgressEvent(PROGRESS, "analyzing", shot_index=1, shot_total=1, percent=1.0))
        from app.dle.queue.downloader import resolve_source
        doc_id = resolve_source(ref).documentary_id
        self.store.add(doc_id)

        class _K:
            schema_version = "1.0"

            class statistics:
                shot_count = 1
                scene_count = 1
        return {"status": "learned", "documentary_id": doc_id, "knowledge": _K()}


class _FakeStore:
    def __init__(self):
        self._ids = set()

    def add(self, doc_id):
        self._ids.add(doc_id)

    def exists(self, doc_id):
        return doc_id in self._ids


def test_manager_emits_events_to_monitor(tmp_path):
    mgr = LearningQueueManager(
        engine=_FakeEngine(),
        store=QueueStore(str(tmp_path / "q.json")),
        index=KnowledgeIndex(str(tmp_path / "idx.json")),
        knowledge_root=str(tmp_path / "knowledge"),
    )
    mgr.add_urls([f"https://youtu.be/vid{i:05d}aaa" for i in range(3)])

    monitor = LearningMonitor(clock=_Clock())
    kinds: list[str] = []

    def sink(event):
        kinds.append(f"{event.kind}:{event.stage}")
        monitor.handle(event)

    mgr.process_all(on_event=sink)
    assert "STARTED:queue" in kinds and "FINISHED:queue" in kinds
    assert "STARTED:item" in kinds
    assert any(k == "PROGRESS:analyzing" for k in kinds)   # eventos del orquestador (vía job)
    assert monitor.state.global_percent == 1.0
    assert monitor.state.finished is True
