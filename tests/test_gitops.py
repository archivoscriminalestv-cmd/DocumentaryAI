"""Tests del Git Sanitizer (INF-003) — deterministas. Unidades sin git; una integración con git
real guardada por disponibilidad. Nunca hacen commit/push.
"""

import os
import shutil
import subprocess

import pytest

from app.gitops import gitignore_manager, large_files, secrets
from app.gitops.classifier import classify
from app.gitops.models import FileCategory as C


# --- clasificador ------------------------------------------------------------

def test_classifier_categories():
    assert classify("output/final/documentary.mp4") == C.OUTPUT
    assert classify("outputs/x.png") == C.OUTPUT
    assert classify("app/nar/engine.py") == C.SOURCE
    assert classify("tests/test_x.py") == C.SOURCE
    assert classify("docs/adr/ADR-0001.md") == C.SOURCE
    assert classify("knowledge/styles/a.json") == C.KNOWLEDGE
    assert classify("datasets/youtube/urls.txt") == C.DATASET
    assert classify("config/settings.py") == C.CONFIG
    assert classify("pyproject.toml") == C.CONFIG
    assert classify(".github/workflows/ci.yml") == C.CONFIG
    assert classify("__pycache__/x.pyc") == C.CACHE
    assert classify("app/x.pyc") == C.CACHE
    assert classify("cache/blob") == C.TEMPORARY
    assert classify("library/assets/a.png") == C.GENERATED
    assert classify("channel_intro.mp4") == C.BINARIES
    assert classify("assets/fallback/gray.mp4") == C.BINARIES


# --- .gitignore manager (idempotente, no destructivo) ------------------------

def test_gitignore_missing_and_write(tmp_path):
    gi = tmp_path / ".gitignore"
    gi.write_text("__pycache__/\n.env\noutputs/\n", encoding="utf-8")
    missing = gitignore_manager.missing_entries(str(gi))
    assert "output/" in missing and "workspace/" in missing
    assert "outputs/" not in missing                       # ya presente, no se repite

    added = gitignore_manager.ensure_entries(str(gi), write=True)
    assert "output/" in added
    body = gi.read_text(encoding="utf-8")
    assert gitignore_manager.MANAGED_HEADER in body and "output/" in body
    # idempotente: segunda vez no añade nada
    assert gitignore_manager.ensure_entries(str(gi), write=True) == []


def test_gitignore_preserves_existing(tmp_path):
    gi = tmp_path / ".gitignore"
    gi.write_text("# mio\nmi_carpeta/\n", encoding="utf-8")
    gitignore_manager.ensure_entries(str(gi), write=True)
    body = gi.read_text(encoding="utf-8")
    assert "mi_carpeta/" in body                            # nunca borra lo del usuario


# --- archivos grandes (umbral 50/100 MB) -------------------------------------

def test_large_files_threshold(tmp_path, monkeypatch):
    monkeypatch.setattr(large_files, "WARN_BYTES", 1000)
    monkeypatch.setattr(large_files, "HARD_BYTES", 2000)
    big = tmp_path / "big.bin"
    big.write_bytes(b"x" * 2500)                            # supera el límite duro simulado
    small = tmp_path / "small.txt"
    small.write_bytes(b"x" * 10)
    found = large_files.scan(str(tmp_path), ["big.bin", "small.txt"], tree_scan=False)
    paths = {f.path: f for f in found}
    assert "big.bin" in paths and paths["big.bin"].blocks_push is True
    assert "small.txt" not in paths


# --- secretos (con filtrado de falsos positivos) -----------------------------

def _seed(tmp_path, rel, content):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return rel


def test_secret_detection_and_false_positives(tmp_path):
    rels = [
        _seed(tmp_path, "real_key.py", 'OPENAI="sk-abcdefghij0123456789ABCD"\n'),
        _seed(tmp_path, "env_name.py", 'requires_api_key="REPLICATE_API_TOKEN"\n'),
        _seed(tmp_path, "placeholder.env.example", 'API_KEY="your-key-here-please"\n'),
        _seed(tmp_path, "pk.txt", "-----BEGIN PRIVATE KEY-----\nabc\n"),
        _seed(tmp_path, "real_generic.py", "password = 'S3cr3tP4ssw0rd_1234'\n"),
    ]
    findings = secrets.scan(str(tmp_path), rels)
    by_path = {f.path: f for f in findings}
    assert by_path["real_key.py"].severity == "ERROR"
    assert by_path["pk.txt"].kind == "private_key"
    assert "real_generic.py" in by_path                    # asignación real → WARNING
    assert "env_name.py" not in by_path                    # nombre de variable, no secreto
    assert "placeholder.env.example" not in by_path        # placeholder, no secreto


# --- integración con git real (guardada) -------------------------------------

def _git(root, *args):
    subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)


@pytest.mark.skipif(not shutil.which("git"), reason="git no disponible")
def test_readiness_blocks_generated_then_clean(tmp_path):
    from app.gitops.readiness import build_readiness

    root = str(tmp_path)
    _git(root, "init", "-q")
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "m.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "big.txt").write_text("data\n", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=abc\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")

    rep = build_readiness(root)
    assert rep.git.is_repo is True
    assert C.OUTPUT in rep.category_counts                  # output/ se subiría → mal
    assert rep.ready_for_push is False
    assert any("generado" in b for b in rep.blockers)

    # sanear: ignorar output/
    gitignore_manager.ensure_entries(os.path.join(root, ".gitignore"), write=True)
    rep2 = build_readiness(root)
    assert C.OUTPUT not in rep2.category_counts            # ya no se subiría
    assert rep2.env_ignored is True
    assert rep2.ready_for_push is True                     # limpio
