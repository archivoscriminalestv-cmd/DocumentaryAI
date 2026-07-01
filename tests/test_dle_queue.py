"""Tests del pipeline de aprendizaje por lotes (DLE-002) — deterministas, sin red."""

import os

from app.dle import SCHEMA_VERSION
from app.dle.queue import LearningQueueManager
from app.dle.queue.downloader import resolve_source
from app.dle.queue.index import KnowledgeIndex
from app.dle.queue.models import QueueStatus
from app.dle.queue.store import QueueStore


# --- fuente desacoplada ------------------------------------------------------

def test_resolve_source_youtube_and_unknown(tmp_path):
    yt = resolve_source("https://youtu.be/AbCdEfGhIjk")
    assert yt.kind == "youtube" and yt.documentary_id == "doc_yt_AbCdEfGhIjk"
    assert yt.learn_kwargs == {"youtube": "https://youtu.be/AbCdEfGhIjk"}
    assert resolve_source("https://example.com/not-a-video") is None   # no reconocida


def test_resolve_source_local(tmp_path):
    p = tmp_path / "v.mp4"
    p.write_bytes(b"fake-bytes")
    r = resolve_source(str(p))
    assert r.kind == "local" and r.documentary_id.startswith("doc_")
    assert r.learn_kwargs == {"video": str(p)}


# --- store persistente -------------------------------------------------------

def test_queue_store_persists_and_dedups(tmp_path):
    path = str(tmp_path / "q.json")
    s = QueueStore(path)
    s.add("u1"); s.add("u2"); s.add("u1")     # dedup
    s.save()
    assert len(s.ordered()) == 2
    reloaded = QueueStore(path)               # sobrevive a "reinicio"
    assert [i.url for i in reloaded.ordered()] == ["u1", "u2"]


def test_recover_inflight_resets_to_pending(tmp_path):
    s = QueueStore(str(tmp_path / "q.json"))
    it = s.add("u1")
    it.status = QueueStatus.ANALYZING         # interrumpido a mitad
    s.save()
    reloaded = QueueStore(str(tmp_path / "q.json"))
    assert reloaded.recover_inflight() == 1
    assert reloaded.get("u1").status == QueueStatus.PENDING


# --- índice de conocimiento --------------------------------------------------

def test_index_skip_same_schema(tmp_path):
    idx = KnowledgeIndex(str(tmp_path / "idx.json"))
    idx.record(documentary_id="doc_yt_x", video_id="x", canonical_url="u", schema_version=SCHEMA_VERSION)
    assert idx.should_skip(documentary_id="doc_yt_x") is True
    assert idx.should_skip(video_id="x") is True
    assert idx.should_skip(documentary_id="doc_other") is False


def test_index_relearn_when_older_schema(tmp_path):
    idx = KnowledgeIndex(str(tmp_path / "idx.json"))
    idx.record(documentary_id="doc_old", video_id="o", canonical_url="u", schema_version="0.9")
    assert idx.should_skip(documentary_id="doc_old") is False   # esquema antiguo -> re-aprender


# --- manager con motor FALSO (sin ffmpeg/red) --------------------------------

class _FakeEngine:
    """Motor DLE simulado: aprende deterministamente y respeta el store de conocimiento."""

    def __init__(self, fail_urls=None):
        self.store = _FakeKnowledgeStore()
        self._fail = set(fail_urls or [])
        self.calls = []

    def learn(self, *, youtube=None, video=None, force=False, on_stage=None, work_dir=None,
              on_event=None):
        ref = youtube or video
        self.calls.append(ref)
        if on_stage:
            for st in ("downloading", "analyzing", "learning", "storing"):
                on_stage(st)
        if ref in self._fail:
            return {"status": "error", "errors": [{"message": "boom"}]}
        from app.dle.queue.downloader import resolve_source
        doc_id = resolve_source(ref).documentary_id
        self.store.add(doc_id)

        class _K:
            schema_version = SCHEMA_VERSION
        return {"status": "learned", "documentary_id": doc_id, "knowledge": _K()}


