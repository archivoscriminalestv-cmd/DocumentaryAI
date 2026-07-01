"""Tests de DocumentaryAI Studio (DAS-001) — servicios (sin Qt) + arranque de UI (importorskip).

Studio no contiene lógica de negocio: los tests verifican que ORQUESTA correctamente (usa el
flujo existente queue_add, detecta si learn_queue ya corre, no lanza dos, y lee el estado ya
existente sin recalcular). Todo con dependencias inyectadas: nunca se lanza un proceso real.
"""

import json
import os

import subprocess

from app.studio import config
from app.studio.services import LearningService, LogTail, StatusService
from app.studio.services.learning_service import win_creationflags, win_startupinfo
from app.studio.services.models import LearningState, StatusSnapshot

_CREATE_NO_WINDOW = 0x08000000
_DETACHED_PROCESS = 0x00000008


# --- config ------------------------------------------------------------------

def test_config_paths_resolve():
    assert os.path.isdir(os.path.join(config.project_root(), "app"))
    assert config.stats_path().endswith(os.path.join("knowledge", "learning_statistics.json"))
    assert config.queue_path().endswith(os.path.join("knowledge", "learning_queue.json"))
    assert config.lock_path().endswith(os.path.join("output", "studio", "learning.lock"))


# --- models ------------------------------------------------------------------

def test_indicator_label():
    assert StatusSnapshot(learning=True).indicator_label == "🟢 Modo Aprendizaje"
    assert StatusSnapshot(learning=False).indicator_label == "⚪ Inactivo"


# --- add_urls delega en el flujo existente -----------------------------------

def test_add_urls_uses_existing_queue_add(tmp_path):
    captured = {}
    def fake_run(args, show_environment=True):
        captured["args"] = args
        captured["show_environment"] = show_environment
        return {"found": 128, "added": 31, "duplicates": 97, "invalid": 0}
    ls = LearningService(str(tmp_path), queue_add_run=fake_run, probe=lambda: [])
    res = ls.add_urls("datasets/youtube/truecrime_urls.txt")
    assert res.ok and res.found == 128 and res.added == 31 and res.duplicates == 97
    assert captured["args"] == ["datasets/youtube/truecrime_urls.txt"]
    assert captured["show_environment"] is False        # no reimprime el entorno


def test_add_urls_handles_errors(tmp_path):
    def boom(args, show_environment=True):
        raise RuntimeError("fallo del parser")
    ls = LearningService(str(tmp_path), queue_add_run=boom, probe=lambda: [])
    res = ls.add_urls("x.txt")
    assert res.ok is False and "fallo del parser" in res.error


# --- detección de estado -----------------------------------------------------

def test_is_learning_idle(tmp_path):
    ls = LearningService(str(tmp_path), probe=lambda: [])
    assert ls.is_learning() is False
    assert ls.learning_state().source == "none"


def test_start_learning_launches_once(tmp_path):
    calls = []
    def spawn(cmd, cwd, log):
        calls.append(cmd)
        return os.getpid()                              # PID vivo → aparece como "aprendiendo"
    ls = LearningService(str(tmp_path), spawn=spawn, probe=lambda: [], clock=lambda: 100.0)
    r1 = ls.start_learning()
    assert r1.started and not r1.already_running and r1.state.source == "studio"
    assert len(calls) == 1
    assert ls.is_learning() is True
    # el segundo intento NO lanza otro proceso
    r2 = ls.start_learning()
    assert r2.started is False and r2.already_running is True
    assert len(calls) == 1
    assert os.path.exists(config.lock_path(str(tmp_path)))


def test_stale_lock_is_cleared(tmp_path):
    ls = LearningService(str(tmp_path), probe=lambda: [])
    ls._write_lock({"pid": 999999, "started_at": 0.0, "source": "studio"})   # PID muerto
    assert ls.is_learning() is False
    assert not os.path.exists(config.lock_path(str(tmp_path)))                # lock obsoleto limpiado


def test_external_learn_queue_detected(tmp_path):
    ls = LearningService(str(tmp_path), probe=lambda: [4321])                 # arrancado fuera de Studio
    state = ls.learning_state()
    assert state.running is True and state.source == "external" and state.pid == 4321


def test_runtime_seconds_from_lock(tmp_path):
    ls = LearningService(str(tmp_path), probe=lambda: [], clock=lambda: 500.0)
    ls._write_lock({"pid": os.getpid(), "started_at": 440.0, "source": "studio"})
    state = ls.learning_state()
    assert state.running and state.runtime_seconds == 60


# --- StatusService: lee lo existente, nunca recalcula ------------------------

class _FakeLearning:
    def __init__(self, state):
        self._state = state
    def learning_state(self):
        return self._state


def _seed_knowledge(root):
    kdir = os.path.join(root, "knowledge")
    os.makedirs(kdir, exist_ok=True)
    with open(os.path.join(kdir, "learning_statistics.json"), "w", encoding="utf-8") as h:
        json.dump({"documentaries_learned": 97, "shots_analyzed": 31884, "scenes": 27402,
                   "hours_learned": 49.088, "pending": 31, "failed": 3, "skipped": 1}, h)
    with open(os.path.join(kdir, "learning_queue.json"), "w", encoding="utf-8") as h:
        json.dump({"items": [
            {"url": "https://youtu.be/aaa", "status": "FINISHED", "video_id": "aaa"},
            {"url": "https://youtu.be/bbb", "status": "DOWNLOADING", "video_id": "bbb"},
            {"url": "https://youtu.be/ccc", "status": "PENDING", "video_id": "ccc"},
        ]}, h)


