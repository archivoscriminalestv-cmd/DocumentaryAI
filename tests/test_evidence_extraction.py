"""Tests del Evidence Intelligence Layer (C-04). Determinista, sin red, sin IA."""

import json
from dataclasses import asdict

from app.application.evidence_extractor import EvidenceExtractor
from app.application.evidence_service import EvidenceService
from app.domain.evidence.extracted_evidence import ExtractedEvidence
from app.domain.search import SearchType
from app.domain.source.retrieved_source import RetrievedSource

_LONG = (
    "The Fermi paradox is the conflict between the lack of clear evidence for "
    "extraterrestrial life and various high estimates for its probability; "
    "many possible solutions have been proposed over the decades."
)


def _source(text=_LONG, type_=SearchType.WIKIPEDIA, id_="src-01") -> RetrievedSource:
    return RetrievedSource(id=id_, type=type_, title="T", url="http://x", snippet=text, query="q")


def test_extracts_claims_over_40_chars_with_provenance():
    out = EvidenceExtractor().extract(_source())

    assert len(out) == 2  # dos frases significativas; el resto se filtra
    assert all(isinstance(e, ExtractedEvidence) for e in out)
    assert all(len(e.claim) > 40 for e in out)
    assert all(e.source_id == "src-01" for e in out)        # cadena de procedencia
    assert all(e.confidence == 0.9 for e in out)            # wikipedia
    assert out[0].id == "ev-01" and out[1].id == "ev-02"
    assert all(e.context for e in out)


def test_short_sentences_are_filtered():
    out = EvidenceExtractor().extract(_source("Too short. Also short."))
    assert out == []


def test_splits_on_period_newline_semicolon():
    text = (
        "First long sentence that comfortably exceeds the forty character limit"
        "\n"
        "Second long sentence that also exceeds the forty character minimum here"
        ";"
        "Third long sentence likewise beyond the forty character threshold now"
    )
    out = EvidenceExtractor().extract(_source(text))
    assert len(out) == 3


def test_confidence_by_source_type():
    expected = {
        SearchType.WIKIPEDIA: 0.9,
        SearchType.YOUTUBE: 0.7,
        SearchType.NEWS: 0.85,
        SearchType.ACADEMIC: 0.95,
        SearchType.ARCHIVES: 0.8,
        SearchType.BOOKS: 0.6,          # other
        SearchType.GOVERNMENT: 0.6,     # other
        SearchType.SCIENTIFIC_PAPERS: 0.6,  # other
    }
    for type_, conf in expected.items():
        out = EvidenceExtractor().extract(_source(type_=type_))
        assert out and all(e.confidence == conf for e in out), type_


def test_extract_all_assigns_global_sequential_ids():
    sources = [_source(id_="src-01"), _source(id_="src-02")]
    out = EvidenceService().extract_all(sources)

    assert [e.id for e in out] == ["ev-01", "ev-02", "ev-03", "ev-04"]
    # procedencia preservada por fuente
    assert [e.source_id for e in out] == ["src-01", "src-01", "src-02", "src-02"]


def test_empty_sources_returns_empty():
    assert EvidenceService().extract_all([]) == []
    assert EvidenceService().extract_all(None) == []


def test_invalid_sources_are_skipped_safely():
    out = EvidenceService().extract_all([_source(), None, object(), _source("short")])
    # solo la fuente válida produce evidencia; nada revienta
    assert len(out) == 2
    assert all(e.source_id == "src-01" for e in out)


def test_output_is_json_serializable():
    out = EvidenceService().extract_all([_source()])
    decoded = json.loads(json.dumps([asdict(e) for e in out], ensure_ascii=False))
    assert decoded[0]["confidence"] == 0.9
    assert set(decoded[0].keys()) == {"id", "source_id", "claim", "context", "confidence"}


def test_extraction_is_deterministic():
    sources = [_source(id_="src-01"), _source(id_="src-02")]
    a = EvidenceService().extract_all(sources)
    b = EvidenceService().extract_all(sources)
    assert [asdict(x) for x in a] == [asdict(x) for x in b]
