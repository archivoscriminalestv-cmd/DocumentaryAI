"""Tests de los proveedores REALES de Discovery (EAE-004) — sin red (HTTP mockeado)."""

from app.eae.discovery.cache import DiscoveryCache, cache_key
from app.eae.discovery.engine import CaseDiscoveryEngine
from app.eae.discovery.http import MappingHttpClient, RealHttpClient, Response
from app.eae.discovery.manifest import build_manifest
from app.eae.discovery.providers.base import DiscoveryQuery
from app.eae.discovery.providers.catalog import contract_providers
from app.eae.discovery.providers.real import (
    InternetArchiveProvider,
    OpenStreetMapProvider,
    WikidataProvider,
    WikimediaCommonsProvider,
    WikipediaProvider,
    real_providers,
)
from app.eae.discovery.registry import SourceRegistry
from app.eae.discovery.resolver import SourceResolver
from app.eae.planner import CaseProfile, EvidenceInvestigationPlanner
from app.eae.planner.models import EvidenceCategory as C

COMMONS = {"query": {"pages": {"123": {"title": "File:Zodiac letter.jpg", "imageinfo": [{
    "url": "https://upload.wikimedia.org/zodiac.jpg",
    "descriptionurl": "https://commons.wikimedia.org/wiki/File:Zodiac_letter.jpg",
    "width": 1200, "height": 900, "mime": "image/jpeg",
    "extmetadata": {"LicenseShortName": {"value": "Public domain"},
                    "Artist": {"value": "<a href='#'>SFPD</a>"},
                    "ImageDescription": {"value": "A cipher letter"},
                    "DateTimeOriginal": {"value": "1969-11-08"}}}]}}}}
IA = {"response": {"docs": [{"identifier": "zodiac_footage", "title": "Zodiac footage",
      "mediatype": "movies", "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/",
      "year": "1971", "format": ["MPEG4", "h.264"]}]}}
OSM = [{"osm_type": "relation", "osm_id": 111111, "lat": "37.7749", "lon": "-122.4194",
        "boundingbox": ["37.7", "37.8", "-122.5", "-122.3"],
        "display_name": "San Francisco, California, USA", "type": "city", "category": "place"}]
WIKIDATA = {"search": [{"id": "Q186386", "label": "Zodiac Killer",
            "description": "unidentified American serial killer", "aliases": ["Zodiac"],
            "concepturi": "http://www.wikidata.org/entity/Q186386"}]}
WIKIPEDIA = {"query": {"search": [{"pageid": 34176, "title": "Zodiac Killer",
             "snippet": "The <b>Zodiac Killer</b> was active in California."}]}}


def _client():
    return MappingHttpClient([
        ("commons.wikimedia.org", COMMONS),
        ("archive.org/advancedsearch", IA),
        ("nominatim.openstreetmap.org", OSM),
        ("wikidata.org/w/api.php", WIKIDATA),
        ("wikipedia.org/w/api.php", WIKIPEDIA),
    ])


def _q(category, terms, **kw):
    return DiscoveryQuery(case_id="c", need_id=f"need:{category}", category=category,
                          terms=terms, **kw)


# --- proveedores reales (parsing) -------------------------------------------
def test_wikimedia_parses_rich_fields():
    p = WikimediaCommonsProvider(http=_client())
    assert p.available() is True
    ev = p.discover(_q(C.SCENE_PHOTO, ["Zodiac Killer"]))[0]
    assert ev.provider == "wikimedia_commons"
    assert ev.url == "https://upload.wikimedia.org/zodiac.jpg"
    assert ev.license == "Public domain" and ev.resolution == "1200x900"
    assert ev.fmt == "jpeg" and ev.date == "1969-11-08"
    assert ev.extra["author"] == "SFPD"            # HTML eliminado
    assert ev.query_used == ["Zodiac Killer"]


def test_internet_archive_parses_identifier_and_license():
    ev = InternetArchiveProvider(http=_client()).discover(_q(C.ARCHIVE_VIDEO, ["Zodiac"]))[0]
    assert ev.extra["identifier"] == "zodiac_footage"
    assert ev.url == "https://archive.org/details/zodiac_footage"
    assert ev.media_type == "movies" and "publicdomain" in ev.license
    assert ev.extra["metadata_url"].endswith("/metadata/zodiac_footage")


def test_openstreetmap_parses_coordinates():
    ev = OpenStreetMapProvider(http=_client()).discover(_q(C.MAP, ["San Francisco"]))[0]
    assert ev.extra["lat"] == "37.7749" and ev.extra["lon"] == "-122.4194"
    assert ev.extra["bounding_box"] == ["37.7", "37.8", "-122.5", "-122.3"]
    assert ev.url.startswith("https://www.openstreetmap.org/relation/")


