"""Persistencia del subsistema de protección (INF-001).

Escribe los artefactos en ``output/system/`` (reproducible, sort_keys). NUNCA en ``knowledge/``.
Solo metadatos/planes/hashes; jamás binarios.
"""

import json
import os

from app.infra.models import ProjectSnapshot

DEFAULT_OUT = os.path.join("output", "system")


def _guard(out_dir: str) -> None:
    if "knowledge" in os.path.normpath(out_dir).split(os.sep):
        raise ValueError("INF nunca debe escribir dentro de knowledge/")


def _write(out_dir: str, name: str, data: dict) -> str:
    _guard(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as h:
        json.dump(data, h, ensure_ascii=False, indent=2, sort_keys=True)
    return path


def write_snapshot_bundle(snapshot: ProjectSnapshot, out_dir: str = DEFAULT_OUT) -> dict[str, str]:
    """Escribe los seis artefactos estándar del sprint a partir de un ProjectSnapshot."""
    paths = {}
    if snapshot.manifest:
        paths["project_manifest"] = _write(out_dir, "project_manifest.json",
                                           snapshot.manifest.to_dict())
    if snapshot.knowledge:
        paths["knowledge_snapshot"] = _write(out_dir, "knowledge_snapshot.json",
                                             snapshot.knowledge.to_dict())
    if snapshot.backup_plan:
        paths["backup_plan"] = _write(out_dir, "backup_plan.json",
                                      snapshot.backup_plan.to_dict())
    if snapshot.integrity:
        paths["integrity_report"] = _write(out_dir, "integrity_report.json",
                                           snapshot.integrity.to_dict())
    if snapshot.restore_plan:
        paths["restore_plan"] = _write(out_dir, "restore_plan.json",
                                       snapshot.restore_plan.to_dict())
    paths["project_snapshot"] = _write(out_dir, "project_snapshot.json", snapshot.to_dict())
    return paths


def load_manifest(path: str) -> dict:
    with open(path, encoding="utf-8") as h:
        return json.load(h)
