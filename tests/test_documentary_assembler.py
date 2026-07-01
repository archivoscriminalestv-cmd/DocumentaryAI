"""Tests del ensamblador de SECUENCIAS (Shot como unidad de render). Sin red."""

import os
import wave

from PIL import Image

from app.application.documentary_assembler import DocumentaryAssembler, RenderShot
from app.rda.models import CinematicProfile
from app.domain.narrative.scene import Scene


def _png(path: str) -> str:
    Image.new("RGB", (64, 36), (20, 20, 30)).save(path, "PNG")
    return path


def _wav(path: str, seconds: float = 2.0) -> None:
    with wave.open(path, "wb") as h:
        h.setnchannels(1); h.setsampwidth(2); h.setframerate(8000)
        h.writeframes(b"\x00\x00" * int(8000 * seconds))


def _profile(**over) -> CinematicProfile:
    base = dict(
        reference="ref", source_type="local", width=1920, height=1080, aspect_ratio="16:9",
        fps=24.0, duration=60.0, sample_fps=4.0, shot_count=20, avg_shot_length=2.5,
        median_shot_length=2.5, min_shot_length=1.0, max_shot_length=5.0, shot_length_stddev=1.0,
        cuts_per_minute=24.0, pacing_tier="fast", shot_length_variety="varied",
        brightness_mean=60.0, contrast_mean=70.0, lighting_tendency="low-key high-contrast",
        warmth_mean=-20.0, colorfulness_mean=15.0, color_temperature="cool",
        saturation_tendency="muted", motion_mean=0.08, movement_tendency="dynamic",
    )
    base.update(over)
    return CinematicProfile(**base)


class FakeMGL:
    """Genera un PNG real por SHOT (MGL.generate_for_shot)."""

    def __init__(self, tmp):
        self._tmp = str(tmp); os.makedirs(self._tmp, exist_ok=True)
        self.shot_calls = 0

    def generate_for_shot(self, request):
        from app.media.store.models import Asset
        self.shot_calls += 1
        path = _png(os.path.join(self._tmp, f"img{self.shot_calls}.png"))
        return Asset(asset_id=f"a{self.shot_calls}", type="image", prompt=request.prompt,
                     provider="fake", path=path)


class FakeSynth:
    def __init__(self, ok=True):
        self.ok = ok

    def synthesize(self, text, out_path):
        if self.ok:
            _wav(out_path, 3.0)
        return self.ok


class RecordingNormalizer:
    def __init__(self):
        self.clips = []

    def scene_clip(self, image_path, audio_path, duration, out_clip):
        self.clips.append((image_path, audio_path, round(duration, 2)))
        with open(out_clip, "wb") as h:
            h.write(b"clip")
        return out_clip


class FakeComposer:
    def __init__(self):
        self.clip_paths = []

    def compose(self, clips, out_path, intro_clip=None):
        self.clip_paths = list(clips)
        with open(out_path, "wb") as h:
            h.write(b"\x00\x00\x00\x18ftypmp42")


def _scenes(n=2):
    return [Scene(id=f"s{i}", title=f"Topic {i}", narration=f"Narration number {i} for the scene", fact_ids=[]) for i in range(n)]


# --- estructura escena -> múltiples planos preservada hasta el render --------

def test_assembles_multi_shot_sequence(tmp_path):
    mgl = FakeMGL(tmp_path / "imgs")
    normalizer, composer = RecordingNormalizer(), FakeComposer()
    asm = DocumentaryAssembler(mgl, FakeSynth(), normalizer, composer, output_dir=str(tmp_path / "out"))

    result = asm.assemble(_scenes(2), profile=_profile(), topic="X")

    assert result.rendered is True
    assert result.scene_count == 2
    # cada escena tiene VARIOS planos (VIS produce >=5) -> total >> nº escenas
    assert result.shot_count >= 10
    assert mgl.shot_calls == result.shot_count          # un asset por PLANO
    assert len(composer.clip_paths) == result.shot_count  # un clip por PLANO
    # la estructura escena->planos se preserva en el report
    assert len(result.report["scenes"]) == 2
    assert all(s["shot_count"] >= 5 for s in result.report["scenes"])
    assert result.report["scenes"][0]["shots"][0]["lens"]  # metadata de plano presente


def test_narration_is_split_across_shots(tmp_path):
    mgl = FakeMGL(tmp_path / "imgs")
    normalizer = RecordingNormalizer()
    asm = DocumentaryAssembler(mgl, FakeSynth(ok=True), normalizer, FakeComposer(), output_dir=str(tmp_path / "out"))

    asm.assemble(_scenes(1), profile=_profile(), topic="X")

    # cada plano recibe un trozo de audio (no None) -> voz continua por escena
    assert all(audio is not None for (_, audio, _) in normalizer.clips)
    assert len(normalizer.clips) >= 5


def test_silent_when_no_narration(tmp_path):
    mgl = FakeMGL(tmp_path / "imgs")
    normalizer = RecordingNormalizer()
    asm = DocumentaryAssembler(mgl, FakeSynth(ok=False), normalizer, FakeComposer(), output_dir=str(tmp_path / "out"))

    asm.assemble(_scenes(1), profile=_profile(), topic="X")
    assert all(audio is None for (_, audio, _) in normalizer.clips)


def test_graceful_without_ffmpeg(tmp_path):
    mgl = FakeMGL(tmp_path / "imgs")
    asm = DocumentaryAssembler(mgl, FakeSynth(), normalizer=None, composer=None, output_dir=str(tmp_path / "out"))
    result = asm.assemble(_scenes(1), profile=_profile(), topic="X")
    assert result.rendered is False
    assert result.shot_count >= 5   # estructura calculada igualmente


# --- hook Camera Motion: el ShotProcessor recibe cada plano con su motion ----

def test_camera_motion_hook_receives_shots(tmp_path):
    class RecordingProcessor:
        def __init__(self): self.shots = []
        def render(self, shot: RenderShot, out_clip):
            self.shots.append(shot)
            with open(out_clip, "wb") as h: h.write(b"c")
            return out_clip

    processor = RecordingProcessor()
    mgl = FakeMGL(tmp_path / "imgs")
    asm = DocumentaryAssembler(
        mgl, FakeSynth(), RecordingNormalizer(), FakeComposer(),
        shot_processor=processor, output_dir=str(tmp_path / "out"),
    )
    asm.assemble(_scenes(1), profile=_profile(), topic="X")

    assert len(processor.shots) >= 5
    # cada plano lleva su 'motion' (camera move + intensity) para el futuro procesador
    for shot in processor.shots:
        assert "move" in shot.motion and "intensity" in shot.motion
        assert shot.camera_move and shot.lens
