"""Tests del Documentary Learning Engine (DLE) — deterministas, sin red, sin ffmpeg real."""

import io

import pytest
from PIL import Image

from app.dle import UNKNOWN, DocumentaryLearningEngine
from app.dle.analysis import audio as audio_an
from app.dle.analysis import narration as narration_an
from app.dle.analysis.motion import analyze_motion
from app.dle.analysis.visual_style import analyze_frame
from app.dle.downloader.youtube import DownloadError, YouTubeDownloader, video_id_from_url
from app.dle.ffmpeg import cuts_to_shots, parse_probe, parse_silence
from app.dle.models import Transcript, TranscriptSegment
from app.dle.segmentation.scene_detector import build_narrative_blocks, group_into_scenes
from app.dle.storage.knowledge_store import KnowledgeStore
from app.dle.transcription.whisper import NullTranscriber, WhisperTranscriber


# --- parsers FFmpeg (puros) --------------------------------------------------

def test_parse_probe():
    stderr = ("  Duration: 00:01:18.00, start: 0.0, bitrate: 655 kb/s\n"
              "  Stream #0:0: Video: h264, yuv420p, 1280x720, 455 kb/s, 25 fps, 25 tbr\n"
              "  Stream #0:1: Audio: aac, 44100 Hz, stereo")
    p = parse_probe(stderr)
    assert p == {"duration": 78.0, "width": 1280, "height": 720, "fps": 25.0, "has_audio": True}


def test_parse_silence_and_cuts_to_shots():
    sil = parse_silence("silence_start: 1.0\nsilence_end: 2.0\nsilence_start: 5.0\nsilence_end: 6.0")
    assert sil == [(1.0, 2.0), (5.0, 6.0)]
    shots = cuts_to_shots([3.0, 6.0], 9.0)
    assert shots == [(0.0, 3.0), (3.0, 6.0), (6.0, 9.0)]


def test_cuts_to_shots_handles_no_cuts():
    assert cuts_to_shots([], 10.0) == [(0.0, 10.0)]


# --- análisis visual / movimiento (Pillow, determinista) ---------------------

def _png(color, size=(160, 90)) -> str:
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    Image.new("RGB", size, color).save(path)
    return path


def test_analyze_frame_color_temperature_and_lighting():
    warm = analyze_frame(_png((200, 120, 60)))
    cool = analyze_frame(_png((60, 90, 200)))
    dark = analyze_frame(_png((10, 10, 10)))
    assert warm["color_temperature"] == "warm"
    assert cool["color_temperature"] == "cool"
    assert dark["lighting"] == "low-key" and dark["day_night"] == "night"


def test_analyze_frame_is_deterministic():
    p = _png((123, 80, 40))
    assert analyze_frame(p) == analyze_frame(p)


def test_analyze_motion_static_vs_dynamic():
    a, b = _png((50, 50, 50)), _png((50, 50, 50))
    mag, cat = analyze_motion(a, b)
    assert mag == 0.0 and cat == "static"
    _mag2, cat2 = analyze_motion(_png((0, 0, 0)), _png((255, 255, 255)))
    assert cat2 == "dynamic"


# --- audio / narración -------------------------------------------------------

def test_audio_present_logic():
    assert audio_an.audio_present(0, 3, [], True) == "true"
    assert audio_an.audio_present(0, 3, [(0.0, 5.0)], True) == "false"   # silencio cubre el plano
    assert audio_an.audio_present(0, 3, [(0.0, 1.0)], True) == "true"    # hay sonido tras el silencio
    assert audio_an.audio_present(0, 3, [], False) == "false"           # sin pista de audio
    assert audio_an.music_present() == UNKNOWN                          # no se inventa


def test_narration_present_requires_transcript():
    empty = Transcript(available=False)
    assert narration_an.narration_present(0, 3, empty) == UNKNOWN
    t = Transcript(provider="x", available=True, segments=[TranscriptSegment(1.0, 2.0, "hola")])
    assert narration_an.narration_present(0, 3, t) == "true"
    assert narration_an.narration_present(10, 13, t) == "false"


# --- segmentación ------------------------------------------------------------

def test_scene_grouping_and_narrative_unknown():
    from app.dle.models import ShotAnalysis
    shots = [
        ShotAnalysis(0, 0, 0, 3, 3, dominant_color="blue", color_temperature="cool", brightness=80),
        ShotAnalysis(1, 0, 3, 6, 3, dominant_color="blue", color_temperature="cool", brightness=82),
        ShotAnalysis(2, 0, 6, 9, 3, dominant_color="red", color_temperature="warm", brightness=120),
    ]
    scenes = group_into_scenes(shots)
    assert len(scenes) == 2                       # cambio de color/temperatura abre escena
    assert shots[2].scene_index == 1
    blocks = build_narrative_blocks(shots, 9.0)
    assert all(b.category == UNKNOWN for b in blocks)   # nunca inventa categorías


# --- transcripción inyectable ------------------------------------------------

def test_null_transcriber_unavailable():
    t = NullTranscriber().transcribe("x.mp4")
    assert t.available is False and t.segments == []


def test_whisper_transcriber_graceful_without_backend():
    t = WhisperTranscriber(loader=lambda: None).transcribe("x.mp4")
    assert t.available is False


def test_whisper_transcriber_with_fake_backend():
    class Fake:
        def transcribe(self, path):
            return {"language": "en", "segments": [{"start": 0.0, "end": 1.0, "text": "hi"}]}
    t = WhisperTranscriber(loader=lambda: Fake()).transcribe("x.mp4")
    assert t.available and t.segments[0].text == "hi" and t.language == "en"


