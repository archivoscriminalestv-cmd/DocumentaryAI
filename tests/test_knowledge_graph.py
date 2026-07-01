"""Tests del Knowledge Graph Builder (C-06). Determinista, sin red, sin IA."""

import json
from dataclasses import asdict

from app.application.knowledge_service import KnowledgeService
from app.domain.fact.consolidated_fact import ConsolidatedFact
from app.domain.knowledge.knowledge_relation import KnowledgeRelation, RelationshipType


def _fact(id_, statement, source_ids=("src-01",), confidence=0.9) -> ConsolidatedFact:
    return ConsolidatedFact(
        id=id_, statement=statement, confidence=confidence,
        evidence_ids=[f"ev-{id_}"], source_ids=list(source_ids),
    )


def test_temporal_relationship_by_shared_year():
    facts = [
        _fact("f1", "The disaster occurred in 1986"),
        _fact("f2", "Major reforms were announced in 1986"),
    ]
    out = KnowledgeService().build(facts)

    assert len(out) == 1
    assert out[0].relationship_type == RelationshipType.TEMPORAL
    assert out[0].fact_ids == ["f1", "f2"]
    assert "1986" in out[0].statement


def test_causal_relationship_by_marker_and_shared_entity():
    facts = [
        _fact("f1", "The reactor exploded because of a flawed safety test"),
        _fact("f2", "The reactor used an unstable graphite design"),
    ]
    out = KnowledgeService().build(facts)

    assert len(out) == 1
    assert out[0].relationship_type == RelationshipType.CAUSAL
    assert out[0].fact_ids == ["f1", "f2"]


def test_geographical_relationship_by_shared_place():
    facts = [
        _fact("f1", "The power plant operated in Pripyat"),
        _fact("f2", "Thousands of residents lived in Pripyat"),
    ]
    out = KnowledgeService().build(facts)

    assert len(out) == 1
    assert out[0].relationship_type == RelationshipType.GEOGRAPHICAL


def test_hierarchical_relationship_by_marker():
    facts = [
        _fact("f1", "An RBMK reactor is a type of nuclear reactor"),
        _fact("f2", "The nuclear reactor generated electric power"),
    ]
    out = KnowledgeService().build(facts)

    assert len(out) == 1
    assert out[0].relationship_type == RelationshipType.HIERARCHICAL


def test_associative_relationship_by_shared_entity():
    facts = [
        _fact("f1", "The reactor was painted light gray"),
        _fact("f2", "The reactor structure stood very tall"),
    ]
    out = KnowledgeService().build(facts)

    assert len(out) == 1
    assert out[0].relationship_type == RelationshipType.ASSOCIATIVE


def test_unrelated_facts_form_no_knowledge():
    facts = [
        _fact("f1", "Cats are small domestic mammals"),
        _fact("f2", "The ocean floor is extremely deep"),
    ]
    assert KnowledgeService().build(facts) == []


def test_each_knowledge_connects_two_facts_never_all():
    facts = [
        _fact("f1", "The reactor exploded violently overnight"),
        _fact("f2", "The reactor released radioactive material"),
        _fact("f3", "The reactor was sealed in concrete"),
    ]
    out = KnowledgeService().build(facts)

    assert len(out) == 3  # pares: f1-f2, f1-f3, f2-f3 (unidad mínima)
    assert all(len(k.fact_ids) == 2 for k in out)
    assert all(k.fact_ids[0] != k.fact_ids[1] for k in out)


def test_provenance_and_confidence():
    facts = [
        _fact("f1", "The reactor exploded because of human error", source_ids=["src-01"], confidence=0.9),
        _fact("f2", "The reactor lacked a containment building", source_ids=["src-02", "src-01"], confidence=0.7),
    ]
    out = KnowledgeService().build(facts)

    assert out[0].source_ids == ["src-01", "src-02"]  # unión deduplicada
    assert out[0].confidence == 0.7  # mínimo


def test_empty_and_single_input():
    assert KnowledgeService().build([]) == []
    assert KnowledgeService().build(None) == []
    assert KnowledgeService().build([_fact("f1", "Only one fact present here")]) == []


def test_invalid_facts_skipped_safely():
    facts = [
        _fact("f1", "The reactor overheated during the test"),
        None,
        object(),
        _fact("f2", "The reactor overheated and failed quickly"),
    ]
    out = KnowledgeService().build(facts)
    assert len(out) == 1
    assert out[0].fact_ids == ["f1", "f2"]


def test_ids_sequential_and_json_serializable():
    facts = [
        _fact("f1", "The reactor exploded overnight"),
        _fact("f2", "The reactor released radiation"),
    ]
    out = KnowledgeService().build(facts)

    assert out[0].id == "know-01"
    decoded = json.loads(json.dumps([asdict(k) for k in out], ensure_ascii=False))
    assert set(decoded[0].keys()) == {
        "id", "statement", "fact_ids", "source_ids", "relationship_type", "confidence",
    }
    assert decoded[0]["relationship_type"] in {
        "causal", "temporal", "hierarchical", "geographical", "associative",
    }


def test_build_is_deterministic():
    facts = [
        _fact("f1", "The reactor exploded in 1986"),
        _fact("f2", "The reactor failed in 1986"),
        _fact("f3", "The disaster spread across Europe"),
    ]
    a = KnowledgeService().build(facts)
    b = KnowledgeService().build(facts)
    assert [asdict(x) for x in a] == [asdict(x) for x in b]
