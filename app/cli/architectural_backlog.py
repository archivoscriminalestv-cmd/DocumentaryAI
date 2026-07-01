"""CLI del Architectural Backlog (DCA-004).

Lee ``docs/roadmap/ARCHITECTURAL-BACKLOG.md`` mediante el DCA, lo valida y muestra un resumen.
Con ``--review <json>`` genera (y persiste) un BacklogProposal para un sprint, SIN reescribir el
documento humano (solo el desarrollador lo edita a mano).

Ejemplos:
    python -m app.cli.architectural_backlog
    python -m app.cli.architectural_backlog --validate
    python -m app.cli.architectural_backlog --review sprint_review.json
"""

import argparse
import json
import os

from app.dca.backlog.orchestrator import DEFAULT_BACKLOG_PATH
from app.dca.backlog.persistence import write_proposal, write_snapshot
from app.dca.orchestrator import DocumentaryChiefArchitect


def main() -> None:
    ap = argparse.ArgumentParser(description="Architectural Backlog (DCA-004).")
    ap.add_argument("--path", default=DEFAULT_BACKLOG_PATH)
    ap.add_argument("--validate", action="store_true", help="muestra incidencias de validación")
    ap.add_argument("--review", default=None, help="json con el resumen del sprint → propuesta")
    ap.add_argument("--snapshot", action="store_true", help="guarda snapshot interno del backlog")
    ap.add_argument("--out", default=os.path.join("output", "dca", "backlog"))
    args = ap.parse_args()

    dca = DocumentaryChiefArchitect()
    backlog = dca.backlog(path=args.path)
    counts = backlog.counts

    print(f"Architectural Backlog — {backlog.source_path}")
    print(f"  entradas: {counts['total']}")
    print(f"  por estado:    {counts['by_status']}")
    print(f"  por prioridad: {counts['by_priority']}")
    print(f"  por sección:   {counts['by_section']}")

    issues = dca.validate_backlog(path=args.path)
    errors = [i for i in issues if i.level == "ERROR"]
    warnings = [i for i in issues if i.level == "WARNING"]
    print(f"  validación: {len(errors)} errores · {len(warnings)} avisos")
    if args.validate:
        for i in issues:
            print(f"    [{i.level}] {i.entry_id}: {i.message}")

    if args.snapshot:
        paths = write_snapshot(backlog, out_dir=args.out)
        print(f"  snapshot -> {paths['snapshot']}")

    if args.review:
        with open(args.review, encoding="utf-8") as h:
            sprint_review = json.load(h)
        proposal = dca.review_backlog(sprint_review, path=args.path)
        paths = write_proposal(proposal, out_dir=args.out)
        print(f"\nPropuesta para sprint '{proposal.sprint}' (requiere aprobación manual):")
        print(f"  resueltos: {proposal.resolved}")
        for c in proposal.status_changes:
            mark = "" if c.accepted else "  (!) revisar"
            print(f"  estado: {c.entry_id} {c.from_status} -> {c.to_status}{mark}")
        for n in proposal.new_ideas:
            print(f"  idea nueva: [{n.section}/{n.status}] {n.title}")
        for r in proposal.related_to_add:
            print(f"  relacionar: {r['id']} -> {r['related']}")
        print(f"  proposal -> {paths['proposal']}")


if __name__ == "__main__":
    main()
