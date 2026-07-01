"""Tests del vertical Images + Voice → Video (con compositor falso)."""

import os
import wave

import pytest

from app.application.production_service import ProductionService
from app.domain.narrative import Narrative, NarrativeSegment
from app.domain.video import VideoScene
from app.domain.visual import Storyboard, VisualScene
from app.domain.voice import Voiceover, VoiceClip
from app.infrastructure.memory.repositories import (
    InMemoryFactRepository,
    InMemoryKnowledgeRepository,
    InMemoryNarrativeRepository,
)


class FakeNormalizer:
    """Imita MediaNormalizer: registra (image, audio, duration) por escena."""

    def __init__(self) -> None:
        self.received: list[tuple] = []

    def scene_clip(self, image_path, audio_path, duration, clip_path) -> None:
        self.received.append((image_path, audio_path, duration))
        with open(clip_path, "wb") as handle:
            handle.write(b"clip")


class FakeComposer:
    def __init__(self) -> None:
        self.clip_paths: list[str] = []

    def compose(self, clip_paths, out_path: str) -> bool:
        self.clip_paths = list(clip_paths)
        with open(out_path, "wb") as handle:
            handle.write(b"fake mp4")
        return True


def _write_wav(path: str, seconds: float) -> None:
    framerate = 8000
    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(framerate)
        handle.writeframes(b"\x00\x00" * int(framerate * seconds))


def _service(composer, normalizer=None):
    return ProductionService(
        knowledge=InMemoryKnowledgeRepository(),
        facts=InMemoryFactRepository(),
        narratives=InMemoryNarrativeRepository(),
        composer=composer,
        normalizer=normalizer,
    )


def _fixtures(tmp_path):
    narrative = Narrative(
        id="n1",
        research_id="r1",
        knowledge_id="k1",
        title="Doc",
        segments=[
            NarrativeSegment(id="s0", kind="intro", text="Hola mundo intro larga aquí"),
            NarrativeSegment(id="s1", kind="body", text="Cuerpo."),
        ],
    )
    img0 = os.path.join(tmp_path, "i0.png")
    img1 = os.path.join(tmp_path, "i1.png")
    for p in (img0, img1):
        with open(p, "wb") as h:
            h.write(b"png")
    storyboard = Storyboard(
        id="sb",
        narrative_id="n1",
        scenes=[
            VisualScene(segment_id="s0", kind="intro", image_path=img0, rendered=True),
            VisualScene(segment_id="s1", kind="body", image_path=img1, rendered=True),
        ],
    )
    wav0 = os.path.join(tmp_path, "a0.wav")
    _write_wav(wav0, 5.0)
    voiceover = Voiceover(
        id="vo",
        narrative_id="n1",
        clips=[
            VoiceClip(segment_id="s0", kind="intro", audio_path=wav0, synthesized=True),
            VoiceClip(segment_id="s1", kind="body", audio_path="x.txt", synthesized=False),
        ],
    )
    return narrative, storyboard, voiceover


def test_generate_video_aligns_scenes_and_durations(tmp_path):
    composer = FakeComposer()
    normalizer = FakeNormalizer()
    service = _service(composer, normalizer)
    narrative, storyboard, voiceover = _fixtures(tmp_path)

    documentary = service.generate_video(
        narrative, storyboard, voiceover, str(tmp_path)
    )

    assert documentary.rendered
    assert os.path.exists(documentary.video_path)
    assert len(normalizer.received) == 2
    assert len(composer.clip_paths) == 2  # un clip normalizado por escena

    (_, real_audio, real_dur), (_, silent_audio, silent_dur) = normalizer.received
    # Escena con audio real: duración = duración del WAV (5s).
    assert real_audio is not None
    assert abs(real_dur - 5.0) < 0.5
    # Escena degradada: sin audio, duración estimada por nº de palabras (>= mínimo).
    assert silent_audio is None
    assert silent_dur >= 3.0


def test_generate_video_requires_composer(tmp_path):
    service = _service(None, None)
    narrative, storyboard, voiceover = _fixtures(tmp_path)
    with pytest.raises(ValueError):
        service.generate_video(narrative, storyboard, voiceover, str(tmp_path))
