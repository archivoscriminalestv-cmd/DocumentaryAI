"""Tests del Narrative Engine (Facts -> Scenes) con un LLM falso (sin red)."""

import json

from app.application.narrative_engine import NARRATIVE_PROMPT, NarrativeEngine
from app.domain.fact import Fact


class FakeLLM:
    """Devuelve una respuesta fija; registra el system/user recibidos."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.system: str | None = None
        self.user: str | None = None

    def complete(self, system: str, user: str) -> str:
        self.system = system
        self.user = user
        return self.response


def _facts(n: int) -> list[Fact]:
    return [Fact(id=f"f{i}", evidence_id=f"e{i}", text=f"hecho {i}") for i in range(n)]


def test_generates_scenes_with_traceability():
    facts = _facts(3)
    payload = json.dumps({
        "scenes": [
            {"id": "s1", "title": "Hook", "narration": "Intro.", "fact_ids": ["f0", "f1"]},
            {"id": "s2", "title": "Insight", "narration": "Mid.", "fact_ids": ["f2"]},
        ]
    })
    engine = NarrativeEngine(llm=FakeLLM(payload))

    scenes = engine.generate(facts)

    assert [s.id for s in scenes] == ["s1", "s2"]
    assert scenes[0].fact_ids == ["f0", "f1"]
    assert scenes[1].title == "Insight"


def test_uses_exact_prompt_and_sends_facts():
    fake = FakeLLM(json.dumps({"scenes": [
        {"id": "s1", "title": "T", "narration": "N", "fact_ids": ["f0"]}
    ]}))
    engine = NarrativeEngine(llm=fake)

    engine.generate(_facts(1))

    assert fake.system == NARRATIVE_PROMPT  # prompt obligatorio, sin alterar
    assert "f0" in fake.user and "hecho 0" in fake.user


def test_does_not_invent_facts_unknown_ids_dropped():
    facts = _facts(2)
    payload = json.dumps({"scenes": [
        {"id": "s1", "title": "T", "narration": "N", "fact_ids": ["f0", "f999"]},
    ]})
    engine = NarrativeEngine(llm=FakeLLM(payload))

    scenes = engine.generate(facts)

    assert scenes[0].fact_ids == ["f0"]  # f999 no existe -> descartado


def test_scene_without_valid_fact_ids_is_dropped():
    facts = _facts(2)
    payload = json.dumps({"scenes": [
        {"id": "s1", "title": "ok", "narration": "N", "fact_ids": ["f1"]},
        {"id": "s2", "title": "huérfana", "narration": "N", "fact_ids": ["zzz"]},
    ]})
    engine = NarrativeEngine(llm=FakeLLM(payload))

    scenes = engine.generate(facts)

    assert [s.id for s in scenes] == ["s1"]


def test_parses_json_wrapped_in_code_fence():
    facts = _facts(1)
    fenced = "```json\n" + json.dumps({"scenes": [
        {"id": "s1", "title": "T", "narration": "N", "fact_ids": ["f0"]}
    ]}) + "\n```"
    engine = NarrativeEngine(llm=FakeLLM(fenced))

    scenes = engine.generate(facts)

    assert len(scenes) == 1 and scenes[0].fact_ids == ["f0"]


def test_empty_facts_returns_no_scenes_without_calling_llm():
    fake = FakeLLM("should not be used")
    engine = NarrativeEngine(llm=fake)

    assert engine.generate([]) == []
    assert fake.system is None  # no se invoca al LLM sin hechos


def test_invalid_json_raises_valueerror():
    engine = NarrativeEngine(llm=FakeLLM("no soy json"))
    try:
        engine.generate(_facts(1))
    except ValueError:
        return
    raise AssertionError("Se esperaba ValueError ante JSON inválido")


def test_prompt_enforces_grounding_grouping_and_arc():
    # La estrategia de prompt (B-07) debe exigir no inventar, agrupar y arco.
    lowered = NARRATIVE_PROMPT.lower()
    assert "must not invent" in lowered
    assert "only use the provided facts" in lowered
    assert "group" in lowered  # agrupar varios hechos por escena
    assert "hook" in lowered and "conclusion" in lowered  # arco narrativo
    assert '"scenes"' in NARRATIVE_PROMPT  # esquema JSON estable


def test_groups_many_facts_into_fewer_scenes():
    # El motor debe soportar varios hechos agrupados en una sola escena.
    facts = _facts(6)
    payload = json.dumps({"scenes": [
        {"id": "s1", "title": "Hook", "narration": "A.", "fact_ids": ["f0", "f1", "f2"]},
        {"id": "s2", "title": "Cierre", "narration": "B.", "fact_ids": ["f3", "f4", "f5"]},
    ]})
    engine = NarrativeEngine(llm=FakeLLM(payload))

    scenes = engine.generate(facts)

    assert len(scenes) == 2  # 6 hechos -> 2 escenas (no uno-por-escena)
    assert sum(len(s.fact_ids) for s in scenes) == 6
