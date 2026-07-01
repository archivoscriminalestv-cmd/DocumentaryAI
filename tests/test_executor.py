"""Tests del Research Executor (ResearchPlan -> SearchTask[]). Sin red, sin IA."""

import json
from dataclasses import asdict

import pytest

from app.application.deterministic_planner import DeterministicPlanner
from app.application.executor_service import ExecutorService
from app.domain.research_plan import ResearchPlan
from app.domain.search import SearchPriority, SearchTask, SearchType


def _plan(topic: str = "The Fermi Paradox") -> ResearchPlan:
    return DeterministicPlanner().create_plan(topic)


def test_execute_returns_search_tasks():
    tasks = ExecutorService().execute(_plan())

    assert tasks and all(isinstance(t, SearchTask) for t in tasks)
    for t in tasks:
        assert t.id and t.query and t.reason
        assert isinstance(t.type, SearchType)
        assert isinstance(t.priority, SearchPriority)


def test_covers_all_example_source_types():
    tasks = ExecutorService().execute(_plan())
    present = {t.type for t in tasks}
    assert present == set(SearchType)  # los 8 tipos de ejemplo aparecen


def test_ids_are_unique_and_sequential():
    tasks = ExecutorService().execute(_plan())
    ids = [t.id for t in tasks]
    assert len(ids) == len(set(ids))
    assert ids[0] == "task-01" and ids[1] == "task-02"


def test_tasks_are_grounded_in_topic_and_plan():
    topic = "MH370"
    plan = _plan(topic)
    tasks = ExecutorService().execute(plan)

    # La búsqueda base de Wikipedia es exactamente el topic.
    wiki = next(t for t in tasks if t.type == SearchType.WIKIPEDIA)
    assert wiki.query == topic and wiki.priority == SearchPriority.HIGH

    # Hay una tarea por subtema (profundización), con el subtema como query.
    for subtopic in plan.subtopics:
        assert any(t.query == subtopic for t in tasks)


def test_execution_is_deterministic():
    plan = _plan()
    a = ExecutorService().execute(plan)
    b = ExecutorService().execute(plan)
    assert [asdict(x) for x in a] == [asdict(x) for x in b]


def test_tasks_are_json_serializable_and_roundtrip():
    tasks = ExecutorService().execute(_plan())

    encoded = json.dumps([asdict(t) for t in tasks], ensure_ascii=False)
    decoded = json.loads(encoded)

    assert isinstance(decoded, list) and len(decoded) == len(tasks)
    # Los enums se serializan como su valor de cadena.
    assert decoded[0]["type"] == "wikipedia"
    assert decoded[0]["priority"] == "high"
    assert set(decoded[0].keys()) == {"id", "type", "query", "priority", "reason"}


def test_empty_topic_plan_raises():
    empty = ResearchPlan(topic="   ")
    with pytest.raises(ValueError):
        ExecutorService().execute(empty)


def test_plan_without_subtopics_still_produces_core_sweep():
    plan = ResearchPlan(topic="Chernobyl")  # sin subtemas ni listas
    tasks = ExecutorService().execute(plan)

    assert len(tasks) == 8  # solo el barrido base por tipo de fuente
    assert {t.type for t in tasks} == set(SearchType)