def test_wikidata_parses_entity():
    ev = WikidataProvider(http=_client()).discover(_q(C.TIMELINE, ["Zodiac Killer"]))[0]
    assert ev.extra["qid"] == "Q186386" and "Zodiac" in ev.extra["aliases"]
    assert ev.url == "http://www.wikidata.org/entity/Q186386"


def test_wikipedia_parses_reference_no_html():
    ev = WikipediaProvider(http=_client()).discover(_q(C.NEWS, ["Zodiac Killer"]))[0]
    assert ev.extra["pageid"] == 34176
    assert "<b>" not in ev.extra["snippet"]         # nunca HTML
    assert ev.url.endswith("?curid=34176")


def test_provider_without_http_is_contract():
    assert WikimediaCommonsProvider().available() is False
    assert WikimediaCommonsProvider().discover(_q(C.PHOTO, ["x"])) == []


# --- cache -------------------------------------------------------------------
def test_cache_avoids_repeated_queries():
    http = _client()
    p = WikimediaCommonsProvider(http=http, cache=DiscoveryCache())
    q = _q(C.SCENE_PHOTO, ["Zodiac Killer"])
    p.discover(q)
    p.discover(q)
    assert len(http.calls) == 1                     # segunda vez: cache


def test_errors_are_never_cached():
    class Raising:
        def __init__(self): self.calls = 0
        def get(self, url, params=None, headers=None):
            self.calls += 1
            raise OSError("network down")
    http = Raising()
    p = WikimediaCommonsProvider(http=http, cache=DiscoveryCache())
    q = _q(C.SCENE_PHOTO, ["x"])
    assert p.discover(q) == [] and p.discover(q) == []
    assert http.calls == 2                          # el error no se cachea


def test_cache_key_is_deterministic():
    a = cache_key("p", category="PHOTO", target="t", terms=["b", "a"], language="en", filters=[])
    b = cache_key("p", category="PHOTO", target="t", terms=["a", "b"], language="en", filters=[])
    assert a == b                                   # términos ordenados


# --- resolver: selección por capacidad/coste/fiabilidad ----------------------
def test_resolver_select_discards_with_reasons():
    reg = SourceRegistry(real_providers() + contract_providers())
    selected, discarded = SourceResolver(reg).select(C.NEWS, max_cost="free")
    names = [p.name for p in selected]
    assert "wikipedia" in names                     # free
    discarded_names = {p.name: reason for p, reason in discarded}
    assert "reuters_archive" in discarded_names and "paid" in discarded_names["reuters_archive"]


# --- HTTP client -------------------------------------------------------------
def test_mapping_http_client_routes_and_404():
    http = _client()
    assert http.get("https://commons.wikimedia.org/w/api.php").json() == COMMONS
    assert http.get("https://unknown.example/x").status_code == 404


def test_real_http_client_constructs():
    # no hace red; solo comprobamos que se construye con sus políticas
    c = RealHttpClient(timeout=5.0)
    assert c._timeout == 5.0


# --- engine integración (real providers, HTTP mockeado) ----------------------
def _plan():
    profile = CaseProfile(case_id="zodiac", title="Zodiac Killer", genre="true_crime",
                          subject="Zodiac", people=["Arthur Leigh Allen"],
                          locations=["San Francisco"], events=["1969 attacks"])
    return EvidenceInvestigationPlanner().plan(profile)


def _real_registry():
    return SourceRegistry(real_providers(http=_client(), cache=DiscoveryCache())
                          + contract_providers())


def test_engine_with_real_providers_locates_and_audits():
    plan = _plan()
    dp = CaseDiscoveryEngine(registry=_real_registry()).discover(plan)
    assert dp.totals["discovered"] > 0
    # múltiples proveedores reales aportan material
    for provider in ("wikimedia_commons", "openstreetmap", "wikidata", "wikipedia"):
        assert provider in dp.by_provider
    # auditoría: decisiones con motivo por necesidad
    some = next(n for n in dp.needs if n.provider_decisions)
    assert any(d["selected"] and d["results"] >= 0 for d in some.provider_decisions)

    manifest = build_manifest(plan, dp)
    assert manifest.provider_audit and all("results" in a for a in manifest.provider_audit)
    ev = manifest.entries[0]
    assert ev.query_used and ev.selection_reason       # autocontenida + auditable


def test_engine_real_is_deterministic():
    plan = _plan()
    a = CaseDiscoveryEngine(registry=_real_registry()).discover(plan)
    b = CaseDiscoveryEngine(registry=_real_registry()).discover(plan)
    assert a.to_dict() == b.to_dict()                  # timings excluidos → reproducible
