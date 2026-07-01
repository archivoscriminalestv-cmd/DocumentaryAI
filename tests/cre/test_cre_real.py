"""Tests deterministas de los proveedores REALES del CRE (CRE-002).

Toda la red está mockeada con un ``FakeHttpClient``: no se realiza ninguna llamada
externa. Cubren: proveedores (Wikipedia/Wikidata/Commons), normalización con
confianza, conflictos/provenance, serialización de los campos nuevos, manifest,
reporte y CLI con proveedores inyectados.
"""

import json
import os
import tempfile

from app.cre.models import CharacterBible, CharacterRequest, VisualReference
from app.cre.normalizer import ResearchNormalizer
from app.cre.orchestrator import ResearchOrchestrator, real_providers
from app.cre.persistence import write_outputs
from app.cre.providers.base import ResearchResult
from app.cre.providers.commons import CommonsProvider
from app.cre.providers.wikidata import WikidataProvider
from app.cre.providers.wikipedia import WikipediaProvider


# --- cliente HTTP falso (canned data para "Nikola Tesla") -------------------
class FakeHttpClient:
    summary = {
        "type": "standard",
        "title": "Nikola Tesla",
        "extract": "Nikola Tesla was a Serbian-American inventor and engineer.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Nikola_Tesla"}},
    }
    pageprops = {"query": {"pages": {"123": {"pageprops": {"wikibase_item": "Q9036"}}}}}
    entity = {
        "entities": {
            "Q9036": {
                "claims": {
                    "P569": [{"mainsnak": {"datavalue": {"value": {"time": "+1856-07-10T00:00:00Z"}}}}],
                    "P570": [{"mainsnak": {"datavalue": {"value": {"time": "+1943-01-07T00:00:00Z"}}}}],
                    "P106": [
                        {"mainsnak": {"datavalue": {"value": {"id": "Q205375"}}}},
                        {"mainsnak": {"datavalue": {"value": {"id": "Q81096"}}}},
                    ],
                    "P27": [{"mainsnak": {"datavalue": {"value": {"id": "Q174193"}}}}],
                }
            }
        }
    }
    labels = {
        "entities": {
            "Q205375": {"labels": {"en": {"value": "inventor"}}},
            "Q81096": {"labels": {"en": {"value": "engineer"}}},
            "Q174193": {"labels": {"en": {"value": "Austrian Empire"}}},
        }
    }
    images = {
        "query": {
            "pages": {
                "123": {
                    "images": [
                        {"title": "File:Tesla circa 1890.jpeg"},
                        {"title": "File:Tesla Sarony.jpg"},
                        {"title": "File:Commons-logo.svg"},  # filtrado (no es imagen)
                    ]
                }
            }
        }
    }

    def _imageinfo(self, title: str) -> dict:
        return {
            "query": {
                "pages": {
                    "1": {
                        "imageinfo": [
                            {
                                "url": f"https://upload.wikimedia.org/{title.replace(' ', '_')}",
                                "width": 2000,
                                "height": 2500,
                                "extmetadata": {
                                    "LicenseShortName": {"value": "Public domain"},
                                    "Artist": {"value": "<a href='#'>Napoleon Sarony</a>"},
                                    "ImageDescription": {"value": "Tesla aged 34"},
                                },
                            }
                        ]
                    }
                }
            }
        }

    def get_json(self, url, params=None):
        params = params or {}
        if "rest_v1/page/summary" in url:
            return self.summary
        if "Special:EntityData" in url:
            return self.entity
        if url.startswith("https://www.wikidata.org/w/api.php") and params.get("action") == "wbgetentities":
            return self.labels
        if "wikipedia.org/w/api.php" in url:
            if params.get("prop") == "pageprops":
                return self.pageprops
            if params.get("prop") == "images":
                return self.images
        if "commons.wikimedia.org/w/api.php" in url and params.get("prop") == "imageinfo":
            return self._imageinfo(params.get("titles", ""))
        raise AssertionError(f"URL inesperada: {url} {params}")


class FailingHttpClient:
    def get_json(self, url, params=None):
        raise OSError("network blocked")


class DisambigHttpClient(FakeHttpClient):
    def get_json(self, url, params=None):
        if "rest_v1/page/summary" in url:
            return {"type": "disambiguation", "title": "Tesla"}
        return super().get_json(url, params)


REQ = CharacterRequest(name="Nikola Tesla")


# --- proveedores ------------------------------------------------------------
def test_wikipedia_provider_extracts_name_and_summary():
    res = WikipediaProvider(client=FakeHttpClient()).research(REQ)
    assert res.available is True
    assert res.data["identity"]["canonical_name"] == "Nikola Tesla"
    assert "inventor" in res.data["biography"]["summary"]
    assert res.sources == ["https://en.wikipedia.org/wiki/Nikola_Tesla"]
    assert res.confidence == 0.8


def test_wikipedia_provider_disambiguation_is_unavailable():
    res = WikipediaProvider(client=DisambigHttpClient()).research(REQ)
    assert res.available is False and res.data == {}


def test_wikipedia_provider_network_error_degrades_cleanly():
    res = WikipediaProvider(client=FailingHttpClient()).research(REQ)
    assert res.available is False and res.error and res.data == {}


