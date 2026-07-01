"""Integrity Checker (INF-001) — comprueba que el proyecto está sano y completo.

Detecta: carpetas críticas inexistentes, archivos faltantes, documentación perdida, conocimiento
corrupto y (si se le da un manifiesto previo) hashes distintos. Solo lectura, determinista.
"""

import json
import os

from app.infra.manifest import rel, sha256_file
from app.infra.models import Health, IntegrityIssue, IntegrityReport

_CRITICAL_FOLDERS = ("app", "docs", "knowledge", "tests")
_CRITICAL_FILES = ("main.py",)
_EITHER = (("requirements.txt", "pyproject.toml"),)   # al menos uno
_KEY_DOC_DIRS = ("docs/adr",)
_KEY_DOCS = ("docs/VISION.md",)


def _exists(root: str, relpath: str) -> bool:
    return os.path.exists(os.path.join(root, *relpath.split("/")))


def _knowledge_jsons(root: str) -> list[str]:
    out = [os.path.join(root, "knowledge", "learning_statistics.json")]
    styles = os.path.join(root, "knowledge", "styles")
    if os.path.isdir(styles):
        out += [os.path.join(styles, f) for f in sorted(os.listdir(styles)) if f.endswith(".json")]
    return out


def check_integrity(root: str = ".", baseline_manifest: dict | None = None) -> IntegrityReport:
    issues: list[IntegrityIssue] = []
    checked = 0

    # carpetas críticas
    for folder in _CRITICAL_FOLDERS:
        checked += 1
        if not _exists(root, folder):
            issues.append(IntegrityIssue("missing_folder", folder,
                                         "carpeta crítica inexistente", "ERROR"))

    # archivos críticos
    for f in _CRITICAL_FILES:
        checked += 1
        if not _exists(root, f):
            issues.append(IntegrityIssue("missing_file", f, "archivo crítico ausente", "ERROR"))
    for group in _EITHER:
        checked += 1
        if not any(_exists(root, f) for f in group):
            issues.append(IntegrityIssue("missing_file", " | ".join(group),
                                         "no existe ninguno de los archivos requeridos", "ERROR"))

    # documentación
    for d in _KEY_DOC_DIRS:
        checked += 1
        full = os.path.join(root, *d.split("/"))
        if not os.path.isdir(full) or not any(f.endswith(".md") for f in os.listdir(full)):
            issues.append(IntegrityIssue("missing_doc", d, "documentación clave perdida", "WARNING"))
    for d in _KEY_DOCS:
        checked += 1
        if not _exists(root, d):
            issues.append(IntegrityIssue("missing_doc", d, "documento clave ausente", "WARNING"))

    # conocimiento corrupto (debe parsear como JSON)
    for p in _knowledge_jsons(root):
        checked += 1
        if not os.path.isfile(p):
            issues.append(IntegrityIssue("missing_file", rel(root, p),
                                         "artefacto de conocimiento ausente", "ERROR"))
            continue
        try:
            with open(p, encoding="utf-8") as fh:
                json.load(fh)
        except (OSError, ValueError) as exc:
            issues.append(IntegrityIssue("corrupt_knowledge", rel(root, p),
                                         f"JSON ilegible: {type(exc).__name__}", "ERROR"))

    # comparación de hashes contra un manifiesto previo (opcional)
    baseline_used = False
    if baseline_manifest:
        baseline_used = True
        for art in baseline_manifest.get("artifact_hashes", []) or []:
            checked += 1
            relpath = art.get("path", "")
            abspath = os.path.join(root, *relpath.split("/"))
            if not os.path.isfile(abspath):
                issues.append(IntegrityIssue("missing_file", relpath,
                                             "presente en el backup, ausente ahora", "ERROR"))
                continue
            if sha256_file(abspath) != art.get("sha256"):
                issues.append(IntegrityIssue("hash_mismatch", relpath,
                                             "el contenido cambió respecto al manifiesto", "WARNING"))

    report = IntegrityReport(checked=checked, issues=issues, baseline_used=baseline_used)
    report.health = _health(report)
    return report


def _health(report: IntegrityReport) -> str:
    critical = report.by_kind("missing_folder") or report.by_kind("corrupt_knowledge")
    if critical:
        return Health.CRITICAL
    if report.errors or report.warnings:
        return Health.DEGRADED
    return Health.OK
