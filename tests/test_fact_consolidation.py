"""Tests del Fact Intelligence Layer (C-05). Determinista, sin red, sin IA."""

import json
from dataclasses import asdict

from app.application.fact_service import FactService
from app.domain.evidence.extracted_evidence import ExtractedEvidence
from app.domain.fact.consolidated_fact import ConsolidatedFact


def _ev(id_, source_id, claim, confidence=0.9) -> ExtractedEvidence:
    return ExtractedEvidence(id=id_, source_id=source_id, claim=claim, context="ctx", confidence=confidence)


# Tres afirmaciones léxicamente equivalentes (mismos tokens significativos) + 1 distinta.
_NEAR_DUPES = [
    _ev("ev-01", "src-01", "The Chernobyl nuclear disaster occurred in 1986 near the city of Pripyat", 0.9),
    _ev("ev-02", "src-02", "The Chernobyl nuclear disaster occurred in 1986 near Pripyat", 0.85),
    _ev("ev-03", "src-03", "The Chernobyl nuclear disaster occurred in 1986", 0.95),
]
_DISTINCT = _ev("ev-04", "src-04", "Radioactive fallout spread across large regions of Europe", 0.8)


def test_merges_near_duplicates_into_single_fact():
    facts = FactService().consolidate(_NEAR_DUPES)

    assert len(facts) == 1  # NO un hecho por evidencia
    fact = facts[0]
    assert fact.evidence_ids == ["ev-01", "ev-02", "ev-03"]
    assert fact.source_ids == ["src-01", "src-02", "src-03"]


def test_statement_is_simplest_claim_verbatim_no_invention():
    facts = FactService().consolidate(_NEAR_DUPES)
    # La afirmación más simple del grupo, tal cual (grounding estricto).
    assert facts[0].statement == "The Chernobyl nuclear disaster occurred in 1986"
    assert facts[0].statement in {e.claim for e in _NEAR_DUPES}


def test_confidence_is_minimum_of_group():
    facts = FactService().consolidate(_NEAR_DUPES)
    assert facts[0].confidence == 0.85  # min(0.9, 0.85, 0.95)


def test_distinct_claims_are_not_over_merged():
    facts = FactService().consolidate(_NEAR_DUPES + [_DISTINCT])
    assert len(facts) == 2
    assert facts[1].statement == _DISTINCT.claim
    assert facts[1].evidence_ids == ["ev-04"]
    assert facts[1].source_ids == ["src-04"]
    assert facts[1].confidence == 0.8


def test_ids_are_sequential_and_deterministic():
    facts = FactService().consolidate(_NEAR_DUPES + [_DISTINCT])
    assert [f.id for f in facts] == ["fact-01", "fact-02"]


def test_empty_input_returns_empty():
    assert FactService().consolidate([]) == []
    assert FactService().consolidate(None) == []


def test_invalid_evidence_is_skipped_safely():
    facts = FactService().consolidate([
        _ev("ev-01", "src-01", "A clearly distinct verifiable statement about reactors"),
        None,
        object(),
        _ev("ev-02", "src-02", "   "),  # claim vacío -> se omite
    ])
    assert len(facts) == 1
    assert facts[0].evidence_ids == ["ev-01"]


def test_output_is_json_serializable():
    facts = FactService().consolidate(_NEAR_DUPES + [_DISTINCT])
    decoded = json.loads(json.dumps([asdict(f) for f in facts], ensure_ascii=False))
    assert set(decoded[0].keys()) == {"id", "statement", "confidence", "evidence_ids", "source_ids"}
    assert decoded[0]["confidence"] == 0.85


def test_consolidation_is_deterministic():
    a = FactService().consolidate(_NEAR_DUPES + [_DISTINCT])
    b = FactService().consolidate(_NEAR_DUPES + [_DISTINCT])
    assert [asdict(x) for x in a] == [asdict(x) for x in b]


def test_provenance_dedupes_repeated_ids():
    # Misma fuente repetida en evidencias del mismo grupo -> source_id único.
    facts = FactService().consolidate([
        _ev("ev-01", "src-01", "The reactor core overheated during the safety test procedure"),
        _ev("ev-02", "src-01", "The reactor core overheated during the safety test"),
    ])
    assert len(facts) == 1
    assert facts[0].evidence_ids == ["ev-01", "ev-02"]
    assert facts[0].source_ids == ["src-01"]  # deduplicado
