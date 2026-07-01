"""Tests deterministas del Evidence Research Engine (ERE). Sin llamadas reales.

La red se mockea con ``FakeHttpClient``. Cubren: modelos/serialización, proveedores
reales (Wikipedia/Wikidata/Commons), preparados, seed, mock, graph builder (merge +
conflictos + relaciones→referencias), orquestador (nunca rompe), manifest/checksum,
reporte y CLI.
"""

import json
import os
import tempfile

from app.ere.graph_builder import GraphBuilder
from app.ere.models import (
    Claim,
    Entity,
    EvidenceGraph,
    ImageAsset,
    ProjectQuery,
    Relationship,
    SourceRef,
    slugify,
)
from app.ere.orchestrator import (
    EvidenceOrchestrator,
    default_providers,
    real_providers,
)
from app.ere.persistence import write_outputs
from app.ere.providers.base import EvidenceProvider, EvidenceResult
from app.ere.providers.commons import CommonsProvider
from app.ere.providers.mock import MockEvidenceProvider
from app.ere.providers.prepared import NewsProvider, CourtDocumentsProvider
from app.ere.providers.seed import SeedEvidenceProvider
from app.ere.providers.wikidata import WikidataProvider
from app.ere.providers.wikipedia import WikipediaProvider


# --- cliente HTTP falco (canned, "Nikola Tesla") ----------------------------
class FakeHttpClient:
    summary = {
        "type": "standard", "title": "Nikola Tesla",
        "extract": "Nikola Tesla was a Serbian-American inventor and engineer.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Nikola_Tesla"}},
    }
    pageprops = {"query": {"pages": {"1": {"pageprops": {"wikibase_item": "Q9036"}}}}}
    entity = {"entities": {"Q9036": {"claims": {
        "P569": [{"mainsnak": {"datavalue": {"value": {"time": "+1856-07-10T00:00:00Z"}}}}],
        "P570": [{"mainsnak": {"datavalue": {"value": {"time": "+1943-01-07T00:00:00Z"}}}}],
        "P106": [{"mainsnak": {"datavalue": {"value": {"id": "Q205375"}}}}],
        "P27": [{"mainsnak": {"datavalue": {"value": {"id": "Q174193"}}}}],
    }}}}
    labels = {"entities": {
        "Q205375": {"labels": {"en": {"value": "inventor"}}},
        "Q174193": {"labels": {"en": {"value": "Austrian Empire"}}},
    }}
    images = {"query": {"pages": {"1": {"images": [
        {"title": "File:Tesla Sarony.jpg"},
        {"title": "File:N.Tesla.JPG"},
        {"title": "File:Logo.svg"},  # filtrado
    ]}}}}

    def _imageinfo(self, title):
        return {"query": {"pages": {"1": {"imageinfo": [{
            "url": f"https://upload.wikimedia.org/{title.replace(' ', '_')}",
            "width": 2000, "height": 2500,
            "extmetadata": {
                "LicenseShortName": {"value": "Public domain"},
                "Artist": {"value": "<a>Napoleon Sarony</a>"},
                "ImageDescription": {"value": "portrait"},
            },
        }]}}}}

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


class BoomProvider(EvidenceProvider):
    name = "boom"

    def research(self, query):
        raise RuntimeError("kaboom")


TESLA = ProjectQuery(name="Nikola Tesla")
COQUITO = ProjectQuery(name="Coquito", location="Barcelona", date="2021-01-04",
                       aliases=["El Coquito"])


# --- modelos / serialización ------------------------------------------------
def test_slugify_and_subject_id():
    assert slugify("Coquito") == "coquito"
    assert COQUITO.subject_id() == "character:coquito"


def test_graph_serialization_roundtrip():
    graph = EvidenceGraph(project=COQUITO)
    graph.entities.append(Entity(
        id="character:coquito", canonical_name="Coquito", aliases=["El Coquito"],
        attributes={"nationality": [Claim("nationality", "Spain", "seed", 0.6, "u")]},
        references=["image:x"], sources=[SourceRef(provider="seed", url="u", confidence=0.6)],
    ))
    graph.images.append(ImageAsset(id="image:x", provider="seed", license="CC0"))
    graph.relationships.append(Relationship("character:coquito", "has_reference", "image:x"))
    restored = EvidenceGraph.from_dict(graph.to_dict())
    assert restored == graph


