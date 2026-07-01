"""CLI del Narrative Intelligence Engine (NAR-001).

Construye el ``NarrativeBlueprint`` de un caso a partir de las salidas reales de los motores
previos (EAE/ECE en ``output/projects/<case>/`` + Generation Knowledge del KBG). NO descarga,
NO usa red, NO usa IA: solo decide CÓMO contar la historia.

Ejemplo:
    python -m app.cli.design_narrative --case-id madeleine_mccann --genre true_crime \
        --title "Madeleine McCann" --person "Madeleine McCann" --location "Praia da Luz" \
        --event disappearance
"""

import argparse
import os

from app.nar.engine import NarrativeIntelligenceEngine
from app.nar.inputs import NarrativeInputs
from app.nar.persistence import write_blueprint
from app.nar.report import render_markdown


def main() -> None:
    ap = argparse.ArgumentParser(description="Narrative Intelligence Engine (NAR).")
    ap.add_argument("--case-id", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--genre", default="true_crime")
    ap.add_argument("--subject", default="")
    ap.add_argument("--person", action="append", default=[])
    ap.add_argument("--location", action="append", default=[])
    ap.add_argument("--event", action="append", default=[])
    ap.add_argument("--case-dir", default=None,
                    help="dir con los JSON del caso (def: output/projects/<case_id>)")
    ap.add_argument("--generation-knowledge",
                    default=os.path.join("output", "kbg", "GenerationKnowledge.json"))
    ap.add_argument("--out", default=os.path.join("output", "narrative"))
    args = ap.parse_args()

    case_dir = args.case_dir or os.path.join("output", "projects", args.case_id)
    profile = {
        "case_id": args.case_id, "title": args.title or args.case_id, "genre": args.genre,
        "subject": args.subject, "people": args.person, "locations": args.location,
        "events": args.event,
    }
    gk = args.generation_knowledge if os.path.exists(args.generation_knowledge) else None
    context = NarrativeInputs.from_case_dir(profile, case_dir, generation_knowledge_path=gk)

    blueprint = NarrativeIntelligenceEngine().design(context)
    paths = write_blueprint(blueprint, out_dir=args.out)

    report_path = os.path.join(args.out, blueprint.case_id, "blueprint_report.md")
    with open(report_path, "w", encoding="utf-8") as h:
        h.write(render_markdown(blueprint))

    t = blueprint.totals
    print(f"NAR Blueprint ({args.case_id}) — estructura: {blueprint.structure}")
    print(f"  {t['segments']} segmentos · {t['acts']} actos · {t['total_suggested_seconds']}s · "
          f"arco {t['arc_type']} · pico {t['tension_peak']}")
    print(f"  reveals {t['reveals']} · hooks {t['hooks']} · foreshadows {t['foreshadows']} · "
          f"cliffhangers {t['cliffhangers']} · payoffs {t['payoffs']}")
    print(f"  preguntas abiertas {t['viewer_questions']} · recreaciones {t['recreations']} · "
          f"evidencias colocadas {t['evidence_placements']}")
    print(f"  dispositivos: {', '.join(d['type'] for d in blueprint.devices_applied) or '—'}")
    print(f"  entradas presentes: {', '.join(context.inputs_present)}")
    print(f"  blueprint -> {paths['blueprint']}")
    print(f"  report    -> {report_path}")


if __name__ == "__main__":
    main()
