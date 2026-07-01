"""Persistencia del EAE (EAE-001) — reproducible, sin marcas de tiempo.

Serializa un ``EvidenceCase`` a JSON. Nunca escribe en ``knowledge/`` (raíz por defecto
``output/eae/``). Reproducible (``sort_keys``); sin información efímera.
"""

import json
import os

from app.eae.models import EvidenceCase


def _guard(out_dir: str) -> None:
    if "knowledge" in os.path.normpath(out_dir).split(os.sep):
        raise ValueError("El EAE nunca debe escribir dentro de knowledge/")


def write_case(case: EvidenceCase, out_dir: str = os.path.join("output", "eae")) -> dict[str, str]:
    _guard(out_dir)
    case_dir = os.path.join(out_dir, "cases", case.case_id)
    os.makedirs(case_dir, exist_ok=True)
    case_path = os.path.join(case_dir, "case.json")
    with open(case_path, "w", encoding="utf-8") as h:
        json.dump(case.to_dict(), h, ensure_ascii=False, indent=2, sort_keys=True)
    return {"case": case_path}


def load_case(path: str) -> dict:
    with open(path, encoding="utf-8") as h:
        return json.load(h)
