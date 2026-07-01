"""Tests del Documentary Learning Monitor / Dashboard (DLM-001) — deterministas."""

import json
import os

from app.dle.monitor.events import FAILED, FINISHED, PROGRESS, STARTED, ProgressEvent
from app.dlm.models import HealthStatus
from app.dlm.monitor import DashboardMonitor
from app.dlm.persistence import session_statistics, write_outputs
from app.dlm.renderer import ProgressBar, render_dashboard, supports_ansi
from app.dlm.statistics import ETAEstimator, SpeedEstimator, ThroughputCalculator


class _Clock:
    """Reloj inyectable determinista (avanza un paso fijo por lectura)."""

    def __init__(self, step=1.0):
        self.t = 0.0
        self.step = step

    def __call__(self):
        v = self.t
        self.t += self.step
        return v


def _stream(monitor, n=2, shots=10, scenes=4):
    """Simula una cola de ``n`` documentales con sus etapas."""
    monitor.handle(ProgressEvent(kind=STARTED, stage="queue", total=n))
    for i in range(n):
        doc = f"doc_{i}"
        monitor.handle(ProgressEvent(kind=STARTED, stage="item", position=i + 1,
                                     total=n, doc_ref=f"https://y/{i}", doc_id=doc))
        for st in ("downloading", "analyzing", "learning", "storing"):
            monitor.handle(ProgressEvent(kind=STARTED, stage=st, doc_id=doc))
        monitor.handle(ProgressEvent(kind=FINISHED, stage="item", doc_id=doc,
                                     shot_total=shots, scene_total=scenes,
                                     metrics={"documentaries_learned": i + 1,
                                              "hours_learned": (i + 1) * 0.5,
                                              "kb_size_bytes": (i + 1) * 4096}))
    monitor.handle(ProgressEvent(kind=FINISHED, stage="queue", total=n))


# --- determinismo ------------------------------------------------------------

def test_dashboard_is_deterministic():
    a = DashboardMonitor(clock=_Clock())
    b = DashboardMonitor(clock=_Clock())
    _stream(a); _stream(b)
    assert a.snapshot().to_dict() == b.snapshot().to_dict()


def test_render_is_deterministic():
    m = DashboardMonitor(clock=_Clock())
    _stream(m)
    assert render_dashboard(m.snapshot()) == render_dashboard(m.snapshot())


# --- ETA / throughput reproducibles ------------------------------------------

def test_eta_estimator():
    assert ETAEstimator.remaining(10.0, 0.5) == 10.0
    assert ETAEstimator.remaining(10.0, 0.0) == 0.0
    assert ETAEstimator.queue_eta(60.0, 2, 10) == 240.0


def test_throughput_calculator():
    assert ThroughputCalculator.per_hour(10, 3600) == 10.0
    assert ThroughputCalculator.per_minute(120, 60) == 120.0
    assert ThroughputCalculator.mb_per_hour(1024 * 1024 * 5, 3600) == 5.0


def test_speed_estimator_instant():
    s = SpeedEstimator()
    s.record_completion(10.0)
    s.record_completion(13.0)
    assert s.last_item_seconds == 3.0
    assert SpeedEstimator.average_item_seconds(20.0, 4) == 5.0


# --- health states (nunca ambiguos) ------------------------------------------

def test_health_states_progress_with_stage():
    m = DashboardMonitor(clock=_Clock())
    m.handle(ProgressEvent(kind=STARTED, stage="queue", total=1))
    m.handle(ProgressEvent(kind=STARTED, stage="item", position=1, total=1, doc_id="d"))
    m.handle(ProgressEvent(kind=STARTED, stage="analyzing", doc_id="d"))
    health = {e.name: e.status for e in m.snapshot().engines}
    assert health["Downloader"] == HealthStatus.FINISHED        # etapa anterior
    assert health["Scene Detection"] == HealthStatus.RUNNING    # etapa actual
    assert health["Embeddings"] == HealthStatus.WAITING         # etapa posterior
    allowed = vars(HealthStatus).values()
    assert all(e.status in allowed for e in m.snapshot().engines)  # nunca ambiguo


def test_health_failed_marks_current_stage():
    m = DashboardMonitor(clock=_Clock())
    m.handle(ProgressEvent(kind=STARTED, stage="queue", total=1))
    m.handle(ProgressEvent(kind=STARTED, stage="item", position=1, total=1, doc_id="d"))
    m.handle(ProgressEvent(kind=STARTED, stage="downloading", doc_id="d"))
    m.handle(ProgressEvent(kind=FAILED, stage="item", doc_id="d", error="boom"))
    health = {e.name: e.status for e in m.snapshot().engines}
    assert health["Downloader"] == HealthStatus.FAILED
    assert m.snapshot().errors == ["boom"]


def test_finished_marks_all_engines_finished():
    m = DashboardMonitor(clock=_Clock())
    _stream(m, n=1)
    assert all(e.status == HealthStatus.FINISHED for e in m.snapshot().engines)
    assert m.snapshot().finished is True


# --- progreso / contadores ---------------------------------------------------

