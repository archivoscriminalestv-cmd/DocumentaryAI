"""Tests del Evidence Investigation Planner (EAE-002) — deterministas, sin red."""

import json
import os

from app.eae.planner import (
    CaseProfile,
    EvidenceCategory,
    EvidenceInvestigationPlanner,
    EvidencePriority,
    InvestigationPlan,
    ResearchStage,
)
from app.eae.planner.models import CoverageRequirement
from app.eae.planner.persistence import write_plan


def _profile(**kw):
    base = dict(case_id="case_demo", title="Demo", genre="true_crime", subject="Caso X",
                people=["Ana López", "Juan Pérez"], locations=["Almassora"],
                events=["the arrest"], license_requirements=["CC-BY"])
    base.update(kw)
    return CaseProfile(**base)


# --- estructura del plan -----------------------------------------------------

def test_plan_is_complete():
    plan = EvidenceInvestigationPlanner().plan(_profile())
    assert isinstance(plan, InvestigationPlan)
    assert plan.case_id == "case_demo"
    assert plan.needs and plan.search_tasks and plan.acquisition_tasks
    assert len(plan.search_tasks) == len(plan.needs) == len(plan.acquisition_tasks)
    assert plan.stages == list(ResearchStage.ORDER)
    assert plan.manifest is not None and plan.profile is not None


def test_per_entity_needs_created():
    plan = EvidenceInvestigationPlanner().plan(_profile())
    targets = {n.target for n in plan.needs}
    assert "Ana López" in targets and "Juan Pérez" in targets   # foto por persona
    assert "Almassora" in targets                                # mapa/escena por lugar
    assert "the arrest" in targets                               # noticia por evento
    # true_crime: el lugar genera SCENE_PHOTO crítico
    assert any(n.category == EvidenceCategory.SCENE_PHOTO and n.target == "Almassora"
               for n in plan.needs)


def test_needs_sorted_by_priority():
    plan = EvidenceInvestigationPlanner().plan(_profile())
    ranks = [EvidencePriority.RANK[n.priority] for n in plan.needs]
    assert ranks == sorted(ranks)               # CRITICAL primero
    assert plan.needs[0].priority == EvidencePriority.CRITICAL


# --- minimizar descargas / cobertura -----------------------------------------

def test_acquisition_targets_minimum_not_ideal():
    plan = EvidenceInvestigationPlanner().plan(_profile())
    by_need = {n.id: n for n in plan.needs}
    for task in plan.acquisition_tasks:
        # la adquisición apunta al MÍNIMO (minimiza descargas), no al ideal
        assert task.target_count == by_need[task.need_id].requirement.minimum


def test_coverage_pending_never_invented():
    plan = EvidenceInvestigationPlanner().plan(_profile())
    for n in plan.needs:
        r = n.requirement
        assert r.acquired == 0                  # nada conseguido todavía
        assert r.coverage_percent == 0.0 or r.minimum == 0
        assert r.state in ("PENDING", "COVERED")  # COVERED solo si min==0
    assert plan.coverage_summary["total_acquired"] == 0
    assert plan.coverage_summary["overall_coverage"] == 0.0


def test_coverage_requirement_math():
    req = CoverageRequirement(minimum=2, ideal=5, acquired=0)
    assert req.missing == 2 and req.coverage_percent == 0.0 and req.state == "PENDING"
    req2 = CoverageRequirement(minimum=2, ideal=5, acquired=2)
    assert req2.missing == 0 and req2.coverage_percent == 1.0 and req2.state == "COVERED"


# --- manifest ----------------------------------------------------------------

def test_manifest_describes_project():
    plan = EvidenceInvestigationPlanner().plan(_profile())
    m = plan.manifest
    assert m.people == ["Ana López", "Juan Pérez"] and m.timeline == ["the arrest"]
    assert m.expected_material and m.desired_coverage
    assert m.licenses == ["CC-BY"]
    assert m.acquired_material == [] and m.pending_material   # todo pendiente
    assert m.priority_sources                                  # fuentes sugeridas


def test_genre_changes_plan():
    crime = EvidenceInvestigationPlanner().plan(_profile(genre="true_crime"))
    nature = EvidenceInvestigationPlanner().plan(_profile(genre="nature", locations=[], people=[], events=[]))
    crime_cats = {n.category for n in crime.needs}
    nature_cats = {n.category for n in nature.needs}
    assert EvidenceCategory.COURT_DOCUMENT in crime_cats
    assert EvidenceCategory.SATELLITE in nature_cats
    assert crime_cats != nature_cats


# --- determinismo ------------------------------------------------------------

def test_planner_is_deterministic():
    a = EvidenceInvestigationPlanner().plan(_profile()).to_dict()
    b = EvidenceInvestigationPlanner().plan(_profile()).to_dict()
    assert a == b


# --- persistencia (output/eae/plans, nunca knowledge/) -----------------------

def test_persistence_writes_plan_outside_knowledge(tmp_path):
    plan = EvidenceInvestigationPlanner().plan(_profile())
    out = str(tmp_path / "output" / "eae" / "plans")
    paths = write_plan(plan, out_dir=out)
    assert os.path.exists(paths["plan"]) and paths["plan"].endswith("plan.json")
    data = json.loads(open(paths["plan"], encoding="utf-8").read())
    assert data["case_id"] == "case_demo" and data["needs"]


def test_persistence_refuses_knowledge():
    import pytest
    plan = EvidenceInvestigationPlanner().plan(_profile())
    with pytest.raises(ValueError):
        write_plan(plan, out_dir=os.path.join("knowledge", "eae", "plans"))


# --- sin red / sin azar ------------------------------------------------------

def test_no_network_or_random_imports():
    import importlib
    import pkgutil

    import app.eae.planner as pkg
    forbidden = ("requests", "bs4", "selenium", "playwright", "httpx", "random")
    for mod in pkgutil.iter_modules(pkg.__path__):
        source = importlib.import_module(f"app.eae.planner.{mod.name}")
        for name in forbidden:
            assert name not in getattr(source, "__dict__", {})
