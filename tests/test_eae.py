"""Tests del Evidence Acquisition Engine (EAE-001, foundation) — deterministas, sin red."""

import json
import os

import pytest

from app.eae import (
    NOT_IMPLEMENTED,
    UNKNOWN,
    Evidence,
    EvidenceAcquisitionEngine,
    EvidenceCase,
    EvidenceKind,
    EvidenceQuery,
    EvidenceSource,
    VerificationStatus,
)
from app.eae.deduplication import BaseEvidenceDeduplicator, DeduplicationStrategy
from app.eae.models import EvidenceMetadata, EvidencePerson, EvidenceReference
from app.eae.persistence import write_case
from app.eae.providers import default_providers
from app.eae.providers.base import BaseEvidenceProvider
from app.eae.storage import LIBRARY_LAYOUT, BaseEvidenceStorage
from app.eae.verification import BaseEvidenceVerifier


# --- modelos: tipados, serializables, con origen ----------------------------

def test_evidence_serialization_roundtrip():
    ev = Evidence(id="ev1", kind=EvidenceKind.PHOTO,
                  metadata=EvidenceMetadata(title="t", date="1969"),
                  source=EvidenceSource(provider="wikimedia", url="http://x"))
    d = ev.to_dict()
    assert d["kind"] == "photo" and d["source"]["provider"] == "wikimedia"
    assert d["schema_version"] and d["verification"]["status"] == VerificationStatus.UNVERIFIED


def test_evidence_always_has_source_field():
    ev = Evidence(id="ev2")
    assert hasattr(ev, "source") and ev.source.provider == ""   # origen siempre presente


def test_case_serialization():
    case = EvidenceCase(case_id="c1", title="Caso",
                        people=[EvidencePerson(id="p1", name="X")])
    d = case.to_dict()
    assert d["case_id"] == "c1" and d["people"][0]["name"] == "X"
    assert "timeline" in d and "evidence" in d and "sources" in d


# --- proveedores: contrato (sin red) -----------------------------------------

def test_providers_implement_contract():
    provs = default_providers()
    assert len(provs) == 7
    names = {p.name for p in provs}
    assert {"youtube", "wikimedia", "internet_archive", "news",
            "government", "wayback", "future"} <= names
    for p in provs:
        assert p.available() is False              # aún no implementado
        assert p.search(EvidenceQuery(case_id="c")) == []   # sin red


def test_provider_fetch_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseEvidenceProvider().fetch(EvidenceReference(evidence_id="x"))


# --- verificación: contrato (no calcula) -------------------------------------

def test_verifier_returns_unverified():
    v = BaseEvidenceVerifier().verify(Evidence(id="e"))
    assert v.status == VerificationStatus.UNVERIFIED
    assert v.confidence == UNKNOWN and v.source_verified == UNKNOWN
    assert v.chain_of_custody                       # arranca la cadena de custodia


# --- deduplicación: contrato (UNKNOWN, nunca inventa) ------------------------

def test_deduplicator_unknown():
    d = BaseEvidenceDeduplicator()
    assert d.is_duplicate(Evidence(id="a"), [Evidence(id="b")]) == UNKNOWN
    assert d.find_duplicates([Evidence(id="a")]) == []
    assert set(DeduplicationStrategy.ALL) == {
        "perceptual_hash", "exact_hash", "metadata_hash", "source_identity"}


# --- almacenamiento: estructura + nunca knowledge/ + no escribe binarios -----

def test_storage_layout_structure():
    layout = BaseEvidenceStorage(root="output/eae").layout()
    assert set(LIBRARY_LAYOUT) <= set(layout["case_subdirs"])
    assert {"people", "photos", "videos", "documents", "maps", "articles",
            "social", "metadata", "timeline", "locations"} <= set(layout["case_subdirs"])


def test_storage_plans_path_by_kind_without_writing(tmp_path):
    storage = BaseEvidenceStorage(root=str(tmp_path / "eae"))
    path = storage.planned_path("c1", Evidence(id="ev", kind=EvidenceKind.VIDEO))
    assert "videos" in path and path.endswith("ev")
    assert not os.path.exists(path)                 # contrato: no escribe binarios


def test_storage_refuses_knowledge():
    with pytest.raises(ValueError):
        BaseEvidenceStorage(root=os.path.join("knowledge", "eae"))


# --- orquestador: solo coordina, determinista --------------------------------

def test_engine_acquire_returns_case_deterministic():
    q = EvidenceQuery(case_id="case_x", subject="Tesla")
    a = EvidenceAcquisitionEngine().acquire(q).to_dict()
    b = EvidenceAcquisitionEngine().acquire(q).to_dict()
    assert a == b
    assert a["case_id"] == "case_x" and a["evidence"] == []   # sin descarga real
    assert any("Proveedores consultados" in n for n in a["notes"])


def test_engine_provider_failure_does_not_break():
    class _Boom(BaseEvidenceProvider):
        name = "boom"

        def search(self, query):
            raise RuntimeError("no")

    eng = EvidenceAcquisitionEngine(providers=[_Boom()])
    case = eng.acquire(EvidenceQuery(case_id="c"))
    assert isinstance(case, EvidenceCase)            # no rompe


# --- persistencia: output/eae, nunca knowledge/ ------------------------------

def test_persistence_writes_case_outside_knowledge(tmp_path):
    case = EvidenceCase(case_id="c1", title="Caso")
    out = str(tmp_path / "output" / "eae")
    paths = write_case(case, out_dir=out)
    assert os.path.exists(paths["case"]) and "case.json" in paths["case"]
    data = json.loads(open(paths["case"], encoding="utf-8").read())
    assert data["case_id"] == "c1"


def test_persistence_refuses_knowledge():
    with pytest.raises(ValueError):
        write_case(EvidenceCase(case_id="c"), out_dir=os.path.join("knowledge", "eae"))


# --- sin red / sin scraping / sin azar ---------------------------------------

def test_no_network_or_scraping_imports():
    import importlib
    import pkgutil

    import app.eae as pkg
    forbidden = ("requests", "bs4", "selenium", "playwright", "httpx", "urllib3", "random")
    for mod in pkgutil.walk_packages(pkg.__path__, prefix="app.eae."):
        source = importlib.import_module(mod.name)
        for name in forbidden:
            assert name not in getattr(source, "__dict__", {}), f"{mod.name} importa {name}"
