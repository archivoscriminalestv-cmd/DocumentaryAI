"""Limpia de la cola los elementos terminados (FINISHED/SKIPPED) (DLE-002).

    python -m app.cli.queue_clear_finished

El conocimiento aprendido NO se borra (vive en knowledge/); solo se limpia la cola.
"""

import sys

from app.dle.queue import LearningQueueManager


def run() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    mgr = LearningQueueManager()
    n = mgr.clear_finished()
    s = mgr.status()
    print(f"[queue] {n} elementos terminados eliminados de la cola  ·  "
          f"restantes: {s['total_in_queue']} (pendientes {s['pending']})")
    print("(El conocimiento aprendido permanece en knowledge/.)")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