def test_wikidata_provider_extracts_structured_facts():
    res = WikidataProvider(client=FakeHttpClient()).research(REQ)
    assert res.available is True
    ident = res.data["identity"]
    assert ident["birth_date"] == "1856-07-10"
    assert ident["death_date"] == "1943-01-07"
    assert ident["occupation"] == "inventor, engineer"
    assert ident["nationality"] == "Austrian Empire"
    assert res.confidence == 0.9


def test_commons_provider_catalogs_visual_references_without_download():
    res = CommonsProvider(client=FakeHttpClient()).research(REQ)
    assert res.available is True
    # dos imágenes válidas (el .svg se filtra)
    assert len(res.visual_references) == 2
    ref = res.visual_references[0]
    assert ref.provider == "commons"
    assert ref.license == "Public domain"
    assert ref.author == "Napoleon Sarony"  # HTML stripped
    assert ref.resolution == "2000x2500"
    assert ref.quality_score == 1.0
    assert ref.hash == ""  # NO se descarga: hash reservado


# --- normalización: confianza, provenance, conflictos -----------------------
def test_normalizer_higher_confidence_wins_and_records_provenance():
    req = CharacterRequest(name="X")
    low = ResearchResult("low", True, {"identity": {"occupation": "mito"}}, confidence=0.2)
    high = ResearchResult("high", True, {"identity": {"occupation": "inventor"}}, confidence=0.9)
    bible = ResearchNormalizer().normalize(req, [low, high])
    assert bible.identity.occupation == "inventor"  # mayor confianza gana
    prov = [p for p in bible.provenance if p["field"] == "identity.occupation"]
    assert prov and prov[0]["provider"] == "high" and prov[0]["confidence"] == 0.9
    # discrepancia registrada sin fusionar
    conflict = [c for c in bible.conflicts if c["field"] == "identity.occupation"]
    assert conflict and len(conflict[0]["candidates"]) == 2


def test_normalizer_is_deterministic_with_real_provider_shapes():
    n = ResearchNormalizer()
    results = [
        WikipediaProvider(client=FakeHttpClient()).research(REQ),
        WikidataProvider(client=FakeHttpClient()).research(REQ),
        CommonsProvider(client=FakeHttpClient()).research(REQ),
    ]
    b1 = n.normalize(REQ, results)
    b2 = n.normalize(REQ, results)
    assert b1 == b2


# --- serialización de campos nuevos -----------------------------------------
def test_serialization_roundtrip_with_new_visual_and_provenance_fields():
    bible = CharacterBible()
    bible.visual_references.append(
        VisualReference(id="img1", provider="commons", url="u", license="PD",
                        resolution="100x100", quality_score=0.01)
    )
    bible.provenance.append({"field": "identity.occupation", "value": "x",
                             "provider": "wikidata", "confidence": 0.9})
    bible.conflicts.append({"field": "identity.nationality",
                            "candidates": [{"value": "a", "provider": "p", "confidence": 0.5}]})
    restored = CharacterBible.from_dict(bible.to_dict())
    assert restored == bible


# --- orquestador + manifest -------------------------------------------------
def test_orchestrator_with_real_providers_builds_rich_bible():
    fake = FakeHttpClient()
    orch = ResearchOrchestrator(real_providers(client=fake))
    b1, manifest = orch.research(REQ)
    b2, _ = orch.research(REQ)
    assert b1 == b2  # determinista con red mockeada

    assert b1.identity.canonical_name == "Nikola Tesla"
    assert b1.identity.birth_date == "1856-07-10"
    assert b1.identity.occupation == "inventor, engineer"
    assert b1.biography.summary
    assert len(b1.visual_references) == 2
    for p in ("wikipedia", "wikidata", "commons", "mock-research"):
        assert p in b1.providers_used

    # manifest enriquecido
    assert manifest["versions"]["cre"] == "CRE-002"
    assert manifest["character_id"] == "nikola_tesla"
    assert manifest["totals"]["providers_available"] >= 4
    wiki = next(p for p in manifest["providers"] if p["provider"] == "wikipedia")
    assert wiki["confidence"] == 0.8 and "elapsed_ms" in wiki
    # los stubs preparados aparecen como no disponibles
    assert any(p["provider"] == "news" and not p["available"] for p in manifest["providers"])


# --- persistencia / reporte / CLI -------------------------------------------
def test_report_includes_coverage_and_sources():
    orch = ResearchOrchestrator(real_providers(client=FakeHttpClient()))
    bible, manifest = orch.research(REQ)
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_outputs(os.path.join(tmp, "tesla"), bible, manifest, generated_at=0.0)
        report = open(paths["report"], encoding="utf-8").read()
        assert "Cobertura de la investigación" in report
        assert "Referencias visuales" in report
        assert "Nikola Tesla" in report
        manifest_saved = json.load(open(paths["manifest"], encoding="utf-8"))
        assert manifest_saved["versions"]["cre"] == "CRE-002"
        assert "generated_at" in manifest_saved


def test_cli_with_injected_real_providers(monkeypatch=None):
    import app.cli.research_character as cli

    providers = real_providers(client=FakeHttpClient())
    with tempfile.TemporaryDirectory() as tmp:
        cli.main(["--name", "Nikola Tesla", "--output-dir", tmp], providers=providers)
        bible_path = os.path.join(tmp, "nikola_tesla", "character_bible.json")
        data = json.load(open(bible_path, encoding="utf-8"))
        assert data["identity"]["birth_date"] == "1856-07-10"
        assert len(data["visual_references"]) == 2
        assert data["provenance"]  # trazabilidad presente