# --- proveedores reales (mock HTTP) -----------------------------------------
def test_wikipedia_provider_emits_entity_with_provenance():
    res = WikipediaProvider(client=FakeHttpClient()).research(TESLA)
    assert res.available and len(res.entities) == 1
    ent = res.entities[0]
    assert ent.id == "character:nikola_tesla"
    assert ent.canonical_name == "Nikola Tesla"
    claim = ent.attributes["biography_summary"][0]
    assert claim.provider == "wikipedia" and claim.confidence == 0.8
    assert res.sources[0].url.endswith("Nikola_Tesla")


def test_wikidata_provider_structured_claims():
    res = WikidataProvider(client=FakeHttpClient()).research(TESLA)
    attrs = res.entities[0].attributes
    assert attrs["birth_date"][0].value == "1856-07-10"
    assert attrs["death_date"][0].value == "1943-01-07"
    assert attrs["occupation"][0].value == "inventor"
    assert attrs["nationality"][0].value == "Austrian Empire"


def test_commons_provider_catalogs_images_and_links():
    res = CommonsProvider(client=FakeHttpClient()).research(TESLA)
    assert res.available and len(res.images) == 2  # svg filtrado
    img = res.images[0]
    assert img.id.startswith("image:") and img.license == "Public domain"
    assert img.author == "Napoleon Sarony" and img.hash == ""  # sin descarga
    assert all(r.relation == "has_reference" for r in res.relationships)


# --- preparados / seed / mock -----------------------------------------------
def test_prepared_providers_are_unavailable_but_safe():
    for prov in (NewsProvider(), CourtDocumentsProvider()):
        res = prov.research(COQUITO)
        assert res.available is False and res.error == "" and res.entities == []


def test_seed_provider_normalizes_public_evidence():
    seed = {
        "entities": [{"canonical_name": "Jonathan Burgos", "aliases": ["Coquito"],
                      "attributes": {"nationality": "Spain", "estimated_age": "40"},
                      "url": "https://example.org/case"}],
        "articles": [{"headline": "Caso X", "medium": "Diario", "date": "2021-01-05",
                      "url": "https://news.example/1", "snippet": "...",
                      "entities_detected": ["Jonathan Burgos"]}],
        "images": [{"original_url": "https://img.example/1.jpg", "license": "CC BY",
                    "caption": "foto", "resolution": "800x600"}],
        "videos": [{"title": "Reportaje", "url": "https://youtu.be/abc", "channel": "TV"}],
        "court_documents": [{"title": "Sentencia", "reference": "STS 1/2022",
                             "url": "https://court.example/1"}],
        "relationships": [{"source_id": "character:jonathan_burgos",
                           "relation": "mentioned_in", "target_id": "article:caso_x"}],
    }
    res = SeedEvidenceProvider(data=seed).research(COQUITO)
    assert res.available
    assert res.entities[0].attributes["estimated_age"][0].value == "40"
    assert res.articles[0].medium == "Diario"
    assert res.images[0].license == "CC BY"
    assert res.videos[0].channel == "TV"
    assert res.court_documents[0].reference == "STS 1/2022"
    assert res.relationships[0].relation == "mentioned_in"


def test_mock_provider_only_subject_no_facts():
    res = MockEvidenceProvider().research(COQUITO)
    ent = res.entities[0]
    assert ent.canonical_name == "Coquito" and ent.attributes == {}
    assert ent.metadata["query_location"] == "Barcelona"  # del request, no un hecho


