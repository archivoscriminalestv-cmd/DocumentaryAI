"""Tests del vertical Voice → Images."""

import os

import pytest

from app.application.production_service import ProductionService
from app.domain.narrative import Narrative, NarrativeSegment
from app.infrastructure.memory.repositories import (
    InMemoryFactRepository,
    InMemoryKnowledgeRepository,
    InMemoryNarrativeRepository,
)
from app.infrastructure.visual import CardImageRenderer


def _narrative() -> Narrative:
    return Narrative(
        id="n1",
        research_id="r1",
        knowledge_id="k1",
        title="Doc",
        segments=[
            NarrativeSegment(id="s0", kind="intro", text="Introducción del caso."),
            NarrativeSegment(id="s1", kind="body", text="Cuerpo con hechos.", fact_ids=["f1"]),
            NarrativeSegment(id="s2", kind="outro", text="Cierre del documental."),
        ],
    )


def _service(renderer):
    return ProductionService(
        knowledge=InMemoryKnowledgeRepository(),
        facts=InMemoryFactRepository(),
        narratives=InMemoryNarrativeRepository(),
        renderer=renderer,
    )


def test_storyboard_renders_one_image_per_segment(tmp_path):
    service = _service(CardImageRenderer())

    storyboard = service.generate_storyboard(_narrative(), str(tmp_path))

    assert len(storyboard.scenes) == 3
    assert all(scene.rendered for scene in storyboard.scenes)
    assert [s.segment_id for s in storyboard.scenes] == ["s0", "s1", "s2"]
    for scene in storyboard.scenes:
        assert os.path.exists(scene.image_path)
        assert scene.image_path.endswith(".png")
        assert os.path.getsize(scene.image_path) > 0


def test_storyboard_requires_renderer(tmp_path):
    service = _service(None)
    with pytest.raises(ValueError):
        service.generate_storyboard(_narrative(), str(tmp_path))
