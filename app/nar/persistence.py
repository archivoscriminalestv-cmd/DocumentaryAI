"""Persistencia del NarrativeBlueprint (NAR-001) — reproducible, sin timestamps.

Se guarda en ``output/narrative/<case_id>/blueprint.json``. NUNCA en ``knowledge/``.
"""

import json
import os

from app.nar.models import NarrativeBlueprint


def _guard(out_dir: str) -> None:
    if "knowledge" in os.path.normpath(out_dir).split(os.sep):
        raise ValueError("El NAR nunca debe escribir dentro de knowledge/")


def write_blueprint(blueprint: NarrativeBlueprint,
                    out_dir: str = os.path.join("output", "narrative")) -> dict[str, str]:
    _guard(out_dir)
    case_dir = os.path.join(out_dir, blueprint.case_id)
    os.makedirs(case_dir, exist_ok=True)
    path = os.path.join(case_dir, "blueprint.json")
    with open(path, "w", encoding="utf-8") as h:
        json.dump(blueprint.to_dict(), h, ensure_ascii=False, indent=2, sort_keys=True)
    return {"blueprint": path}


def load_blueprint(path: str) -> dict:
    with open(path, encoding="utf-8") as h:
        return json.load(h)
