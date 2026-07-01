"""Tests del Evidence Correlation Engine (ECE-001) — deterministas, sin red ni IA."""

import json
import os

from app.eae.discovery.models import DiscoveredEvidence, DiscoveryPlan, NeedCoverage
from app.eae.planner.models import (
    CaseProfile,
    CoverageRequirement,
    EvidenceCategory as C,
    EvidenceNeed,
    EvidencePriority as P,
    InvestigationPlan,
)
from app.ece.engine import CaseCorrelationEngine
from app.ece.models import CoverageState, NodeType, RelationType
from app.ece.persistence import write_correlation_outputs

ALLEN, SF, EVENT = "Arthur Leigh Allen", "San Francisco", "1969 attack"


def _plan():
    profile = CaseProfile(case_id="zodiac", title="Zodiac Killer", genre="true_crime",
                          people=[ALLEN], locations=[SF], events=[EVENT])
    needs = [
        EvidenceNeed("need:scene_photo:san_francisco", C.SCENE_PHOTO, P.CRITICAL, SF,
                     CoverageRequirement(minimum=1, ideal=2)),
        EvidenceNeed("need:photo:arthur_leigh_allen", C.PHOTO, P.HIGH, ALLEN,
                     CoverageRequirement(minimum=1, ideal=2)),
        EvidenceNeed("need:court_document:case", C.COURT_DOCUMENT, P.HIGH, "case",
                     CoverageRequirement(minimum=1, ideal=2)),
        EvidenceNeed("need:map:san_francisco", C.MAP, P.MEDIUM, SF,
                     CoverageRequirement(minimum=1, ideal=1)),
    ]
    return InvestigationPlan(case_id="zodiac", profile=profile, needs=needs)


def _discovery():
    ev = [
        DiscoveredEvidence(id="wikimedia_commons:photo_allen",
                           need_id="need:photo:arthur_leigh_allen", target=ALLEN, category=C.PHOTO,
                           title="Arthur Leigh Allen portrait", provider="wikimedia_commons",
                           date="1968-05-01"),
        DiscoveredEvidence(id="openstreetmap:sf", need_id="need:map:san_francisco", target=SF,
                           category=C.MAP, title="San Francisco", provider="openstreetmap"),
        DiscoveredEvidence(id="wikipedia:scene1", need_id="need:scene_photo:san_francisco",
                           target=SF, category=C.SCENE_PHOTO, provider="wikipedia",
                           title="Scene report mentions Arthur Leigh Allen", date="1969-07-04"),
        DiscoveredEvidence(id="news:scene2", need_id="need:scene_photo:san_francisco",
                           target=SF, category=C.SCENE_PHOTO, provider="news",
                           title="Another scene report", date="1969-08-01"),  # fecha en conflicto
    ]
    needs = [
        NeedCoverage("need:scene_photo:san_francisco", C.SCENE_PHOTO, SF, P.CRITICAL,
                     minimum=1, discovered=2, state="COVERED",
                     evidence_ids=["wikipedia:scene1", "news:scene2"]),
        NeedCoverage("need:photo:arthur_leigh_allen", C.PHOTO, ALLEN, P.HIGH, minimum=1,
                     discovered=1, state="COVERED", evidence_ids=["wikimedia_commons:photo_allen"]),
        NeedCoverage("need:court_document:case", C.COURT_DOCUMENT, "case", P.HIGH, minimum=1,
                     discovered=0, state="PENDING", evidence_ids=[]),
        NeedCoverage("need:map:san_francisco", C.MAP, SF, P.MEDIUM, minimum=1, discovered=1,
                     state="COVERED", evidence_ids=["openstreetmap:sf"]),
    ]
    return DiscoveryPlan(case_id="zodiac", title="Zodiac Killer", discovered=ev, needs=needs)


def _result():
    return CaseCorrelationEngine().analyze(_plan(), _discovery())


# --- grafo -------------------------------------------------------------------
def test_graph_nodes_and_direct_relations():
    g = _result().graph
    ids = {n.id: n for n in g.nodes}
    assert ids["person:arthur_leigh_allen"].type == NodeType.PERSON
    assert "location:san_francisco" in ids and "event:1969_attack" in ids
    assert "timeline:case" in ids
    assert "evidence:wikimedia_commons:photo_allen" in ids

    rels = {(r.source_id, r.relation, r.target_id) for r in g.relations}
    assert ("evidence:wikimedia_commons:photo_allen", RelationType.SAME_PERSON,
            "person:arthur_leigh_allen") in rels
    assert ("evidence:openstreetmap:sf", RelationType.SAME_LOCATION,
            "location:san_francisco") in rels


