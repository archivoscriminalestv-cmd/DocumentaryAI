"""Runner independiente del Research Executor (Sprint C-02).

Encadena planificación + ejecución (sin red, sin LLM) e imprime las SearchTasks
como JSON:

    python -m app.cli.research_tasks "The Fermi Paradox"
"""

import json
import sys
from dataclasses import asdict

from app.application.deterministic_planner import DeterministicPlanner
from app.application.executor_service import ExecutorService


def run(topic: str) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    plan = DeterministicPlanner().create_plan(topic)
    tasks = ExecutorService().execute(plan)
    print(json.dumps([asdict(t) for t in tasks], ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print('Uso: python -m app.cli.research_tasks "<topic>"')
        raise SystemExit(2)
    run(" ".join(args))


if __name__ == "__main__":
    main()
