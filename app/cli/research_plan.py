"""Runner independiente del Research Planner (Sprint C-01).

Ejecuta SOLO la etapa de planificación (sin tubería, sin red, sin LLM) e imprime
el ``ResearchPlan`` como JSON.

    python -m app.cli.research_plan "The Fermi Paradox"
"""

import json
import sys
from dataclasses import asdict

from app.application.deterministic_planner import DeterministicPlanner


def run(topic: str) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    plan = DeterministicPlanner().create_plan(topic)
    print(json.dumps(asdict(plan), ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print('Uso: python -m app.cli.research_plan "<topic>"')
        raise SystemExit(2)
    run(" ".join(args))


if __name__ == "__main__":
    main()
