"""Tests del subsistema de protección (INF-001) — deterministas, sin red, sin Git.

Usan un proyecto FALSO en tmp_path para aserciones exactas (el proyecto real cambia mientras se
aprende en segundo plano). Solo el proyecto real se usa para comprobaciones estructurales.
"""

import json
import os

import pytest

from app.infra.backup_manager import build_backup_plan
from app.infra.integrity import check_integrity
from app.infra.knowledge_snapshot import build_knowledge_snapshot
from app.infra.manifest import build_manifest
from app.infra.models import BackupClass, Health
from app.infra.persistence import write_snapshot_bundle
from app.infra.project_snapshot import build_project_snapshot
from app.infra.restore import build_restore_plan


def _fake_project(base) -> str:
    root = base / "proj"
    (root / "app" / "foo").mkdir(parents=True)
    (root / "app" / "foo" / "__init__.py").write_text("x = 1\n", encoding="utf-8")
    (root / "app" / "bar").mkdir()
    (root / "app" / "bar" / "__init__.py").write_text("y = 2\n", encoding="utf-8")
    (root / "docs" / "adr").mkdir(parents=True)
    (root / "docs" / "adr" / "ADR-0001-x.md").write_text("# adr\n", encoding="utf-8")
    (root / "docs" / "rfc").mkdir()
    (root / "docs" / "spec").mkdir()
    (root / "docs" / "spec" / "SPEC-0001.md").write_text("# spec\n", encoding="utf-8")
    (root / "docs" / "VISION.md").write_text("vision\n", encoding="utf-8")
    (root / "knowledge" / "styles").mkdir(parents=True)
    (root / "knowledge" / "styles" / "a.json").write_text('{"k": 1}', encoding="utf-8")
    (root / "knowledge" / "documentaries" / "d1").mkdir(parents=True)
    (root / "knowledge" / "learning_statistics.json").write_text(
        json.dumps({"documentaries_learned": 5, "shots_analyzed": 100,
                    "scenes": 40, "hours_learned": 2.5}), encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_x.py").write_text(
        "def test_a():\n    assert 1\n\ndef test_b():\n    assert 2\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (root / "main.py").write_text("print('x')\n", encoding="utf-8")
    return str(root)


# --- manifest ----------------------------------------------------------------

def test_manifest_on_fake_project(tmp_path):
    root = _fake_project(tmp_path)
    m = build_manifest(root, as_of="2026-01-01")
    assert m.generated_for_date == "2026-01-01"
    assert m.subsystem_count == 2 and set(m.engines) == {"foo", "bar"}
    assert m.adrs == ["ADR-0001-x.md"] and m.specs == ["SPEC-0001.md"] and m.rfcs == []
    assert m.test_count == 2
    assert m.documentaries_learned == 5 and m.shots_analyzed == 100
    assert m.scenes_analyzed == 40 and m.hours_learned == 2.5
    assert m.knowledge_size_bytes > 0 and m.project_size_bytes > 0
    assert m.artifact_hashes and all(len(a.sha256) == 64 for a in m.artifact_hashes)


def test_manifest_is_deterministic(tmp_path):
    root = _fake_project(tmp_path)
    a = json.dumps(build_manifest(root, as_of="2026-01-01").to_dict(), sort_keys=True)
    b = json.dumps(build_manifest(root, as_of="2026-01-01").to_dict(), sort_keys=True)
    assert a == b


def test_manifest_on_real_project_structural():
    m = build_manifest(".", as_of="2026-01-01")
    assert m.subsystem_count > 0 and m.test_count > 0
    assert isinstance(m.capability_count, int) or m.capability_count == "UNKNOWN"
    assert m.documentaries_learned >= 0


# --- knowledge snapshot ------------------------------------------------------

def test_knowledge_snapshot_only_knowledge(tmp_path):
    root = _fake_project(tmp_path)
    k = build_knowledge_snapshot(root)
    assert k.documentaries_learned == 5 and k.documentary_count == 1
    assert k.styles == ["a.json"] and k.style_hashes
    assert k.knowledge_size_bytes > 0
    # la política es explícita: solo conocimiento, nunca output/binarios
    assert "output" in k.note.lower() and "binarios" in k.note.lower()
    assert all("output" not in h.path and "knowledge" in h.path for h in k.style_hashes)


# --- backup plan -------------------------------------------------------------

def test_backup_plan_classification(tmp_path):
    root = _fake_project(tmp_path)
    (root_cache := os.path.join(root, "cache"))
    os.makedirs(root_cache)
    open(os.path.join(root_cache, "junk.bin"), "w").close()
    plan = build_backup_plan(root)

    crit = {e.path: e for e in plan.critical}
    assert crit["app"].exists and crit["app"].classification == BackupClass.CRITICAL
    assert crit["knowledge"].exists and crit["docs"].exists and crit["tests"].exists
    assert crit["app"].size_bytes > 0          # las críticas se miden

    temp = {e.path: e for e in plan.temporary}
    for t in ("cache", "workspace", "downloads", "render", "tmp"):
        assert t in temp and temp[t].classification == BackupClass.TEMPORARY
    assert temp["cache"].exists and temp["cache"].size_bytes == 0   # nunca se miden/copian

    imp = {e.path for e in plan.important}
    assert "output/dca" in imp and "output/kbg" in imp


# --- integrity ---------------------------------------------------------------

def test_integrity_healthy_project(tmp_path):
    root = _fake_project(tmp_path)
    rep = check_integrity(root)
    assert rep.health == Health.OK and rep.errors == 0


def test_integrity_missing_critical_folder(tmp_path):
    root = _fake_project(tmp_path)
    import shutil
    shutil.rmtree(os.path.join(root, "knowledge"))
    rep = check_integrity(root)
    assert rep.health == Health.CRITICAL
    assert any(i.kind == "missing_folder" and i.path == "knowledge" for i in rep.issues)


def test_integrity_corrupt_knowledge(tmp_path):
    root = _fake_project(tmp_path)
    (tmp_path / "proj" / "knowledge" / "styles" / "bad.json").write_text("{not json", encoding="utf-8")
    rep = check_integrity(root)
    assert rep.health == Health.CRITICAL
    assert any(i.kind == "corrupt_knowledge" for i in rep.issues)


def test_integrity_hash_mismatch_vs_baseline(tmp_path):
    root = _fake_project(tmp_path)
    baseline = build_manifest(root, as_of="2026-01-01").to_dict()
    # modificar un artefacto hasheado
    (tmp_path / "proj" / "pyproject.toml").write_text("[project]\nname='CHANGED'\n", encoding="utf-8")
    rep = check_integrity(root, baseline_manifest=baseline)
    assert rep.baseline_used
    assert any(i.kind == "hash_mismatch" for i in rep.issues)


# --- restore plan ------------------------------------------------------------

def test_restore_plan(tmp_path):
    root = _fake_project(tmp_path)
    rp = build_restore_plan(root)
    orders = [s.order for s in rp.steps]
    assert orders == sorted(orders) and len(rp.steps) >= 6
    for t in ("workspace", "render", "downloads", "tmp", "cache"):
        assert t in rp.do_not_restore
    assert rp.requirements_file in ("requirements.txt", "pyproject.toml")


# --- project snapshot + persistence ------------------------------------------

def test_project_snapshot_ready_for_backup(tmp_path):
    root = _fake_project(tmp_path)
    snap = build_project_snapshot(root, as_of="2026-01-01")
    assert snap.health == Health.OK and snap.ready_for_backup is True
    assert snap.manifest and snap.knowledge and snap.backup_plan
    assert snap.integrity and snap.restore_plan


def test_persistence_writes_six_files(tmp_path):
    root = _fake_project(tmp_path)
    snap = build_project_snapshot(root, as_of="2026-01-01")
    out = str(tmp_path / "out" / "system")
    paths = write_snapshot_bundle(snap, out_dir=out)
    for key in ("project_manifest", "knowledge_snapshot", "project_snapshot",
                "backup_plan", "integrity_report", "restore_plan"):
        assert os.path.exists(paths[key])


def test_persistence_refuses_knowledge(tmp_path):
    root = _fake_project(tmp_path)
    snap = build_project_snapshot(root, as_of="2026-01-01")
    with pytest.raises(ValueError):
        write_snapshot_bundle(snap, out_dir=os.path.join("knowledge", "system"))


# --- sin red / sin Git / sin IA ----------------------------------------------

def test_no_network_git_or_ai_imports():
    import importlib
    import pkgutil

    import app.infra as pkg
    forbidden = ("requests", "httpx", "urllib", "socket", "git", "subprocess",
                 "openai", "anthropic", "datetime")
    for mod in pkgutil.walk_packages(pkg.__path__, prefix="app.infra."):
        source = importlib.import_module(mod.name)
        for name in forbidden:
            assert name not in getattr(source, "__dict__", {}), f"{mod.name} importa {name}"
