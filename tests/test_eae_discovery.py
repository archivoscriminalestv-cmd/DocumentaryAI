"""Tests del Case Discovery Engine + Workspace (EAE-003) — deterministas, sin red."""

import json
import os
from types import SimpleNamespace

from app.eae.discovery.engine import CaseDiscoveryEngine
from app.eae.discovery.manifest import build_manifest
from app.eae.discovery.providers.catalog import default_providers
from app.eae.discovery.providers.static import StaticCatalogProvider
from app.eae.discovery.registry import SourceRegistry, default_registry
from app.eae.discovery.resolver import SourceResolver
from app.eae.planner import CaseProfile, EvidenceInvestigationPlanner, InvestigationPlan
from app.eae.planner.models import EvidenceCategory as C
from app.eae.workspace import WorkspaceManager


def _plan(genre="true_crime"):
    profile = CaseProfile(case_id="case_x", title="Case X", genre=genre, subject="X",
                          people=["Person A"], locations=["Place B"], events=["Event C"])
    return EvidenceInvestigationPlanner().plan(profile)


def _static_registry():
    """Registro = contratos del catálogo + dos proveedores estáticos disponibles."""
    providers = default_providers() + [
        StaticCatalogProvider("demo_commons", media=(C.SCENE_PHOTO, C.PHOTO, C.MAP),
                              catalog=[{"category": C.SCENE_PHOTO, "count": 3, "license": "CC-BY"},
                                       {"category": C.PHOTO, "count": 2, "license": "PUBLIC_DOMAIN"},
                                       {"category": C.MAP, "count": 1, "license": "CC0"}],
                              priority=5),
        StaticCatalogProvider("demo_news", media=(C.NEWS,),
                              catalog=[{"category": C.NEWS, "count": 4, "license": "UNKNOWN"}],
                              priority=6, reliability="MEDIUM"),
    ]
    return SourceRegistry(providers)


# --- registro / resolver -----------------------------------------------------
def test_registry_sorted_and_by_media():
    reg = default_registry()
    names = [p.name for p in reg.all()]
    assert names == sorted(names, key=lambda n: (dict((p.name, p.priority()) for p in reg.all())[n], n))
    photo_sources = [p.name for p in reg.by_media(C.PHOTO)]
    assert "wikimedia_commons" in photo_sources and "library_of_congress" in photo_sources
    assert all(C.PHOTO in p.supported_media() for p in reg.by_media(C.PHOTO))


def test_registry_capabilities_declared():
    cap = next(c for c in default_registry().capabilities() if c["name"] == "internet_archive")
    assert cap["cost"] == "free" and cap["reliability"] == "HIGH"
    assert "search" in cap["capabilities"] and cap["available"] is False


def test_resolver_license_filter():
    reg = default_registry()
    res = SourceResolver(reg)
    # COURT_DOCUMENT: gobierno/archivos/juzgados públicos
    cands = [p.name for p in res.candidates(C.COURT_DOCUMENT)]
    assert "government" in cands and "public_court" in cands
    # filtro de licencia que nadie declara explícitamente -> no descarta (devuelve todos)
    assert res.candidates(C.COURT_DOCUMENT, ["CC-BY"]) == reg.by_media(C.COURT_DOCUMENT) \
        or len(res.candidates(C.COURT_DOCUMENT, ["CC-BY"])) >= 1


# --- engine: contratos (descubierto 0, candidatas pobladas) ------------------
def test_discover_with_contracts_is_pending_but_has_candidates():
    plan = _plan()
    dp = CaseDiscoveryEngine(registry=default_registry()).discover(plan)
    assert dp.totals["discovered"] == 0
    assert dp.totals["required"] > 0
    # cada necesidad de foto-de-escena tiene fuentes candidatas aunque no haya descargas
    scene = [n for n in dp.needs if n.category == C.SCENE_PHOTO]
    assert scene and all(n.state == "PENDING" for n in scene)
    assert any("wikimedia_commons" in n.candidate_providers for n in scene)