def test_counters_and_progress(tmp_path):
    # knowledge_root aislado (sin learning_statistics.json) -> corpus desde metrics.
    m = DashboardMonitor(clock=_Clock(), knowledge_root=str(tmp_path / "knowledge"))
    _stream(m, n=3, shots=12, scenes=5)
    st = m.snapshot()
    assert st.globals.completed == 3
    assert st.globals.global_percent == 1.0
    assert st.corpus.documentaries == 3            # de metrics
    assert st.globals.shots_per_minute >= 0.0


# --- render ANSI vs fallback -------------------------------------------------

def test_render_contains_sections():
    m = DashboardMonitor(clock=_Clock())
    _stream(m, n=1)
    text = render_dashboard(m.snapshot())
    for section in ("DOCUMENTARY AI", "Corpus", "Cola", "Progreso", "Estado de motores",
                    "Throughput", "Errores", "Learning Finished"):
        assert section in text
    assert "█" in text or "░" in text              # barra de progreso


def test_progress_bar_bounds():
    assert ProgressBar.render(0.0, 10) == "░" * 10
    assert ProgressBar.render(1.0, 10) == "█" * 10
    assert len(ProgressBar.render(0.5, 10)) == 10


def test_supports_ansi_fallback_for_non_tty():
    class _NoTTY:
        def isatty(self):
            return False
    assert supports_ansi(_NoTTY()) is False         # fallback limpio


# --- estadísticas del vídeo desde knowledge/ (artefacto público) -------------

def test_reads_video_stats_from_public_artifact(tmp_path):
    doc_dir = tmp_path / "knowledge" / "documentaries" / "doc_0"
    doc_dir.mkdir(parents=True)
    (doc_dir / "statistics.json").write_text(json.dumps({
        "average_shot_length": 2.5, "cuts_per_minute": 24.0,
        "movement_distribution": {"subtle": 8, "dynamic": 2},
        "color_temperature_distribution": {"warm": 6, "neutral": 4},
        "time_with_audio": 20.0, "time_with_narration": 12.0,
    }), encoding="utf-8")
    m = DashboardMonitor(clock=_Clock(), knowledge_root=str(tmp_path / "knowledge"))
    _stream(m, n=1)
    cur = m.snapshot().current
    assert cur.avg_shot_length == 2.5 and cur.cuts_per_minute == 24.0
    assert cur.dominant_movement == "subtle" and cur.dominant_color_temperature == "warm"


# --- persistencia ------------------------------------------------------------

def test_persistence_writes_history_and_session(tmp_path):
    m = DashboardMonitor(clock=_Clock())
    _stream(m, n=2)
    paths = write_outputs(str(tmp_path / "knowledge"), m.snapshot(),
                          started_at=100.0, finished_at=200.0)
    assert os.path.exists(paths["history"]) and os.path.exists(paths["session"])
    session = json.loads(open(paths["session"], encoding="utf-8").read())
    assert session["documentaries_learned"] == 2
    # history es acumulativo: una segunda sesión añade, no sobreescribe
    write_outputs(str(tmp_path / "knowledge"), m.snapshot())
    hist = json.loads(open(paths["history"], encoding="utf-8").read())
    assert len(hist["sessions"]) == 2


def test_session_statistics_shape():
    m = DashboardMonitor(clock=_Clock())
    _stream(m, n=1)
    s = session_statistics(m.snapshot())
    for key in ("duration_seconds", "documentaries_learned", "hours_video", "shots",
                "scenes", "videos_per_hour", "knowledge_bytes", "errors"):
        assert key in s


# --- integración real con Queue + DLE (motor falso, sin red) -----------------

def test_integration_with_queue_emits_dashboard(tmp_path):
    from app.dle.queue import LearningQueueManager
    from app.dle.queue.index import KnowledgeIndex
    from app.dle.queue.store import QueueStore

    # Motor falso que emite eventos públicos como el real.
    class _Engine:
        def __init__(self):
            self.store = _Store()

        def learn(self, *, youtube=None, video=None, force=False, on_stage=None,
                  on_event=None, work_dir=None):
            ref = youtube or video
            if on_event:
                for st in ("downloading", "analyzing", "learning", "storing"):
                    on_event(ProgressEvent(kind=STARTED, stage=st, doc_ref=ref))
            from app.dle.queue.downloader import resolve_source
            doc_id = resolve_source(ref).documentary_id
            self.store.add(doc_id)

            class _K:
                schema_version = "1.0"
            return {"status": "learned", "documentary_id": doc_id, "knowledge": _K()}

    class _Store:
        def __init__(self):
            self._ids = set()

        def add(self, i):
            self._ids.add(i)

        def exists(self, i):
            return i in self._ids

    mgr = LearningQueueManager(engine=_Engine(),
                               store=QueueStore(str(tmp_path / "q.json")),
                               index=KnowledgeIndex(str(tmp_path / "idx.json")),
                               knowledge_root=str(tmp_path / "knowledge"))
    mgr.add_urls([f"https://youtu.be/vid{i:05d}xyz" for i in range(3)])

    monitor = DashboardMonitor(clock=_Clock(), knowledge_root=str(tmp_path / "knowledge"))
    mgr.process_all(on_event=monitor.handle)
    st = monitor.snapshot()
    assert st.finished is True
    assert st.globals.completed == 3
    assert all(e.status == HealthStatus.FINISHED for e in st.engines)
