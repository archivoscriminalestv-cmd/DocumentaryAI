"""Persistencia del ECE: escribe los 4 artefactos de correlación (reproducibles).

En el directorio del proyecto: evidence_graph.json · coverage_report.json · conflicts.json
· recreation_candidates.json. ``sort_keys`` para reproducibilidad; sin marcas de tiempo.
"""

import json
import os


def _dump(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)


def write_correlation_outputs(project_dir: str, result) -> dict[str, str]:
    os.makedirs(project_dir, exist_ok=True)
    paths = {
        "evidence_graph.json": os.path.join(project_dir, "evidence_graph.json"),
        "coverage_report.json": os.path.join(project_dir, "coverage_report.json"),
        "conflicts.json": os.path.join(project_dir, "conflicts.json"),
        "recreation_candidates.json": os.path.join(project_dir, "recreation_candidates.json"),
    }
    _dump(paths["evidence_graph.json"], result.graph.to_dict())
    _dump(paths["coverage_report.json"], result.coverage.to_dict())
    _dump(paths["conflicts.json"], {"conflicts": [c.to_dict() for c in result.conflicts]})
    _dump(paths["recreation_candidates.json"],
          {"recreation_candidates": [r.to_dict() for r in result.recreation_candidates]})
    return paths
