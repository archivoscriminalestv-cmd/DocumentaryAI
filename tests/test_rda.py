"""Tests del Reference Documentary Analyzer (RDA).

Unitarios sobre rasgos sintéticos (sin ffmpeg) + integración real guardada por
disponibilidad de ffmpeg. Solo gramática audiovisual; nada de contenido.
"""

import json
import os
import subprocess

import pytest

from app.rda.analysis import (
    build_profile,
    color_temperature,
    detect_boundaries,
    lighting_tendency,
    movement_tendency,
    pacing_tier,
    saturation_tendency,
    variety_label,
)
from app.rda.library import ReferenceLibrary
from app.rda.models import FrameFeatures


def _frame(t, brightness, sig_value, *, contrast=20.0, warmth=0.0, colorfulness=25.0):
    return FrameFeatures(
        t=t, brightness=brightness, contrast=contrast, warmth=warmth,
        colorfulness=colorfulness, signature=tuple([sig_value] * 64),
    )


def _block(start_t, count, brightness, sig, *, fps=4.0, **kw):
    return [_frame(start_t + i / fps, brightness, sig, **kw) for i in range(count)]


# --- detección de cortes -----------------------------------------------------

def test_detects_hard_cuts_into_shots():
    frames = _block(0.0, 4, 10, 0.0) + _block(1.0, 4, 240, 255.0) + _block(2.0, 4, 120, 120.0)
    spans = detect_boundaries(frames)
    assert spans == [(0, 4), (4, 8), (8, 12)]  # 3 planos


def test_no_cuts_single_shot():
    frames = _block(0.0, 6, 100, 100.0)
    assert detect_boundaries(frames) == [(0, 6)]


def test_empty_frames():
    assert detect_boundaries([]) == []


# --- mapeo a vocabulario cinematográfico (ARCH-VIS-000) ----------------------

def test_vocabulary_mappings():
    assert pacing_tier(1.5) == "very_fast"
    assert pacing_tier(3.0) == "fast"
    assert pacing_tier(5.0) == "moderate"
    assert pacing_tier(8.0) == "slow"
    assert variety_label(0.1, 4.0) == "metronomic"
    assert variety_label(3.0, 4.0) == "varied"
    assert lighting_tendency(40, 70).startswith("low-key")
    assert "high-contrast" in lighting_tendency(40, 70)
    assert lighting_tendency(200, 20) == "high-key flat"
    assert color_temperature(30) == "warm"
    assert color_temperature(-30) == "cool"
    assert color_temperature(0) == "neutral"
    assert saturation_tendency(60) == "vivid"
    assert saturation_tendency(5) == "muted"
    assert movement_tendency(0.1) == "dynamic"
    assert movement_tendency(0.005) == "mostly_static"


# --- construcción del perfil -------------------------------------------------

def test_build_profile_from_synthetic_frames():
    frames = (
        _block(0.0, 4, 10, 0.0, warmth=-30, colorfulness=10)
        + _block(1.0, 4, 240, 255.0, warmth=-30, colorfulness=10)
        + _block(2.0, 4, 120, 120.0, warmth=-30, colorfulness=10)
    )
    p = build_profile("synthetic", "local", frames, sample_fps=4.0,
                      meta={"width": 1920, "height": 1080, "fps": 24.0, "duration": 3.0})

    assert p.shot_count == 3
    assert p.pacing_tier == "very_fast"          # ASL ~1.0s
    assert p.shot_length_variety == "metronomic"  # duraciones iguales
    assert p.aspect_ratio == "16:9"
    assert p.color_temperature == "cool"          # warmth -30
    assert p.saturation_tendency == "muted"       # colorfulness 10
    assert p.grammar_notes and p.spec_alignment   # conocimiento para la spec
    assert len(p.shots) == 3


def test_profile_is_json_serializable():
    from dataclasses import asdict
    frames = _block(0.0, 4, 100, 100.0) + _block(1.0, 4, 100, 10.0)
    p = build_profile("ref", "local", frames, sample_fps=4.0)
    decoded = json.loads(json.dumps(asdict(p), ensure_ascii=False))
    assert decoded["shot_count"] == 2
    assert "pacing_tier" in decoded and "lighting_tendency" in decoded


def test_library_saves_and_lists(tmp_path):
    frames = _block(0.0, 4, 100, 100.0)
    p = build_profile("my-ref", "local", frames, sample_fps=4.0)
    lib = ReferenceLibrary(base_dir=str(tmp_path))
    path = lib.save(p)
    assert os.path.exists(path)
    assert path in lib.list_profiles()
    assert lib.load(path)["reference"] == "my-ref"


# --- integración REAL con ffmpeg (vídeo sintético) ---------------------------

def test_real_analysis_of_synthetic_video(tmp_path):
    try:
        import imageio_ffmpeg
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"ffmpeg no disponible: {exc}")
    exe = imageio_ffmpeg.get_ffmpeg_exe()

    video = str(tmp_path / "ref.mp4")
    cmd = [
        exe, "-y",
        "-f", "lavfi", "-i", "color=c=black:s=128x72:r=10:d=1.5",
        "-f", "lavfi", "-i", "color=c=white:s=128x72:r=10:d=1.5",
        "-f", "lavfi", "-i", "color=c=red:s=128x72:r=10:d=1.5",
        "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
        "-map", "[v]", "-pix_fmt", "yuv420p", video,
    ]
    if subprocess.run(cmd, capture_output=True).returncode != 0 or not os.path.exists(video):
        pytest.skip("no se pudo generar el vídeo sintético")

    from app.rda.analyzer import ReferenceDocumentaryAnalyzer

    analyzer = ReferenceDocumentaryAnalyzer(library=ReferenceLibrary(base_dir=str(tmp_path / "lib")))
    profile = analyzer.analyze(video)

    # 3 segmentos -> ~3 planos (tolerancia por muestreo en los límites).
    assert 2 <= profile.shot_count <= 4
    assert profile.duration > 3.0
    brights = [s.brightness for s in profile.shots]
    assert min(brights) < 60 and max(brights) > 180   # negro vs blanco detectados
    assert profile.grammar_notes
    # se guardó como conocimiento reutilizable
    assert any(p.endswith(".json") for p in ReferenceLibrary(base_dir=str(tmp_path / "lib")).list_profiles())
