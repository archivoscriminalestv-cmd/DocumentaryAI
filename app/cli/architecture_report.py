"""Genera el modelo arquitectónico de DocumentaryAI (DCA-001).

    python -m app.cli.architecture_report

Escribe en ``output/dca/``: architecture.json · capability_graph.json ·
dependency_graph.json · roadmap.json · recommendations.json · architecture_report.md
Solo lectura, determinista, sin IA. No ejecuta ni modifica ningún motor.
"""

import argparse
import os
import sys

from app.dca.orchestrator import DocumentaryChiefArchitect
from app.dca.persistence import write_outputs


def run(root: str = ".", out_dir: str | None = None) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    out_dir = out_dir or os.path.join("output", "dca")
    architect = DocumentaryChiefArchitect(root=root)
    paths = write_outputs(out_dir, architect)

    snap = architect.snapshot()
    cov = snap.architecture.coverage
    print(f"DocumentaryAI — {snap.totals['subsystems']} subsistemas · "
          f"{snap.totals['domains']} dominios · {snap.totals['capabilities']} capacidades")
    print(f"Implementados: {cov.get('implemented', 0)}/{cov.get('total_subsystems', 0)} "
          f"({cov.get('implemented_percent', 0) * 100:.0f}%)  ·  huecos: {snap.totals['gaps']} "
          f"· ciclos: {snap.totals['cycles']} · aislados: {snap.totals['isolated']}")
    for rec in architect.recommend()[:5]:
        print(f"  #{rec.priority_rank} {rec.title}")
    for name, path in paths.items():
        print(f"  {name:26} -> {path}")
    return {"paths": paths}


def main() -> None:
    p = argparse.ArgumentParser(description="DocumentaryAI Chief Architect (DCA).")
    p.add_argument("--root", default=".", help="raíz del repositorio (para leer docs públicos)")
    p.add_argument("--out", default=None, help="directorio de salida (def. output/dca)")
    args = p.parse_args()
    run(args.root, args.out)


if __name__ == "__main__":
    main()
