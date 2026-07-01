"""Tests del Composer (COMP-001).

Los que tocan FFmpeg real se marcan y se omiten si el binario no está; el resto
(construcción de filtros, transiciones, plan de escena, sincronía) son puros.
"""

import os

import pytest

from app.composer import DocumentaryComposer
from app.composer.ffmpeg_motion_executor import build_zoompan
from app.composer.models import ClipResult
from app.composer.runtime import DocumentaryComposer as RT
from app.composer import transitions


def _ffmpeg_available() -> bool:
    try:
        import imageio_ffmpeg
        return bool(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return False


# --- construcción de filtros (pura, determinista) ----------------------------

def test_build_zoompan_push_in_uses_zoom():
    f = build_zoompan("SLOW_PUSH_IN", {"zoom_pct": 12, "easing": "ease_in_out"}, 3.0, 25, 1280, 720)
    assert "zoompan" in f and "s=1280x720" in f and "fps=25" in f


def test_build_zoompan_is_deterministic():
    a = build_zoompan("PAN_RIGHT", {"easing": "ease_in_out"}, 3.0, 25, 1280, 720)
    b = build_zoompan("PAN_RIGHT", {"easing": "ease_in_out"}, 3.0, 25, 1280, 720)
    assert a == b


def test_build_zoompan_supports_all_required_motions():
    required = ["SLOW_PUSH_IN", "SLOW_PULL_OUT", "PAN_LEFT", "PAN_RIGHT", "TILT_UP",
               "TILT_DOWN", "DOLLY_LEFT", "PARALLAX", "LOCKED", "HANDHELD_SUBTLE"]
    for mt in required:
        f = build_zoompan(mt, {"easing": "ease_in_out", "amplitude_deg": 0.4}, 2.0, 25, 1280, 720)
        assert "zoompan" in f


def test_easing_curves_present():
    for easing in ("ease_in", "ease_out", "ease_in_out", "linear"):
        f = build_zoompan("SLOW_PUSH_IN", {"zoom_pct": 10, "easing": easing}, 2.0, 25, 1280, 720)
        assert "zoompan" in f


# --- transiciones ------------------------------------------------------------

def test_transitions_edges_and_dissolve():
    first = transitions.decide(0, 26)
    mid = transitions.decide(10, 26)
    last = transitions.decide(25, 26)
    assert first["transition_in"] == "fade_in" and first["fade_in"] == 1.0
    assert mid["transition_in"] == "dissolve" and mid["transition_out"] == "dissolve"
    assert last["transition_out"] == "fade_out" and last["fade_out"] == 1.0


# --- plan de escena / sincronía (puro) ---------------------------------------

def test_scene_plan_sums_durations():
    clips = [
        ClipResult(0, "s1::a", "s1", "asset_a", "STATIC", 3.0, "fade_in", "dissolve", "c1.mp4"),
        ClipResult(1, "s1::b", "s1", "asset_b", "PAN_LEFT", 3.0, "dissolve", "dissolve", "c2.mp4"),
        ClipResult(2, "s2::a", "s2", "asset_c", "SLOW_PUSH_IN", 4.0, "dissolve", "fade_out", "c3.mp4"),
    ]
    plan = RT._scene_plan(clips, {"s1": "hola", "s2": "mundo"})
    assert plan == [("s1", "hola", 6.0), ("s2", "mundo", 4.0)]
    # la suma del plan de narración = suma de duraciones de vídeo (sincronía)
    assert sum(d for _s, _t, d in plan) == sum(c.duration for c in clips)


# --- FFmpeg real (end-to-end pequeño) ----------------------------------------

@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg no disponible")
def test_executor_renders_clip(tmp_path):
    from PIL import Image
    from app.composer.audio import media_duration
    from app.composer.ffmpeg_motion_executor import FFmpegMotionExecutor

    img = tmp_path / "a.png"
    Image.new("RGB", (1024, 576), (40, 60, 80)).save(img)
    out = tmp_path / "clip.mp4"
    FFmpegMotionExecutor().execute(
        asset_path=str(img), motion_type="SLOW_PUSH_IN",
        parameters={"zoom_pct": 10, "easing": "ease_in_out"}, duration=1.0,
        out_clip=str(out), fade_in=0.2, fade_out=0.2)
    assert out.exists() and out.stat().st_size > 0
    assert abs(media_duration(str(out)) - 1.0) < 0.3


@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg no disponible")
def test_full_compose_two_shots_produces_synced_mp4(tmp_path):
    from PIL import Image
    from app.cme import CinematicMotionEngine, CMEContext

    # dos assets + dos MotionShots reales del CME
    assets = []
    for i, color in enumerate([(30, 40, 50), (60, 50, 40)]):
        p = tmp_path / f"a{i}.png"
        Image.new("RGB", (1024, 576), color).save(p)
        assets.append(str(p))
    cme = CinematicMotionEngine()
    cme.plan_shot(CMEContext(shot_id="s1::a", scene_id="s1", asset_id="asset_a",
                             documentary_style="intimate documentary", shot_role="establishing",
                             shot_duration=1.0))
    cme.plan_shot(CMEContext(shot_id="s1::b", scene_id="s1", asset_id="asset_b",
                             documentary_style="intimate documentary", shot_role="",
                             shot_duration=1.0))
    cme.finalize()

    out_dir = tmp_path / "out"
    comp = DocumentaryComposer(synthesizer=None).run(   # sin narración -> silencio sincronizado
        motion_shots=cme.shots, asset_paths=assets,
        narration_by_scene={"s1": "una breve narración de prueba"},
        output_dir=str(out_dir), project="test")
    assert os.path.exists(comp.output_path) and os.path.getsize(comp.output_path) > 0
    assert os.path.exists(out_dir / "clips" / "clip_001.mp4")
    assert os.path.exists(out_dir / "clips" / "clip_002.mp4")
    assert os.path.exists(out_dir / "composer_manifest.json")
    assert os.path.exists(out_dir / "composer_report.md")
    assert comp.in_sync                                  # audio == video
    assert len(comp.clips) == 2
