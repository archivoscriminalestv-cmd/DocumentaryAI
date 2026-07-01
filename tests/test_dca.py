"""Tests del DocumentaryAI Chief Architect (DCA-001) — deterministas, solo lectura."""

import json
import os

from app.dca.analyzer import detect_gaps
from app.dca.architecture_reader import ArchitectureReader
from app.dca.capability_graph import build_capabilities
from app.dca.dependency_graph import analyze_dependencies, find_cycles
from app.dca.orchestrator import DocumentaryChiefArchitect
from app.dca.persistence import write_outputs
from app.dca.registry import build_subsystems


def _names(subsystems):
    return [s.name for s in subsystems]


# --- registry ----------------------------------------------------------------
def test_registry_lists_core_engines_sorted():
    subs = build_subsystems()
    names = _names(subs)
    assert names == sorted(names)
    for engine in ("DLE", "DKS", "YIE", "EAE", "ECE", "VIS", "VAI", "VPL", "Composer"):
        assert engine in names


# --- capabilities ------------------------------------------------------------
def test_capability_producers_and_consumers():
    caps = {c.name: c for c in build_capabilities(build_subsystems())}
    assert caps["cinematographic_knowledge"].producers == ["DLE"]
    assert "DKS" in caps["cinematographic_knowledge"].consumers
    assert caps["generated_assets"].producers == ["VPL"]


# --- dependencies ------------------------------------------------------------
def test_dependency_graph_acyclic_and_transitive():
    subs = build_subsystems()
    deps = analyze_dependencies(subs)
    assert deps["cycles"] == []                       # arquitectura acíclica
    edges = {(e["source"], e["target"]) for e in deps["edges"]}
    assert ("ECE", "EAE") in edges and ("VAI", "VIS") in edges
    # Composer depende transitivamente de VSC/VAI/VIS
    assert "VIS" in deps["transitive"]["Composer"]


def test_isolated_engines_detected():
    deps = analyze_dependencies(build_subsystems())
    assert "VUE" in deps["isolated"]                  # implementado pero no integrado


def test_find_cycles_detects_injected_cycle():
    from app.dca.models import Subsystem
    a = Subsystem("A", dependencies=["B"])
    b = Subsystem("B", dependencies=["A"])
    assert find_cycles([a, b])                        # detecta el ciclo


# --- architecture reader (docs públicos, raíz inyectable) --------------------
def test_reader_lists_public_docs(tmp_path):
    os.makedirs(tmp_path / "docs" / "adr")
    os.makedirs(tmp_path / "docs" / "rfc")
    os.makedirs(tmp_path / "app" / "dca")
    (tmp_path / "docs" / "adr" / "ADR-0001.md").write_text("x", encoding="utf-8")
    (tmp_path / "docs" / "rfc" / "RFC-0001.md").write_text("x", encoding="utf-8")
    (tmp_path / "app" / "dca" / "README.md").write_text("x", encoding="utf-8")
    idx = ArchitectureReader(str(tmp_path)).docs_index()
    assert idx["counts"]["adr"] == 1 and idx["counts"]["rfc"] == 1
    assert "dca" in idx["subsystem_readmes"]


# --- analyzer ----------------------------------------------------------------
def test_gaps_include_not_integrated_and_knowledge_unused():
    gaps = detect_gaps(build_subsystems())
    kinds = {g.kind for g in gaps}
    assert "not_integrated" in kinds                  # VUE
    assert "knowledge_unused" in kinds                # conocimiento no aprovechado
    vue = [g for g in gaps if g.kind == "not_integrated" and "VUE" in g.related]
    assert vue


def test_missing_capability_detected():
    gaps = detect_gaps(build_subsystems())
    missing = {g.id for g in gaps if g.kind == "missing_capability"}
    # 'narration' la consume Composer y no la produce ningún motor del registry
    assert any("narration" in m for m in missing)


# --- roadmap -----------------------------------------------------------------
def test_roadmap_is_deterministic_and_ranked():
    arch = DocumentaryChiefArchitect()
    r1 = arch.roadmap()
    r2 = arch.roadmap()
    assert r1.to_dict() == r2.to_dict()
    ranks = [i.priority_rank for i in r1.items]
    assert ranks == list(range(1, len(ranks) + 1))    # 1..n, sin huecos


# --- orchestrator ------------------------------------------------------------
def test_snapshot_is_deterministic_with_coverage():
    arch = DocumentaryChiefArchitect()
    s1 = arch.snapshot().to_dict()
    s2 = arch.snapshot().to_dict()
    assert s1 == s2
    cov = arch.architecture().coverage
    assert 0.0 < cov["implemented_percent"] <= 1.0
    assert cov["total_subsystems"] == len(build_subsystems())


def test_analyze_returns_engines_and_gaps():
    analysis = DocumentaryChiefArchitect().analyze()
    assert analysis["engines"] and analysis["gaps"]
    assert analysis["cycles"] == []
    assert "VUE" in analysis["isolated"]


# --- persistence -------------------------------------------------------------
def test_persistence_writes_all_outputs(tmp_path):
    arch = DocumentaryChiefArchitect()
    paths = write_outputs(str(tmp_path / "dca"), arch)
    for name in ("architecture.json", "capability_graph.json", "dependency_graph.json",
                 "roadmap.json", "recommendations.json", "architecture_report.md"):
        assert os.path.exists(paths[name])
    data = json.load(open(paths["architecture.json"], encoding="utf-8"))
    assert data["totals"]["subsystems"] >= 9
    assert data["architecture"]["coverage"]["implemented_percent"] > 0
