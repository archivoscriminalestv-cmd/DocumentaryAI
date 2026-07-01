"""Tests del vertical Narrative → Voice (con sintetizador falso, sin SAPI)."""

import os

from app.application.production_service import ProductionService
from app.domain.narrative import Narrative, NarrativeSegment
from app.infrastructure.memory.repositories import (
    InMemoryFactRepository,
    InMemoryKnowledgeRepository,
    InMemoryNarrativeRepository,
)


class FakeSynthesizer:
    """Escribe un WAV de juguete; registra las llamadas recibidas."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def synthesize(self, text: str, out_path: str) -> bool:
        self.calls.append(text)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as handle:
            handle.write(b"RIFF....fake wav....")
        return True


def _narrative() -> Narrative:
    return Narrative(
        id="n1",
        research_id="r1",
        knowledge_id="k1",
        title="Doc",
        segments=[
            NarrativeSegment(id="s0", kind="intro", text="Introducción."),
            NarrativeSegment(id="s1", kind="body", text="Cuerpo.", fact_ids=["f1"]),
            NarrativeSegment(id="s2", kind="outro", text="Cierre."),
        ],
    )


def _service(synth):
    return ProductionService(
        knowledge=InMemoryKnowledgeRepository(),
        facts=InMemoryFactRepository(),
        narratives=InMemoryNarrativeRepository(),
        synthesizer=synth,
    )


def test_voiceover_creates_one_clip_per_segment(tmp_path):
    synth = FakeSynthesizer()
    service = _service(synth)

    voiceover = service.generate_voiceover(_narrative(), str(tmp_path))

    assert len(voiceover.clips) == 3
    assert all(clip.synthesized for clip in voiceover.clips)
    assert synth.calls == ["Introducción.", "Cuerpo.", "Cierre."]
    for clip in voiceover.clips:
        assert os.path.exists(clip.audio_path)
        assert clip.audio_path.endswith(".wav")
    # Trazabilidad guion → audio.
    assert [c.segment_id for c in voiceover.clips] == ["s0", "s1", "s2"]


def test_voiceover_degrades_to_text_without_synthesizer(tmp_path):
    service = _service(None)

    voiceover = service.generate_voiceover(_narrative(), str(tmp_path))

    assert len(voiceover.clips) == 3
    assert all(not clip.synthesized for clip in voiceover.clips)
    for clip in voiceover.clips:
        assert clip.audio_path.endswith(".txt")
        assert os.path.exists(clip.audio_path)