# --- engine: con proveedores estáticos (descubrimiento real) -----------------
def test_discover_with_static_providers_locates_evidence():
    plan = _plan()
    dp = CaseDiscoveryEngine(registry=_static_registry()).discover(plan)
    assert dp.totals["discovered"] > 0
    assert "demo_commons" in dp.sources_consulted and "demo_news" in dp.sources_consulted
    scene = dp.by_category.get(C.SCENE_PHOTO)
    assert scene and scene["discovered"] >= scene["required"] > 0
    # estados de cobertura coherentes
    covered = [n for n in dp.needs if n.state == "COVERED"]
    assert covered


def test_discover_is_deterministic():
    plan = _plan()
    a = CaseDiscoveryEngine(registry=_static_registry()).discover(plan)
    b = CaseDiscoveryEngine(registry=_static_registry()).discover(plan)
    assert a.to_dict() == b.to_dict()


# --- manifest ----------------------------------------------------------------
def test_manifest_entries_rich_and_no_download():
    plan = _plan()
    dp = CaseDiscoveryEngine(registry=_static_registry()).discover(plan)
    manifest = build_manifest(plan, dp)
    assert len(manifest.entries) == dp.totals["discovered"]
    entry = manifest.entries[0]
    assert entry.downloaded is False and entry.validated is False
    assert entry.provider and entry.chain_of_custody
    assert entry.permitted_use in ("free", "attribution_required", "UNKNOWN",
                                   "attribution_share_alike", "restricted")
    # relaciones: alguna entrada de SCENE_PHOTO apunta a la localización del caso
    scene_entries = [e for e in manifest.entries if e.category == C.SCENE_PHOTO]
    assert any("Place B" in e.related_locations for e in scene_entries)


# --- workspace ---------------------------------------------------------------
def test_workspace_create_size_and_finalize(tmp_path):
    mgr = WorkspaceManager(str(tmp_path / "projects"))
    ws = mgr.create("case_x")
    for sub in ("downloads", "photos", "videos", "documents", "audio", "maps", "news", "cache"):
        assert os.path.isdir(ws.path(sub))

    # simula un binario temporal + un metadato permanente
    with open(os.path.join(ws.path("photos"), "x.jpg"), "wb") as h:
        h.write(b"binary")
    meta = ws.metadata_path("manifest.json")
    with open(meta, "w", encoding="utf-8") as h:
        h.write("{}")
    assert mgr.size(ws) >= 6

    freed = mgr.finalize(ws)
    assert freed >= 6
    assert not os.path.exists(ws.workspace_dir)        # binarios eliminados
    assert os.path.exists(meta)                        # metadatos conservados


def test_workspace_clean_cache(tmp_path):
    mgr = WorkspaceManager(str(tmp_path / "projects"))
    ws = mgr.create("c")
    with open(os.path.join(ws.path("cache"), "tmp.bin"), "wb") as h:
        h.write(b"xx")
    mgr.clean_cache(ws)
    assert os.path.isdir(ws.path("cache")) and not os.listdir(ws.path("cache"))


# --- plan round-trip ---------------------------------------------------------
def test_plan_from_dict_roundtrip():
    plan = _plan()
    restored = InvestigationPlan.from_dict(plan.to_dict())
    a = CaseDiscoveryEngine(registry=_static_registry()).discover(plan)
    b = CaseDiscoveryEngine(registry=_static_registry()).discover(restored)
    assert a.to_dict() == b.to_dict()


# --- CLI ---------------------------------------------------------------------
def test_cli_case_discovery_writes_metadata_no_binaries(tmp_path):
    import app.cli.case_discovery as cli

    args = SimpleNamespace(
        case_id="case_x", title="Case X", genre="true_crime", subject="X",
        person=["Person A"], location=["Place B"], event=["Event C"], license=[],
        profile=None, plan=None, output_dir=str(tmp_path / "projects"))
    result = cli.run(args, registry=_static_registry())

    proj = os.path.join(str(tmp_path / "projects"), "case_x")
    for name in ("manifest.json", "sources.json", "timeline.json", "verification.json",
                 "report.json", "discovery_report.md"):
        assert os.path.exists(os.path.join(proj, name))

    report = json.load(open(os.path.join(proj, "report.json"), encoding="utf-8"))
    assert report["totals"]["discovered"] > 0
    # workspace creado pero SIN binarios
    ws_dir = os.path.join(proj, "workspace")
    assert os.path.isdir(ws_dir)
    for base, _dirs, files in os.walk(ws_dir):
        assert files == []                              # nada descargado