# --- downloader inyectable ---------------------------------------------------

def test_video_id_from_url():
    assert video_id_from_url("https://youtu.be/AbCdEfGhIjk") == "AbCdEfGhIjk"


def test_downloader_unavailable_raises():
    dl = YouTubeDownloader(ytdlp=None)         # deshabilitado explícitamente
    assert dl.available() is False
    with pytest.raises(DownloadError):
        dl.download("https://youtube.com/x", "/tmp/x")


def test_downloader_autodetects_module_when_not_on_path(monkeypatch):
    """yt-dlp instalado como módulo pip pero sin ejecutable en PATH (caso Windows)."""
    import sys
    import app.dle.downloader.youtube as y
    monkeypatch.setattr(y.shutil, "which", lambda name: None)         # no en PATH
    monkeypatch.setattr(y.importlib.util, "find_spec", lambda name: object())  # módulo sí
    dl = y.YouTubeDownloader()                 # autodetección
    assert dl.available() is True
    assert dl._cmd[:3] == [sys.executable, "-m", "yt_dlp"]


def test_downloader_explicit_command_list():
    dl = YouTubeDownloader(ytdlp=["python", "-m", "yt_dlp"])
    assert dl.available() is True and dl._cmd == ["python", "-m", "yt_dlp"]


# --- orquestador (probe inyectado, sin ffmpeg/red) ---------------------------

class _FakeProbe:
    def __init__(self, frame, fail_stage=None):
        self.frame, self.fail_stage = frame, fail_stage

    def probe(self, p):
        return {"duration": 9.0, "width": 1280, "height": 720, "fps": 25.0, "has_audio": True}

    def detect_cuts(self, p, threshold=0.27):
        if self.fail_stage == "cuts":
            raise RuntimeError("boom")
        return [3.0, 6.0]

    def silence_intervals(self, p):
        return [(0.0, 1.0)]

    def extract_frame(self, p, t, out):
        return self.frame


class _FakeProvider:
    def __init__(self, vid="doc_test", stype="local"):
        self.vid, self.stype = vid, stype

    def resolve(self, ref, work):
        return {"path": ref, "source_type": self.stype, "source_ref": ref, "video_id": self.vid}


def _engine(tmp_path, frame, **kw):
    return DocumentaryLearningEngine(
        probe=_FakeProbe(frame, **kw), transcriber=NullTranscriber(),
        store=KnowledgeStore(root=str(tmp_path / "knowledge")),
        local_provider=_FakeProvider(), scene_threshold=0.27)


def test_orchestrator_learns_and_persists(tmp_path):
    frame = _png((120, 90, 60))
    res = _engine(tmp_path, frame).learn(video="dummy.mp4")
    assert res["status"] == "learned"
    k = res["knowledge"]
    assert k.statistics.shot_count == 3 and k.statistics.scene_count >= 1
    assert k.statistics.cuts_per_minute > 0
    assert len(k.statistics.embedding) > 0
    # ficheros escritos
    import os
    for name in ("documentary.json", "scenes.json", "shots.json", "statistics.json",
                 "transcript.json", "report.md"):
        assert os.path.exists(os.path.join(res["doc_dir"], name))


def test_orchestrator_is_deterministic(tmp_path):
    frame = _png((100, 70, 50))
    a = _engine(tmp_path, frame).learn(video="d.mp4", force=True)["knowledge"].to_dict()
    b = _engine(tmp_path, frame).learn(video="d.mp4", force=True)["knowledge"].to_dict()
    assert a == b


def test_rerun_does_not_duplicate(tmp_path):
    frame = _png((100, 70, 50))
    eng = _engine(tmp_path, frame)
    first = eng.learn(video="d.mp4")
    second = eng.learn(video="d.mp4")
    assert first["status"] == "learned" and second["status"] == "skipped"
    assert eng.store.list_ids() == ["doc_test"]


def test_failing_stage_does_not_break_pipeline(tmp_path):
    frame = _png((80, 80, 80))
    res = _engine(tmp_path, frame, fail_stage="cuts").learn(video="d.mp4")
    assert res["status"] == "learned"               # no rompe
    k = res["knowledge"]
    assert any(e.stage == "scene_detection" for e in k.errors)   # error registrado
    assert k.statistics.shot_count == 1             # sin cortes -> un plano


def test_provider_agnostic_same_analysis(tmp_path):
    frame = _png((110, 95, 70))
    local = DocumentaryLearningEngine(probe=_FakeProbe(frame), store=KnowledgeStore(root=str(tmp_path / "k1")),
                                      local_provider=_FakeProvider("doc_a", "local"))
    yt = DocumentaryLearningEngine(probe=_FakeProbe(frame), store=KnowledgeStore(root=str(tmp_path / "k2")),
                                   youtube_provider=_FakeProvider("doc_b", "youtube"))
    ka = local.learn(video="x")["knowledge"]
    kb = yt.learn(youtube="https://y")["knowledge"]
    # mismo análisis salvo identidad de la fuente
    assert [s.to_dict() for s in ka.shots] == [s.to_dict() for s in kb.shots]
    assert ka.statistics.to_dict() == kb.statistics.to_dict()


def test_no_random_in_package():
    import importlib, pkgutil
    import app.dle as pkg
    for mod in pkgutil.walk_packages(pkg.__path__, prefix="app.dle."):
        source = importlib.import_module(mod.name)
        assert "random" not in getattr(source, "__dict__", {})
