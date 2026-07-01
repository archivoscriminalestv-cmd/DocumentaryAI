"""Genera las decisiones de generación a partir del conocimiento aprendido (KBG-001).

    python -m app.cli.generation_knowledge --genre true_crime

Escribe ``output/kbg/GenerationKnowledge.json`` + report. Solo lectura, determinista, sin
IA. No genera contenido: solo traduce conocimiento en parámetros de generación.
"""

import argparse
import os
import sys

from app.kbg.bridge import KnowledgeBridge
from app.kbg.persistence import write_outputs


def run(genre: str = "documentary_style", styles_root: str = os.path.join("knowledge", "styles"),
        ece_coverage: str = "", out_dir: str | None = None) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    out_dir = out_dir or os.path.join("output", "kbg")
    gk = KnowledgeBridge(styles_root=styles_root).build(genre=genre, ece_coverage_path=ece_coverage)
    paths = write_outputs(out_dir, gk)

    s = gk.summary
    print(f"GenerationKnowledge (género: {gk.genre}) — "
          f"{s['known']}/{s['total_decisions']} decisiones conocidas "
          f"({s['known_ratio'] * 100:.0f}%)")
    for section, st in s["by_section"].items():
        print(f"  {section:14} {st['known']}/{st['total']}")
    for name, path in paths.items():
        print(f"  {name:22} -> {path}")
    return {"generation_knowledge": gk, "paths": paths}


def main() -> None:
    p = argparse.ArgumentParser(description="Knowledge Bridge (KBG).")
    p.add_argument("--genre", default="documentary_style")
    p.add_argument("--styles-root", default=os.path.join("knowledge", "styles"))
    p.add_argument("--ece-coverage", default="", help="ruta a un coverage_report.json del ECE")
    p.add_argument("--out", default=None)
    args = p.parse_args()
    run(args.genre, args.styles_root, args.ece_coverage, args.out)


if __name__ == "__main__":
    main()
