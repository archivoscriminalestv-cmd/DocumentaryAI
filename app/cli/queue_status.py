"""Muestra el progreso de la cola de aprendizaje (DLE-002).

    python -m app.cli.queue_status
"""

import sys

from app.dle.queue import LearningQueueManager
from app.dle.queue.models import QueueStatus


def run() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    mgr = LearningQueueManager()
    s = mgr.status()
    print("=== LEARNING QUEUE ===")
    print(f"Total: {s['total_in_queue']}  ·  paused: {mgr.store.is_paused()}")
    print(f"Learned {s['documentaries_learned']}  ·  Skipped {s['skipped']}  ·  "
          f"Failed {s['failed']}  ·  Pending {s['pending']}  ·  Remaining {s['remaining']}")
    print(f"Hours {s['hours_learned']:.2f}  ·  Shots {s['shots_analyzed']}  ·  Scenes {s['scenes']}")
    print("\nItems:")
    for i in mgr.store.ordered()[:200]:
        mark = "x" if i.status == QueueStatus.FAILED else ("·" if i.status == QueueStatus.PENDING else "✓")
        print(f"  [{mark}] {i.status:<11} {i.documentary_id or '—':<22} {i.url}")
        if i.status == QueueStatus.FAILED and i.error:
            print(f"        error: {i.error[:120]}")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
