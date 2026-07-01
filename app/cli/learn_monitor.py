"""Procesa la cola de aprendizaje mostrando el progreso EN VIVO (DLE-003).

    python -m app.cli.learn_monitor              # procesa toda la cola con monitor
    python -m app.cli.learn_monitor --limit 10   # procesa como mucho 10

El monitor solo escucha eventos públicos de progreso; no inspecciona estado interno.
La salida se repinta en el sitio (sin ensuciar la terminal).
"""

import argparse
import sys

from app.dle.monitor.monitor import LearningMonitor
from app.dle.monitor.render import LiveDisplay, render
from app.dle.queue import LearningQueueManager


def run(limit: int | None = None, *, manager: LearningQueueManager | None = None,
        display: LiveDisplay | None = None) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    mgr = manager or LearningQueueManager()
    monitor = LearningMonitor()
    display = display or LiveDisplay()

    def sink(event) -> None:
        state = monitor.handle(event)
        display.update(render(state))

    result = mgr.process_all(limit=limit, on_event=sink)
    s = result["status"]
    print(f"\n[monitor] procesados {result['processed']}  ·  aprendidos "
          f"{s['documentaries_learned']}  ·  pendientes {s['pending']}  ·  fallidos {s['failed']}")
    return result


def main() -> None:
    p = argparse.ArgumentParser(description="Procesa la cola con monitor en vivo.")
    p.add_argument("--limit", type=int, default=None, help="máximo de documentales a procesar")
    args = p.parse_args()
    run(args.limit)


if __name__ == "__main__":
    main()
