"""Tests del Architectural Backlog (DCA-004) — deterministas, sin red, sin IA.

Cubren: carga del documento real, validación, parsing correcto, detección de incoherencias en
documentos mal formados, propuestas de sprint (nunca reescriben el documento) y el cableado por
composición en el DocumentaryChiefArchitect (sin tocar analyzer.py).
"""

import json
import os

import pytest

from app.dca.backlog.loader import BacklogLoader
from app.dca.backlog.models import EntryStatus, HypothesisStatus, Priority, Section
from app.dca.backlog.orchestrator import DEFAULT_BACKLOG_PATH, BacklogOrchestrator
from app.dca.backlog.persistence import write_proposal, write_snapshot
from app.dca.backlog.updater import BacklogUpdater
from app.dca.backlog.validator import BacklogValidator


# --- documento real ----------------------------------------------------------

def test_real_document_loads_and_is_valid():
    orch = BacklogOrchestrator()
    backlog = orch.load()
    assert backlog.vision and "DocumentaryAI" in backlog.vision
    assert len(backlog.entries) >= 17
    issues = orch.validate()
    errors = [i for i in issues if i.level == "ERROR"]
    assert errors == [], f"el documento real tiene errores: {errors}"


def test_real_document_has_required_sections_and_entries():
    backlog = BacklogOrchestrator().load()
    sections = {e.section for e in backlog.entries}
    assert Section.STRATEGIC_PRIORITIES in sections
    assert Section.HYPOTHESES in sections
    assert Section.TECHNICAL_DEBT in sections
    # entradas iniciales obligatorias del sprint
    cie = backlog.get("cie")
    assert cie and cie.status == EntryStatus.PLANNED and cie.priority == Priority.P0
    assert backlog.get("documentary_duration_planner").status == EntryStatus.IDEA
    assert backlog.get("evidence_discovery_expansion").priority == Priority.P0
    assert backlog.get("workspace_asset_policy").priority == Priority.P0
    assert backlog.get("narrative_learning").priority == Priority.P1


def test_hypotheses_have_validation_status():
    backlog = BacklogOrchestrator().load()
    hyps = backlog.by_section(Section.HYPOTHESES)
    assert hyps
    for h in hyps:
        assert h.hypothesis_status in HypothesisStatus.ALL


def test_priorities_present_in_strategic():
    backlog = BacklogOrchestrator().load()
    for e in backlog.by_section(Section.STRATEGIC_PRIORITIES):
        assert e.priority in Priority.ALL


def test_load_is_deterministic():
    a = json.dumps(BacklogOrchestrator().load().to_dict(), sort_keys=True)
    b = json.dumps(BacklogOrchestrator().load().to_dict(), sort_keys=True)
    assert a == b


# --- parser sobre documento mal formado --------------------------------------

_BAD_DOC = """# Backlog

## 1. Vision
Una visión.

## 2. Strategic Priorities

#### Entrada Sin Prioridad
- **id:** `sin_prio`
- **status:** PLANNED
- **description:** cae fuera de cualquier ### P

### P0 — x
#### Estado Invalido
- **id:** `mala`
- **status:** FOO
- **description:** estado no permitido

#### Duplicada A
- **id:** `dup`
- **status:** IDEA
- **description:** una

#### Duplicada B
- **id:** `dup`
- **status:** IDEA
- **description:** otra

## 4. Hypotheses
#### Hipotesis Sin Estado
- **id:** `h_sin`
- **description:** falta hypothesis

## 5. Technical Debt
#### Deuda Con Related Roto
- **id:** `deuda`
- **status:** IDEA
- **related:** `no_existe`
- **description:** referencia colgante

## 6. Completed
#### Mal Completed
- **id:** `malc`
- **status:** PLANNED
- **description:** en Completed pero no COMPLETED
"""


def test_validator_detects_all_defects():
    backlog = BacklogLoader().parse(_BAD_DOC)
    issues = BacklogValidator().validate(backlog)
    msgs = {(i.level, i.entry_id) for i in issues}
    errs = {i.entry_id for i in issues if i.level == "ERROR"}
    assert "sin_prio" in errs                      # strategic sin prioridad
    assert "mala" in errs                          # estado no permitido
    assert "dup" in errs                           # id duplicado
    assert "h_sin" in errs                         # hipótesis sin status
    assert "malc" in errs                          # Completed con estado erróneo
    assert ("WARNING", "deuda") in msgs            # related colgante = aviso


# --- updater: propone, nunca escribe -----------------------------------------

