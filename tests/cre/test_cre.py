"""Tests deterministas del Character Research Engine (CRE). Sin llamadas reales."""

import json
import os
import tempfile

from app.cre.models import (
    CharacterBible,
    CharacterRequest,
    Identity,
    VisualReference,
    slugify,
)
from app.cre.normalizer import ResearchNormalizer
from app.cre.orchestrator import ResearchOrchestrator, default_providers
from app.cre.persistence import write_outputs
from app.cre.providers.base import ResearchProvider, ResearchResult
from app.cre.providers.external import WikipediaProvider
from app.cre.providers.mock import MockResearchProvider


# --- modelos / slug ---------------------------------------------------------
def test_slugify_handles_accents_and_spaces():
    assert slugify("Coquito") == "coquito"
    assert slugify("Marie Curie") == "marie_curie"
    assert slugify("Dalí") == "dali"
    assert slugify("") == "unknown"


def test_bible_serialization_roundtrip():
    bible = CharacterBible(identity=Identity(id="x", canonical_name="X", aliases=["a"]))
    bible.visual_references.append(VisualReference(source="s", provider="p"))
    restored = CharacterBible.from_dict(bible.to_dict())
    assert restored == bible


# --- mock provider (determinista, sin inventar) -----------------------------
def test_mock_provider_is_deterministic_and_request_derived():
    req = CharacterRequest(name="Tesla", aliases=["Nikola"])
    a = MockResearchProvider().research(req)
    b = MockResearchProvider().research(req)
    assert a == b  # determinista
    assert a.available is True
    assert a.data["identity"]["canonical_name"] == "Tesla"
    assert a.data["identity"]["aliases"] == ["Nikola"]
    # no inventa hechos: campos sin pista quedan vacíos
    assert a.data["identity"]["birth_date"] == ""


def test_external_providers_are_unavailable_stubs():
    res = WikipediaProvider().research(CharacterRequest(name="Einstein"))
    assert res.available is False and res.data == {}


# --- normalizer (fusión determinista) ---------------------------------------
def test_normalizer_merges_scalars_first_wins_and_lists_dedupe():
    req = CharacterRequest(name="Picasso")
    r1 = ResearchResult("p1", True, {"identity": {"occupation": "pintor"},
                                     "biography": {"locations": ["Málaga", "París"]}})
    r2 = ResearchResult("p2", True, {"identity": {"occupation": "escultor"},  # no pisa
                                     "biography": {"locations": ["París", "Barcelona"]}})
    bible = ResearchNormalizer().normalize(req, [r1, r2])
    assert bible.identity.occupation == "pintor"  # primer no vacío gana
    assert bible.biography.locations == ["Málaga", "París", "Barcelona"]  # dedupe orden
    assert bible.providers_used == ["p1", "p2"]


def test_normalizer_identity_fallback_to_request():
    bible = ResearchNormalizer().normalize(CharacterRequest(name="Marie Curie"), [])
    assert bible.identity.canonical_name == "Marie Curie"
    assert bible.identity.id == "marie_curie"


# --- orquestador ------------------------------------------------------------
def test_orchestrator_generic_and_deterministic():
    orch = ResearchOrchestrator(default_providers())
    b1, m1 = orch.research(CharacterRequest(name="Coquito"))
    b2, m2 = orch.research(CharacterRequest(name="Coquito"))
    assert b1 == b2  # reproducible
    assert b1.identity.id == "coquito"
    assert "mock-research" in b1.providers_used
    # los stubs aparecen como no disponibles en el manifest
    assert any(p["provider"] == "wikipedia" and not p["available"] for p in m1["providers"])


def test_orchestrator_supports_new_provider_without_changing_system():
    class CustomProvider(ResearchProvider):
        name = "custom"
        def research(self, request):
            return ResearchResult("custom", True, {"voice": {"accent": "neutro"}})

    orch = ResearchOrchestrator([CustomProvider(), MockResearchProvider()])
    bible, _ = orch.research(CharacterRequest(name="Einstein"))
    assert bible.voice.accent == "neutro" and "custom" in bible.providers_used


# --- CLI / persistencia -----------------------------------------------------
def test_persistence_writes_three_files_and_reproducible_bible():
    orch = ResearchOrchestrator(default_providers())
    bible, manifest = orch.research(CharacterRequest(name="Dalí"))
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_outputs(os.path.join(tmp, "dali"), bible, manifest, generated_at=0.0)
        for key in ("bible", "manifest", "report"):
            assert os.path.exists(paths[key]) and os.path.getsize(paths[key]) > 0
        data = json.load(open(paths["bible"], encoding="utf-8"))
        assert data["identity"]["id"] == "dali"
        assert data["schema_version"] == "1.0"


def test_cli_main_creates_outputs(tmp_path=None):
    import app.cli.research_character as cli

    with tempfile.TemporaryDirectory() as tmp:
        # --offline: catálogo determinista (sin red), CRE-002 usa fuentes reales por defecto
        cli.main(["--name", "Coquito", "--offline", "--output-dir", tmp])
        bible_path = os.path.join(tmp, "coquito", "character_bible.json")
        assert os.path.exists(bible_path)
        data = json.load(open(bible_path, encoding="utf-8"))
        assert data["identity"]["canonical_name"] == "Coquito"
