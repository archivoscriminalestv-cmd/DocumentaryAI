"""Reintenta los documentales fallidos de la cola (DLE-002).

    python -m app.cli.queue_retry            # marca FAILED -> PENDING
    python -m app.cli.queue_retry --run      # marca y procesa inmediatamente
"""

import argparse
import sys

from app.dle.queue import LearningQueueManager


def run(do_run: bool) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    mgr = LearningQueueManager()
    n = mgr.retry()
    print(f"[queue] {n} elementos fallidos marcados para reintento")
    if do_run and n:
        result = mgr.process_all()
        s = result["status"]
        print(f"[queue] reprocesados {result['processed']}  ·  fallidos restantes: {s['failed']}")


def main() -> None:
    p = argparse.ArgumentParser(description="Reintenta los fallidos de la cola.")
    p.add_argument("--run", action="store_true", help="procesar tras marcar")
    args = p.parse_args()
    run(args.run)


if __name__ == "__main__":
    main()