def _backlog():
    return BacklogOrchestrator().load()


def test_review_resolves_existing_entry():
    proposal = BacklogUpdater().propose(_backlog(), {
        "sprint": "TEST-1", "resolved": ["cie"]})
    assert "cie" in proposal.resolved
    ch = next(c for c in proposal.status_changes if c.entry_id == "cie")
    assert ch.to_status == EntryStatus.COMPLETED and ch.accepted


def test_review_unknown_entry_is_error():
    proposal = BacklogUpdater().propose(_backlog(), {
        "sprint": "TEST-2", "resolved": ["does_not_exist"]})
    assert "does_not_exist" not in proposal.resolved
    assert any(i.level == "ERROR" and i.entry_id == "does_not_exist" for i in proposal.issues)


def test_review_invalid_transition_flagged():
    proposal = BacklogUpdater().propose(_backlog(), {
        "sprint": "TEST-3",
        "status_changes": [{"id": "cie", "to": "IDEA"}]})   # PLANNED → IDEA (hacia atrás)
    ch = next(c for c in proposal.status_changes if c.entry_id == "cie")
    assert ch.accepted is False
    assert any(i.level == "WARNING" and i.entry_id == "cie" for i in proposal.issues)


def test_review_registers_new_ideas_and_relations():
    proposal = BacklogUpdater().propose(_backlog(), {
        "sprint": "TEST-4",
        "new_ideas": [{"title": "Brand-new idea", "section": "OPEN_IDEAS"}],
        "related_to_add": [{"id": "cie", "related": ["feedback_youtube"]}]})
    assert any(n.title == "Brand-new idea" for n in proposal.new_ideas)
    assert proposal.related_to_add == [{"id": "cie", "related": ["feedback_youtube"]}]


def test_proposal_requires_manual_approval():
    proposal = BacklogUpdater().propose(_backlog(), {"sprint": "TEST-5", "resolved": ["cie"]})
    assert proposal.to_dict()["requires_manual_approval"] is True


# --- persistencia: nunca el documento humano ni knowledge --------------------

def test_persistence_writes_proposal_to_output(tmp_path):
    proposal = BacklogUpdater().propose(_backlog(), {"sprint": "TEST-6", "resolved": ["cie"]})
    out = str(tmp_path / "output" / "dca" / "backlog")
    paths = write_proposal(proposal, out_dir=out)
    assert os.path.exists(paths["proposal"]) and paths["proposal"].endswith(".json")


def test_persistence_refuses_knowledge_and_roadmap():
    proposal = BacklogUpdater().propose(_backlog(), {"sprint": "TEST-7"})
    with pytest.raises(ValueError):
        write_proposal(proposal, out_dir=os.path.join("knowledge", "x"))
    with pytest.raises(ValueError):
        write_proposal(proposal, out_dir=os.path.join("docs", "roadmap"))
    backlog = _backlog()
    with pytest.raises(ValueError):
        write_snapshot(backlog, out_dir=os.path.join("docs", "roadmap"))


# --- cableado en el DCA (por composición; analyzer.py intacto) ---------------

def test_dca_exposes_backlog_capability():
    from app.dca.orchestrator import DocumentaryChiefArchitect
    dca = DocumentaryChiefArchitect()
    backlog = dca.backlog()
    assert len(backlog.entries) >= 17
    assert dca.validate_backlog() == dca.validate_backlog()        # determinista
    proposal = dca.review_backlog({"sprint": "NAR-001", "resolved": ["cie"]})
    assert proposal.sprint == "NAR-001"
    # el cableado no rompe las capacidades previas del DCA
    assert "engines" in dca.analyze()
    summary = dca.backlog_summary()
    assert summary["counts"]["total"] >= 17


def test_default_path_constant():
    assert DEFAULT_BACKLOG_PATH.endswith(os.path.join("docs", "roadmap", "ARCHITECTURAL-BACKLOG.md"))


# --- sin red / sin azar / sin IA ---------------------------------------------

def test_no_network_random_or_ai_imports():
    import importlib
    import pkgutil

    import app.dca.backlog as pkg
    forbidden = ("requests", "bs4", "selenium", "playwright", "httpx", "random",
                 "openai", "anthropic", "datetime")
    for mod in pkgutil.walk_packages(pkg.__path__, prefix="app.dca.backlog."):
        source = importlib.import_module(mod.name)
        for name in forbidden:
            assert name not in getattr(source, "__dict__", {}), f"{mod.name} importa {name}"
