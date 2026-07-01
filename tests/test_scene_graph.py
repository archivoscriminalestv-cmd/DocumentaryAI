"""Tests del Scene Graph generator (C-07). Determinista, sin red, sin IA."""

import json
from dataclasses import asdict

from app.application.scene_graph_service import SceneGraphService
from app.domain.knowledge.knowledge_relation import KnowledgeRelation, RelationshipType
from app.domain.narrative.scene import Scene


def _rel(id_, rel_type, fact_ids, statement, source_ids=("src-01",), confidence=0.9):
    return KnowledgeRelation(
        id=id_, statement=statement, fact_ids=list(fact_ids),
        source_ids=list(source_ids), relationship_type=rel_type, confidence=confidence,
    )


def test_connected_relations_cluster_into_one_scene():
    relations = [
        _rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"],
             "[reactor] The reactor failed | An explosion occurred"),
        _rel("know-02", RelationshipType.TEMPORAL, ["f2", "f3"],
             "[1986] An explosion occurred | The event happened in 1986"),
        _rel("know-03", RelationshipType.ASSOCIATIVE, ["f1", "f4"],
             "[reactor] The reactor failed | The reactor is a nuclear system"),
    ]
    scenes = SceneGraphService().build(relations)

    assert len(scenes) == 1  # subgrafo conexo -> una escena (no una por relación)
    assert isinstance(scenes[0], Scene)
    assert scenes[0].fact_ids == ["f1", "f2", "f3", "f4"]  # unión, en orden


def test_disjoint_relations_form_separate_scenes():
    relations = [
        _rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"], "[a] A failed | B occurred"),
        _rel("know-02", RelationshipType.CAUSAL, ["f3", "f4"], "[c] C broke | D followed"),
    ]
    scenes = SceneGraphService().build(relations)
    assert len(scenes) == 2
    assert {fid for s in scenes for fid in s.fact_ids} == {"f1", "f2", "f3", "f4"}


def test_scenes_ordered_causal_before_associative():
    relations = [
        _rel("know-01", RelationshipType.ASSOCIATIVE, ["g1", "g2"],
             "[topic] Some context A | Some context B"),
        _rel("know-02", RelationshipType.CAUSAL, ["f1", "f2"],
             "[reactor] The reactor failed | An explosion occurred"),
    ]
    scenes = SceneGraphService().build(relations)
    assert len(scenes) == 2
    # la escena causal va primero
    assert "f1" in scenes[0].fact_ids and "f2" in scenes[0].fact_ids
    assert "g1" in scenes[1].fact_ids


def test_never_one_scene_per_relation():
    relations = [
        _rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"], "[x] A | B"),
        _rel("know-02", RelationshipType.TEMPORAL, ["f2", "f3"], "[y] B | C"),
        _rel("know-03", RelationshipType.ASSOCIATIVE, ["f3", "f4"], "[z] C | D"),
    ]
    scenes = SceneGraphService().build(relations)
    assert len(scenes) < len(relations)  # 3 relaciones conexas -> 1 escena


def test_isolated_relation_becomes_single_scene():
    scenes = SceneGraphService().build(
        [_rel("know-01", RelationshipType.ASSOCIATIVE, ["f1", "f2"], "[x] A fact | B fact")]
    )
    assert len(scenes) == 1
    assert scenes[0].fact_ids == ["f1", "f2"]


def test_title_describes_relationship():
    relations = [
        _rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"],
             "[reactor] The reactor failed | The reactor exploded"),
        _rel("know-02", RelationshipType.CAUSAL, ["f2", "f3"],
             "[reactor] The reactor exploded | The reactor melted down"),
    ]
    scenes = SceneGraphService().build(relations)
    title = scenes[0].title.lower()
    assert "causal" in title or "chain" in title   # describe la relación
    assert "reactor" in title                       # anclado en el término clave


def test_narration_is_documentary_prose_not_lists():
    relations = [
        _rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"],
             "[reactor] The reactor failed | An explosion occurred"),
    ]
    scenes = SceneGraphService().build(relations)
    narration = scenes[0].narration
    assert "\n" not in narration and "- " not in narration and "•" not in narration
    assert "reactor failed" in narration.lower()           # contenido verbatim
    assert "as a consequence" in narration.lower()         # conector causal


def test_fact_traceability_union_only():
    relations = [
        _rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"], "[x] A | B"),
        _rel("know-02", RelationshipType.TEMPORAL, ["f2", "f3"], "[y] B | C"),
    ]
    scenes = SceneGraphService().build(relations)
    assert sorted(scenes[0].fact_ids) == ["f1", "f2", "f3"]  # solo hechos presentes


def test_empty_input_returns_empty():
    assert SceneGraphService().build([]) == []
    assert SceneGraphService().build(None) == []


def test_invalid_relations_skipped_safely():
    relations = [
        _rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"], "[x] A | B"),
        None,
        object(),
        _rel("know-02", RelationshipType.CAUSAL, [], "[empty] nothing"),  # sin fact_ids
    ]
    scenes = SceneGraphService().build(relations)
    assert len(scenes) == 1
    assert scenes[0].fact_ids == ["f1", "f2"]


def test_output_is_json_serializable():
    scenes = SceneGraphService().build(
        [_rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"], "[x] A | B")]
    )
    decoded = json.loads(json.dumps([asdict(s) for s in scenes], ensure_ascii=False))
    assert set(decoded[0].keys()) == {"id", "title", "narration", "fact_ids"}
    assert decoded[0]["id"] == "scene-01"


def test_build_is_deterministic():
    relations = [
        _rel("know-01", RelationshipType.CAUSAL, ["f1", "f2"], "[reactor] A | B"),
        _rel("know-02", RelationshipType.TEMPORAL, ["f2", "f3"], "[1986] B | C"),
        _rel("know-03", RelationshipType.ASSOCIATIVE, ["g1", "g2"], "[topic] X | Y"),
    ]
    a = SceneGraphService().build(relations)
    b = SceneGraphService().build(relations)
    assert [asdict(x) for x in a] == [asdict(x) for x in b]
