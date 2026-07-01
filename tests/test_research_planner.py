"""Tests del Research Planner determinista (Sprint C-01). Sin red, sin LLM."""

import json
from dataclasses import asdict

import pytest

from app.application.deterministic_planner import DeterministicPlanner
from app.domain.research_plan import ResearchPlan


def test_create_plan_returns_research_plan_for_topic():
    plan = DeterministicPlanner().create_plan("The Fermi Paradox")

    assert isinstance(plan, ResearchPlan)
    assert plan.topic == "The Fermi Paradox"
    assert "Fermi Paradox" in plan.main_research_question


def test_all_sections_are_populated():
    plan = DeterministicPlanner().create_plan("MH370")

    for section in (
        plan.subtopics,
        plan.historical_context,
        plan.timeline,
        plan.actors,
        plan.geographic_areas,
        plan.scientific_concepts,
        plan.controversies,
        plan.primary_sources,
        plan.secondary_sources,
        plan.suggested_queries,
    ):
        assert isinstance(section, list)
        assert len(section) >= 1


def test_topic_grounds_queries_and_subtopics():
    topic = "The disappearance of Malaysia Airlines Flight MH370"
    plan = DeterministicPlanner().create_plan(topic)

    assert topic in plan.suggested_queries
    assert all(topic in q for q in plan.suggested_queries)
    assert all(topic in s for s in plan.subtopics)


def test_plan_is_deterministic():
    planner = DeterministicPlanner()
    a = planner.create_plan("The Fermi Paradox")
    b = planner.create_plan("The Fermi Paradox")

    assert asdict(a) == asdict(b)


def test_plan_is_json_serializable_and_roundtrips():
    plan = DeterministicPlanner().create_plan("The Fermi Paradox")

    encoded = json.dumps(asdict(plan), ensure_ascii=False)
    decoded = json.loads(encoded)

    assert decoded["topic"] == "The Fermi Paradox"
    assert isinstance(decoded["suggested_queries"], list)


def test_empty_topic_raises():
    planner = DeterministicPlanner()
    for bad in ("", "   "):
        with pytest.raises(ValueError):
            planner.create_plan(bad)


def test_topic_is_trimmed():
    plan = DeterministicPlanner().create_plan("   Chernobyl   ")
    assert plan.topic == "Chernobyl"
