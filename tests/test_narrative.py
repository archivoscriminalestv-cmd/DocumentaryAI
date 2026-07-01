"""Tests del vertical Knowledge → Narrative."""

from app.application.production_service import ProductionService
from app.application.research_service import ResearchService
from app.infrastructure.memory.repositories import (
    InMemoryClaimRepository,
    InMemoryEvidenceRepository,
    InMemoryFactRepository,
    InMemoryKnowledgeRepository,
    InMemoryNarrativeRepository,
    InMemoryResearchRepository,
    InMemorySourceRepository,
    InMemoryWorkspaceRepository,
)


def _build():
    facts = InMemoryFactRepository()
    knowledge = InMemoryKnowledgeRepository()
    narratives = InMemoryNarrativeRepository()
    research = ResearchService(
        workspaces=InMemoryWorkspaceRepository(),
        researches=InMemoryResearchRepository(),
        sources=InMemorySourceRepository(),
        evidences=InMemoryEvidenceRepository(),
        facts=facts,
        claims=InMemoryClaimRepository(),
        knowledge=knowledge,
    )
    production = ProductionService(knowledge=knowledge, facts=facts, narratives=narratives)
    return research, production


def _seed_knowledge(research_svc: ResearchService, lines: list[str]):
    r = research_svc.create_research(title="Caso de prueba")
    research_svc.register_source(r.id, reference="ref", content="\n".join(lines))
    source = research_svc._sources.list_by_research(r.id)[0]
    research_svc.extract_evidence(source.id)
    research_svc.generate_knowledge(r.id)
    return r


def test_generate_narrative_has_intro_body_outro():
    research_svc, production = _build()
    r = _seed_knowledge(research_svc, ["hecho uno", "hecho dos", "hecho tres"])

    narrative = production.generate_narrative(r.id, title="Mi documental")

    kinds = [s.kind for s in narrative.segments]
    assert kinds[0] == "intro"
    assert kinds[-1] == "outro"
    assert "body" in kinds
    assert narrative.title == "Mi documental"
    assert narrative.research_id == r.id


def test_body_segments_keep_fact_provenance():
    research_svc, production = _build()
    r = _seed_knowledge(research_svc, [f"hecho {i}" for i in range(12)])

    narrative = production.generate_narrative(r.id)

    body = [s for s in narrative.segments if s.kind == "body"]
    # Como mucho 5 escenas de cuerpo, y toda escena de cuerpo es trazable.
    assert 1 <= len(body) <= 5
    all_fact_ids = [fid for s in body for fid in s.fact_ids]
    assert len(all_fact_ids) == 12  # cada hecho aparece exactamente una vez


def test_script_concatenates_segments():
    research_svc, production = _build()
    r = _seed_knowledge(research_svc, ["alfa", "beta"])

    narrative = production.generate_narrative(r.id)

    assert narrative.script.count("\n\n") == len(narrative.segments) - 1
    for segment in narrative.segments:
        assert segment.text in narrative.script


def test_generate_narrative_without_knowledge_raises():
    research_svc, production = _build()
    r = research_svc.create_research(title="Vacía")

    try:
        production.generate_narrative(r.id)
    except ValueError:
        return
    raise AssertionError("Se esperaba ValueError sin Knowledge")


def test_narrative_from_scenes_maps_llm_scenes_for_production():
    # B-08: las Scenes del LLM se adaptan al Narrative que consumen Voice/Images/Video.
    from app.domain.narrative.scene import Scene

    _, production = _build()
    scenes = [
        Scene(id="s1", title="El enigma", narration="Texto uno.", fact_ids=["f1", "f2"]),
        Scene(id="s2", title="La respuesta", narration="Texto dos.", fact_ids=["f3"]),
    ]

    narrative = production.narrative_from_scenes(
        research_id="r1", knowledge_id="k1", title="Doc", scenes=scenes
    )

    assert narrative.title == "Doc"
    assert [s.text for s in narrative.segments] == ["Texto uno.", "Texto dos."]
    # El título de escena viaja en kind (subtítulo de imagen) y se preserva fact_ids.
    assert [s.kind for s in narrative.segments] == ["El enigma", "La respuesta"]
    assert narrative.segments[0].fact_ids == ["f1", "f2"]
    # narration concatenada -> script que narra la voz.
    assert "Texto uno." in narrative.script and "Texto dos." in narrative.script