# --- graph builder ----------------------------------------------------------
def test_graph_builder_merges_and_preserves_conflicts():
    e1 = Entity(id="character:x", canonical_name="X",
                attributes={"nationality": [Claim("nationality", "Spain", "p1", 0.6, "u1")]},
                sources=[SourceRef(provider="p1", confidence=0.6)])
    e2 = Entity(id="character:x", canonical_name="X",
                attributes={"nationality": [Claim("nationality", "France", "p2", 0.9, "u2")]},
                sources=[SourceRef(provider="p2", confidence=0.9)])
    img = ImageAsset(id="image:1", provider="p2")
    rel = Relationship("character:x", "has_reference", "image:1", "p2", 0.9)
    r1 = EvidenceResult("p1", True, entities=[e1])
    r2 = EvidenceResult("p2", True, entities=[e2], images=[img], relationships=[rel])

    graph = GraphBuilder().build(ProjectQuery(name="X"), [r1, r2])
    ent = graph.entities[0]
    # ambos valores conservados (no se decide)
    assert len(ent.attributes["nationality"]) == 2
    conflict = [c for c in graph.conflicts if c["field"] == "nationality"]
    assert conflict and len(conflict[0]["candidates"]) == 2
    # relación has_reference puebla references
    assert "image:1" in ent.references


def test_graph_builder_is_deterministic():
    fake = FakeHttpClient()
    providers = [WikipediaProvider(client=fake), WikidataProvider(client=fake),
                 CommonsProvider(client=fake), MockEvidenceProvider()]
    g1, _ = EvidenceOrchestrator(providers).research(TESLA)
    g2, _ = EvidenceOrchestrator(providers).research(TESLA)
    assert g1 == g2


# --- orquestador: nunca rompe -----------------------------------------------
def test_orchestrator_never_fails_on_provider_exception():
    orch = EvidenceOrchestrator([BoomProvider(), MockEvidenceProvider()])
    graph, manifest = orch.research(COQUITO)
    assert graph.entities  # el pipeline siguió
    boom = next(p for p in manifest["providers"] if p["provider"] == "boom")
    assert boom["available"] is False and "kaboom" in boom["error"]


def test_orchestrator_real_providers_build_rich_graph():
    orch = EvidenceOrchestrator(real_providers(client=FakeHttpClient()))
    graph, manifest = orch.research(TESLA)
    subject = next(e for e in graph.entities if e.id == "character:nikola_tesla")
    assert subject.canonical_name == "Nikola Tesla"  # wikipedia > mock por confianza
    assert "occupation" in subject.attributes
    assert len(graph.images) == 2
    assert any(r.relation == "has_reference" for r in graph.relationships)
    assert manifest["versions"]["ere"] == "ERE-001"
    assert manifest["statistics"]["images"] == 2
    # proveedores preparados presentes y no disponibles
    assert any(p["provider"] == "news" and not p["available"] for p in manifest["providers"])


# --- persistencia / reporte / CLI -------------------------------------------
def test_persistence_writes_three_files_with_checksum():
    orch = EvidenceOrchestrator(real_providers(client=FakeHttpClient()))
    graph, manifest = orch.research(TESLA)
    with tempfile.TemporaryDirectory() as tmp:
        paths = write_outputs(os.path.join(tmp, "t"), graph, manifest, generated_at=0.0)
        for key in ("graph", "manifest", "report"):
            assert os.path.exists(paths[key])
        saved = json.load(open(paths["manifest"], encoding="utf-8"))
        assert saved["graph_checksum"].startswith("sha256:")
        report = open(paths["report"], encoding="utf-8").read()
        assert "Evidence Report" in report and "Cobertura" in report


def test_cli_offline_and_injected(tmp_path=None):
    import app.cli.research_evidence as cli

    with tempfile.TemporaryDirectory() as tmp:
        cli.main(["--project", "Coquito", "--offline", "--output-dir", tmp])
        graph_path = os.path.join(tmp, "coquito", "evidence_graph.json")
        data = json.load(open(graph_path, encoding="utf-8"))
        assert data["project"]["name"] == "Coquito"
        assert data["entities"][0]["id"] == "character:coquito"

    with tempfile.TemporaryDirectory() as tmp:
        providers = real_providers(client=FakeHttpClient())
        cli.main(["--project", "Nikola Tesla", "--output-dir", tmp], providers=providers)
        data = json.load(open(os.path.join(tmp, "nikola_tesla", "evidence_graph.json"),
                          encoding="utf-8"))
        assert len(data["images"]) == 2
