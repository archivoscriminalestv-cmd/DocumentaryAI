"""Procesa TODA la cola de aprendizaje, automáticamente (DLE-002).

    python -m app.cli.learn_queue
    python -m app.cli.learn_queue --limit 10 --scene-threshold 0.27

Aprende un documental tras otro sin intervención. El progreso es persistente: si se
detiene, al re-ejecutar continúa donde estaba. No re-aprende lo ya aprendido.
"""

import argparse
import sys

from app.dle.orchestrator import DocumentaryLearningEngine
from app.dle.queue import LearningQueueManager
from app.infrastructure.config.runtime_secrets import SecretsManager
from app.yie.intelligence.orchestrator import CompetitiveIntelligenceEngine


def run(limit: int | None, scene_threshold: float) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    SecretsManager().load_env()

    engine = DocumentaryLearningEngine(scene_threshold=scene_threshold)
    # Integración Queue -> YIE -> DLE: para fuentes YouTube se analiza la inteligencia
    # competitiva completa (vídeo/canal/audiencia/engagement/SEO/miniatura + cobertura)
    # antes de aprender. Best-effort y no altera el DLE.
    intelligence = CompetitiveIntelligenceEngine()
    mgr = LearningQueueManager(engine=engine, intelligence=intelligence)
    if mgr.store.is_paused():
        print("[queue] la cola está EN PAUSA. Usa la API/maneja resume() para reanudar.")
    result = mgr.process_all(limit=limit)
    s = result["status"]
    print(f"[queue] procesados {result['processed']} (recuperados {result['recovered']})")
    print(f"  Aprendidos: {s['documentaries_learned']}  ·  Omitidos: {s['skipped']}  ·  "
          f"Fallidos: {s['failed']}  ·  Pendientes: {s['pending']}")
    print(f"  Horas aprendidas: {s['hours_learned']:.2f}h  ·  Planos: {s['shots_analyzed']}  ·  "
          f"Escenas: {s['scenes']}")
    print(f"  Informe: {result['reports']['report']}")


def main() -> None:
    p = argparse.ArgumentParser(description="Procesa la cola de aprendizaje (DLE).")
    p.add_argument("--limit", type=int, default=None, help="máximo de documentales a procesar")
    p.add_argument("--scene-threshold", type=float, default=0.27)
    args = p.parse_args()
    run(args.limit, args.scene_threshold)


if __name__ == "__main__":
    main()