class _FakeKnowledgeStore:
    def __init__(self):
        self._ids = set()

    def add(self, doc_id):
        self._ids.add(doc_id)

    def exists(self, doc_id):
        return doc_id in self._ids


def _mgr(tmp_path, **kw):
    return LearningQueueManager(
        engine=_FakeEngine(**kw),
        store=QueueStore(str(tmp_path / "q.json")),
        index=KnowledgeIndex(str(tmp_path / "idx.json")),
        knowledge_root=str(tmp_path / "knowledge"))


def _yt(n):
    return [f"https://youtu.be/vid{i:05d}aaa" for i in range(n)]


def test_batch_processes_all(tmp_path):
    mgr = _mgr(tmp_path)
    mgr.add_urls(_yt(20))
    result = mgr.process_all()
    s = result["status"]
    assert result["processed"] == 20 and s["documentaries_learned"] == 20 and s["pending"] == 0


def test_never_learns_twice(tmp_path):
    mgr = _mgr(tmp_path)
    mgr.add_urls(_yt(5))
    mgr.process_all()
    calls_first = list(mgr.engine.calls)
    # re-añadir las mismas + procesar otra vez -> 0 nuevas descargas, todas SKIPPED/FINISHED
    mgr.add_urls(_yt(5))
    mgr.process_all()
    assert mgr.engine.calls == calls_first            # no se vuelve a llamar al motor
    assert mgr.status()["pending"] == 0


def test_resume_after_stop(tmp_path):
    mgr = _mgr(tmp_path)
    mgr.add_urls(_yt(10))
    mgr.process_all(limit=4)
    assert mgr.status()["documentaries_learned"] == 4
    # nuevo manager (simula reinicio) sobre la misma cola persistente
    mgr2 = LearningQueueManager(engine=_FakeEngine(),
                                store=QueueStore(str(tmp_path / "q.json")),
                                index=KnowledgeIndex(str(tmp_path / "idx.json")),
                                knowledge_root=str(tmp_path / "knowledge"))
    mgr2.process_all()
    assert mgr2.status()["pending"] == 0 and mgr2.status()["documentaries_learned"] == 10


def test_failed_then_retry(tmp_path):
    bad = "https://youtu.be/badbadbad01"
    mgr = LearningQueueManager(engine=_FakeEngine(fail_urls={bad}),
                               store=QueueStore(str(tmp_path / "q.json")),
                               index=KnowledgeIndex(str(tmp_path / "idx.json")),
                               knowledge_root=str(tmp_path / "knowledge"))
    mgr.add_urls(_yt(2) + [bad])
    mgr.process_all()
    assert mgr.status()["failed"] == 1
    assert mgr.retry() == 1
    mgr.process_all()                                  # sigue fallando (motor falla)
    assert mgr.status()["failed"] == 1                 # registrado, no rompe la cola


def test_pause_stops_processing(tmp_path):
    mgr = _mgr(tmp_path)
    mgr.add_urls(_yt(5))
    mgr.pause()
    result = mgr.process_all()
    assert result["processed"] == 0 and mgr.status()["pending"] == 5
    mgr.resume()
    mgr.process_all()
    assert mgr.status()["pending"] == 0


def test_clear_finished_keeps_pending(tmp_path):
    mgr = _mgr(tmp_path)
    mgr.add_urls(_yt(3))
    mgr.process_all(limit=2)
    removed = mgr.clear_finished()
    assert removed == 2 and mgr.status()["total_in_queue"] == 1


def test_reports_written(tmp_path):
    mgr = _mgr(tmp_path)
    mgr.add_urls(_yt(3))
    result = mgr.process_all()
    for key in ("statistics", "history", "report"):
        assert os.path.exists(result["reports"][key])


def test_cancel_removes_pending(tmp_path):
    mgr = _mgr(tmp_path)
    mgr.add_urls(["https://youtu.be/cancelme01x"])
    assert mgr.cancel("https://youtu.be/cancelme01x") is True
    assert mgr.status()["total_in_queue"] == 0