def test_graph_mentions_and_timeline_references():
    g = _result().graph
    rels = {(r.source_id, r.relation, r.target_id) for r in g.relations}
    # el título de scene1 nombra a Allen -> MENTIONS (hecho observable)
    assert ("evidence:wikipedia:scene1", RelationType.MENTIONS,
            "person:arthur_leigh_allen") in rels
    # evidencias con fecha -> REFERENCES a la cronología
    assert ("evidence:wikipedia:scene1", RelationType.REFERENCES, "timeline:case") in rels


def test_graph_contradicts_on_conflicting_dates():
    g = _result().graph
    contradicts = [r for r in g.relations if r.relation == RelationType.CONTRADICTS]
    assert any({"wikipedia:scene1", "news:scene2"} <= set(r.evidence_ids) for r in contradicts)


# --- conflictos --------------------------------------------------------------
def test_conflict_recorded_not_decided():
    conflicts = _result().conflicts
    date_conflict = next(c for c in conflicts if c.kind == "date")
    assert date_conflict.requires_verification is True
    assert date_conflict.subject_id == "location:san_francisco"
    values = {c["value"] for c in date_conflict.candidates}
    assert values == {"1969-07-04", "1969-08-01"}        # ambos se conservan


# --- cobertura ---------------------------------------------------------------
def test_coverage_dimensions_states():
    cov = {d.name: d for d in _result().coverage.dimensions}
    assert cov["people"].state == CoverageState.COMPLETE
    assert cov["locations"].state == CoverageState.COMPLETE
    assert cov["photographs"].state == CoverageState.COMPLETE     # 3 >= min 2
    assert cov["maps"].state == CoverageState.COMPLETE
    assert cov["chronology"].state == CoverageState.COMPLETE
    assert cov["documents"].state == CoverageState.MISSING        # 0 descubiertos
    assert cov["audio"].state == CoverageState.MISSING


# --- recreación --------------------------------------------------------------
def test_recreation_only_for_uncovered_required_needs():
    candidates = _result().recreation_candidates
    ids = {c.id for c in candidates}
    # solo el documento judicial (requerido y sin evidencia)
    assert ids == {"recreation:court_document:case"}
    cand = candidates[0]
    assert cand.suggested_type == "document_visualization"
    assert cand.existing_coverage == CoverageState.MISSING
    assert cand.missing_evidence == ["COURT_DOCUMENT x1"]
    assert cand.factual_basis["target"] == "Zodiac Killer"
    assert "verificados" in cand.factual_basis["note"]


def test_no_recreation_when_real_evidence_sufficient():
    # ninguna recreación para fotos/mapas/escena (cubiertos por evidencia real)
    segments = {c.story_segment for c in _result().recreation_candidates}
    assert not any(C.PHOTO in s or C.MAP in s or C.SCENE_PHOTO in s for s in segments)


# --- determinismo / persistencia ---------------------------------------------
def test_correlation_is_deterministic():
    assert CaseCorrelationEngine().analyze(_plan(), _discovery()).to_dict() == \
        CaseCorrelationEngine().analyze(_plan(), _discovery()).to_dict()


def test_persistence_writes_four_files(tmp_path):
    paths = write_correlation_outputs(str(tmp_path / "zodiac"), _result())
    for name in ("evidence_graph.json", "coverage_report.json", "conflicts.json",
                 "recreation_candidates.json"):
        assert os.path.exists(paths[name])
    conflicts = json.load(open(paths["conflicts.json"], encoding="utf-8"))
    assert conflicts["conflicts"][0]["requires_verification"] is True


# --- integración con discovery (planner + registro estático) -----------------
def test_integration_via_case_discovery_cli(tmp_path):
    from types import SimpleNamespace
    import app.cli.case_discovery as cli
    from tests.test_eae_discovery import _static_registry

    args = SimpleNamespace(case_id="zodiac", title="Zodiac", genre="true_crime", subject="Z",
                           person=[ALLEN], location=[SF], event=[EVENT], license=[],
                           profile=None, plan=None, output_dir=str(tmp_path / "projects"))
    result = cli.run(args, registry=_static_registry())
    proj = os.path.join(str(tmp_path / "projects"), "zodiac")
    for name in ("evidence_graph.json", "coverage_report.json", "conflicts.json",
                 "recreation_candidates.json"):
        assert os.path.exists(os.path.join(proj, name))
    assert result["correlation"].graph.nodes