def test_status_snapshot_reads_existing_data(tmp_path):
    root = str(tmp_path)
    _seed_knowledge(root)
    fake = _FakeLearning(LearningState(running=True, source="studio", runtime_seconds=42))
    snap = StatusService(root, learning_service=fake).snapshot()
    assert snap.learned == 97 and snap.shots_analyzed == 31884 and snap.scenes == 27402
    assert snap.hours_learned == 49.088 and snap.pending == 31 and snap.failed == 3
    assert snap.current_video == "bbb"                  # el ítem DOWNLOADING (en curso)
    assert snap.learning is True and snap.runtime_seconds == 42
    assert snap.indicator_label == "🟢 Modo Aprendizaje"


def test_status_snapshot_no_current_video_when_idle(tmp_path):
    root = str(tmp_path)
    _seed_knowledge(root)
    # sin ítems en vuelo
    with open(config.queue_path(root), "w", encoding="utf-8") as h:
        json.dump({"items": [{"url": "x", "status": "PENDING"}]}, h)
    fake = _FakeLearning(LearningState(running=False, source="none"))
    snap = StatusService(root, learning_service=fake).snapshot()
    assert snap.current_video == "" and snap.learning is False


def test_status_snapshot_missing_files_is_safe(tmp_path):
    fake = _FakeLearning(LearningState(running=False))
    snap = StatusService(str(tmp_path), learning_service=fake).snapshot()
    assert snap.learned == 0 and snap.current_video == ""   # sin knowledge → ceros, nunca peta


# --- Studio no arrastra Qt ni motores pesados en los servicios ---------------

def test_services_are_qt_free():
    import importlib
    import pkgutil

    import app.studio.services as pkg
    forbidden = ("PySide6", "torch", "whisper")
    for mod in pkgutil.walk_packages(pkg.__path__, prefix="app.studio.services."):
        source = importlib.import_module(mod.name)
        for name in forbidden:
            assert name not in getattr(source, "__dict__", {}), f"{mod.name} importa {name}"


# --- DAS-001A: flags de proceso invisible (causa raíz del bug) ---------------

def test_creationflags_no_window_without_detached():
    flags = win_creationflags()
    if os.name == "nt":
        # el fix: CREATE_NO_WINDOW presente y DETACHED_PROCESS AUSENTE
        assert flags & _CREATE_NO_WINDOW
        assert not (flags & _DETACHED_PROCESS), "DETACHED_PROCESS reintroduce el bug de ventanas"
    else:
        assert flags == 0


def test_startupinfo_hidden():
    si = win_startupinfo()
    if os.name == "nt":
        assert si is not None
        assert si.dwFlags & subprocess.STARTF_USESHOWWINDOW
        assert si.wShowWindow == subprocess.SW_HIDE
    else:
        assert si is None


# --- DAS-001A: LogTail (salida por fichero, mostrada en el Log) ---------------

def test_logtail_reads_incrementally(tmp_path):
    p = tmp_path / "run.log"
    p.write_text("linea1\nlinea2\n", encoding="utf-8")
    tail = LogTail(str(p))
    assert tail.read_new() == ["linea1", "linea2"]
    assert tail.read_new() == []                       # sin novedades
    with open(p, "a", encoding="utf-8") as h:
        h.write("linea3\n")
    assert tail.read_new() == ["linea3"]


def test_logtail_attach_end_skips_backlog(tmp_path):
    p = tmp_path / "run.log"
    p.write_text("viejo1\nviejo2\n", encoding="utf-8")
    tail = LogTail(str(p))
    tail.attach_end()                                  # reconexión: ignora el histórico
    assert tail.read_new() == []
    with open(p, "a", encoding="utf-8") as h:
        h.write("nuevo\n")
    assert tail.read_new() == ["nuevo"]


def test_logtail_handles_truncation(tmp_path):
    p = tmp_path / "run.log"
    p.write_text("a\nb\nc\n", encoding="utf-8")
    tail = LogTail(str(p))
    tail.read_new()
    p.write_text("z\n", encoding="utf-8")              # fichero encogido (rotado)
    assert tail.read_new() == ["z"]                    # reinicia el offset y relee


def test_logtail_missing_file_is_safe(tmp_path):
    assert LogTail(str(tmp_path / "nope.log")).read_new() == []


# --- UI: solo si PySide6 está instalado --------------------------------------

def test_main_window_constructs_if_qt_available():
    import pytest
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from app.studio.services import LearningService, StatusService
    from app.studio.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    fake = _FakeLearning(LearningState(running=False))
    win = MainWindow(learning=LearningService(probe=lambda: []),
                     status=StatusService(learning_service=fake))
    assert win.windowTitle().startswith("DocumentaryAI Studio")
    win.close()
