"""Persistencia del Investigation Plan (EAE-002) — reproducible, sin timestamps.

Cada plan se guarda como JSON en ``output/eae/plans/<case_id>/plan.json``. Nunca en
``knowledge/``. Solo planificación (sin binarios).
"""

import json
import os

from app.eae.planner.models import InvestigationPlan


def _guard(out_dir: str) -> None:
    if "knowledge" in os.path.normpath(out_dir).split(os.sep):
        raise ValueError("El planner del EAE nunca debe escribir dentro de knowledge/")


def write_plan(plan: InvestigationPlan,
               out_dir: str = os.path.join("output", "eae", "plans")) -> dict[str, str]:
    _guard(out_dir)
    plan_dir = os.path.join(out_dir, plan.case_id)
    os.makedirs(plan_dir, exist_ok=True)
    plan_path = os.path.join(plan_dir, "plan.json")
    with open(plan_path, "w", encoding="utf-8") as h:
        json.dump(plan.to_dict(), h, ensure_ascii=False, indent=2, sort_keys=True)
    return {"plan": plan_path}


def load_plan(path: str) -> dict:
    with open(path, encoding="utf-8") as h:
        return json.load(h)
