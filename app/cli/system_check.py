"""Production Readiness del AIM (AIM-001).

    python -m app.cli.system_check

Comprueba todas las integraciones externas (learning/evidence/generation/knowledge): qué
proveedores hay, cuáles tienen credenciales, cuáles están integrados, qué capacidades ofrecen
y qué alternativos existen. Escribe en ``output/system/`` y muestra un informe. Solo lectura,
determinista; no descarga contenido (Health Check sin red por defecto).
"""

import argparse
import os
import sys

from app.aim.models import HealthState
from app.aim.orchestrator import APIIntegrationManager
from app.aim.persistence import write_outputs

_PENDING = {HealthState.NOT_INTEGRATED, HealthState.NO_CREDENTIALS}


def _mark(item) -> str:
    if item.ready:
        return "[Y]"
    if item.state in _PENDING:
        return "[~]"
    return "[ ]"


def run(root: str = ".", out_dir: str | None = None, probe: bool = False) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    out_dir = out_dir or os.path.join("output", "system")
    manager = APIIntegrationManager(root=root)
    report = manager.readiness(probe=probe)
    paths = write_outputs(out_dir, manager, probe=probe)

    print("=" * 40)
    print("DOCUMENTARY AI")
    print("Production Readiness")
    print("=" * 40)
    by_cat: dict[str, list] = {}
    for item in report.items:
        by_cat.setdefault(item.category, []).append(item)
    for category in ("learning", "evidence", "generation", "knowledge"):
        if category not in by_cat:
            continue
        print(f"\n{category.capitalize()}")
        for item in by_cat[category]:
            extra = "" if item.ready else f"   ({item.detail})"
            print(f"  {_mark(item)} {item.name}{extra}")

    s = report.summary
    print("\n" + "-" * 40)
    verdict = "READY FOR PRODUCTION" if s["production_ready"] else "NOT READY YET"
    print(f"{verdict}    {s['ready']} / {s['total']}   ·  pendientes: {s['pending']}")
    print("=" * 40)
    for name, path in paths.items():
        print(f"  {name:26} -> {path}")
    return {"report": report, "paths": paths}


def main() -> None:
    p = argparse.ArgumentParser(description="DocumentaryAI — Production Readiness (AIM).")
    p.add_argument("--root", default=".")
    p.add_argument("--out", default=None)
    p.add_argument("--probe", action="store_true",
                   help="hace una llamada mínima REAL a cada proveedor con credenciales (red)")
    args = p.parse_args()
    run(args.root, args.out, probe=args.probe)


if __name__ == "__main__":
    main()
