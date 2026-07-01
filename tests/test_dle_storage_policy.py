"""Tests del ciclo de vida del vídeo / política de almacenamiento (DLE-002A)."""

import os

import pytest

from app.dle.storage_policy import ARCHIVE, STREAM, TEMPORARY, build_storage_policy
from app.dle.storage_policy.archive import ArchiveStoragePolicy
from app.dle.storage_policy.base import is_protected, safe_rmtree
from app.dle.storage_policy.storage_policy import StreamStoragePolicy
from app.dle.storage_policy.temporary import TemporaryStoragePolicy


def _video(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as h:
        h.write(b"\x00\x00\x00\x18ftypmp42fake")


# --- TEMPORARY: borra el vídeo al finalizar ----------------------------------

def test_temporary_deletes_video_on_success(tmp_path):
    pol = TemporaryStoragePolicy(temp_root=str(tmp_path / "cache"))
    captured = {}
    with pol.workspace("https://youtu.be/aaa") as work:
        _video(os.path.join(work, "video.mp4"))
        captured["work"] = work
        assert os.path.exists(os.path.join(work, "video.mp4"))
    assert not os.path.exists(captured["work"])          # workspace eliminado
    assert not os.path.exists(os.path.join(captured["work"], "video.mp4"))


def test_temporary_cleans_on_error(tmp_path):
    pol = TemporaryStoragePolicy(temp_root=str(tmp_path / "cache"))
    work_seen = {}
    with pytest.raises(RuntimeError):
        with pol.workspace("https://youtu.be/bbb") as work:
            _video(os.path.join(work, "video.mp4"))
            work_seen["w"] = work
            raise RuntimeError("fallo de análisis")
    assert not os.path.exists(work_seen["w"])             # limpia igualmente


# --- ARCHIVE: conserva el vídeo ----------------------------------------------

def test_archive_keeps_video(tmp_path):
    pol = ArchiveStoragePolicy(temp_root=str(tmp_path / "cache"),
                               archive_root=str(tmp_path / "archive"))
    with pol.workspace("https://youtu.be/ccc") as work:
        _video(os.path.join(work, "video.mp4"))
        _video(os.path.join(work, "frames", "f.png"))      # temporal a limpiar
    # el vídeo se conserva en el archivo; el workspace temporal se limpia
    assert pol.last_archived and os.path.exists(pol.last_archived[0])
    assert os.path.basename(pol.last_archived[0]) == "video.mp4"


# --- caller-managed work_dir no se toca --------------------------------------

def test_explicit_work_dir_not_deleted(tmp_path):
    pol = TemporaryStoragePolicy(temp_root=str(tmp_path / "cache"))
    mine = tmp_path / "mine"
    mine.mkdir()
    with pol.workspace("ref", work_dir=str(mine)) as work:
        assert work == str(mine)
    assert mine.exists()                                   # gestionado por el caller


# --- seguridad: nunca borrar directorios permanentes -------------------------

def test_never_deletes_protected_dirs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for prot in ("knowledge", "library", "output", "assets"):
        d = tmp_path / prot / "sub"
        d.mkdir(parents=True)
        (d / "keep.txt").write_text("x")
        assert is_protected(str(tmp_path / prot)) is True
        # safe_rmtree se niega aunque se pida explícitamente
        assert safe_rmtree(str(tmp_path / prot), allowed_root=str(tmp_path)) is False
        assert (d / "keep.txt").exists()


def test_safe_rmtree_only_inside_allowed_root(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "f.txt").write_text("x")
    root = tmp_path / "cache"
    inside = root / "ws"
    inside.mkdir(parents=True)
    (inside / "f.txt").write_text("x")
    assert safe_rmtree(str(outside), allowed_root=str(root)) is False   # fuera de root
    assert outside.exists()
    assert safe_rmtree(str(inside), allowed_root=str(root)) is True     # dentro de root
    assert not inside.exists()


# --- factory + modos ---------------------------------------------------------

def test_factory_default_is_temporary(monkeypatch):
    monkeypatch.delenv("LEARNING_STORAGE_MODE", raising=False)
    assert build_storage_policy().mode == TEMPORARY


def test_factory_reads_env(monkeypatch):
    monkeypatch.setenv("LEARNING_STORAGE_MODE", "archive")
    assert build_storage_policy().mode == ARCHIVE


def test_stream_mode_interface_reserved(monkeypatch):
    monkeypatch.setenv("LEARNING_STORAGE_MODE", "STREAM")
    pol = build_storage_policy()
    assert pol.mode == STREAM and isinstance(pol, StreamStoragePolicy)
    with pytest.raises(NotImplementedError):
        with pol.workspace("ref"):
            pass


# --- integración con el motor (sin ffmpeg/red) -------------------------------

class _FakeProbe:
    def __init__(self, frame):
        self.frame = frame

    def probe(self, p):
        return {"duration": 6.0, "width": 1280, "height": 720, "fps": 25.0, "has_audio": False}

    def detect_cuts(self, p, threshold=0.27):
        return [3.0]

    def silence_intervals(self, p):
        return []

    def extract_frame(self, p, t, out):
        return self.frame


class _DownloadingProvider:
    """Proveedor que 'descarga' un vídeo dentro del workspace (como YouTube)."""

    def __init__(self, vid="doc_test"):
        self.vid = vid

    def resolve(self, ref, work):
        path = os.path.join(work, "downloaded.mp4")
        _video(path)
        return {"path": path, "source_type": "youtube", "source_ref": ref, "video_id": self.vid}


def _frame(tmp_path):
    from PIL import Image
    p = tmp_path / "frame.png"
    Image.new("RGB", (160, 90), (90, 90, 90)).save(p)
    return str(p)


def test_engine_temporary_deletes_downloaded_video(tmp_path):
    from app.dle.orchestrator import DocumentaryLearningEngine
    from app.dle.storage.knowledge_store import KnowledgeStore

    eng = DocumentaryLearningEngine(
        probe=_FakeProbe(_frame(tmp_path)),
        store=KnowledgeStore(root=str(tmp_path / "knowledge")),
        youtube_provider=_DownloadingProvider(),
        storage_policy=TemporaryStoragePolicy(temp_root=str(tmp_path / "cache")))
    res = eng.learn(youtube="https://youtu.be/zzz")
    assert res["status"] == "learned"
    # conocimiento permanente presente, vídeo temporal eliminado
    assert os.path.exists(os.path.join(res["doc_dir"], "documentary.json"))
    leftover = list((tmp_path / "cache").rglob("*.mp4")) if (tmp_path / "cache").exists() else []
    assert leftover == []


def test_engine_archive_keeps_downloaded_video(tmp_path):
    from app.dle.orchestrator import DocumentaryLearningEngine
    from app.dle.storage.knowledge_store import KnowledgeStore

    eng = DocumentaryLearningEngine(
        probe=_FakeProbe(_frame(tmp_path)),
        store=KnowledgeStore(root=str(tmp_path / "knowledge")),
        youtube_provider=_DownloadingProvider(),
        storage_policy=ArchiveStoragePolicy(temp_root=str(tmp_path / "cache"),
                                            archive_root=str(tmp_path / "archive")))
    res = eng.learn(youtube="https://youtu.be/zzz")
    assert res["status"] == "learned"
    archived = list((tmp_path / "archive").rglob("*.mp4"))
    assert len(archived) == 1                              # vídeo conservado en el archivo
