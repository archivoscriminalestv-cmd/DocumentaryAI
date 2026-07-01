"""Centro de control del aprendizaje en TIEMPO REAL (DLM-001).

    python -m app.cli.learn_dashboard
    python -m app.cli.learn_dashboard --limit 50 --scene-threshold 0.27

Un único comando: Dashboard → Learning Queue → YIE → DLE → Knowledge → resumen final.
El dashboard se actualiza en vivo consumiendo SOLO eventos públicos; no modifica nada.
"""

import argparse
import sys
import time

from app.cli.compile_coquito import build_shot_contexts  # noqa: F401  (mantiene cohesión de imports CLI)
from app.dle.orchestrator import DocumentaryLearningEngine
from app.dle.queue import LearningQueueManager
from app.dlm.monitor import DashboardMonitor
from app.dlm.persistence import write_outputs
from app.dlm.renderer import TerminalDashboardRenderer, render_dashboard
from app.infrastructure.config.runtime_secrets import SecretsManager

_KNOWLEDGE = "knowledge"


def _build_intelligence():
    try:
        from app.yie.intelligence.orchestrator import CompetitiveIntelligenceEngine
        return CompetitiveIntelligenceEngine()
    except Exception:
        return None


def run(limit: int | None, scene_threshold: float) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    SecretsManager().load_env()

    engine = DocumentaryLearningEngine(scene_threshold=scene_threshold)
    mgr = LearningQueueManager(engine=engine, intelligence=_build_intelligence(),
                               knowledge_root=_KNOWLEDGE)

    # 1) Cargar la cola. Si no hay pendientes, no hay nada que procesar.
    status0 = mgr.status()
    if status0.get("pending", 0) <= 0:
        _no_pending_summary(status0)
        return
    if mgr.store.is_paused():
        print("[queue] la cola está EN PAUSA; reanúdala para procesar.")
        return

    # 2) Procesar toda la cola mostrando el dashboard en vivo (reutiliza el manager,
    #    mismo flujo que learn_queue; no se duplica lógica).
    monitor = DashboardMonitor(knowledge_root=_KNOWLEDGE)
    renderer = TerminalDashboardRenderer()

    def on_event(event) -> None:
        renderer.render(monitor.handle(event))

    started_at = time.time()
    result = mgr.process_all(limit=limit, on_event=on_event)
    finished_at = time.time()

    state = monitor.snapshot()
    paths = write_outputs(_KNOWLEDGE, state, started_at=started_at, finished_at=finished_at)
    renderer.render(state)

    # 3) Al terminar la cola, sintetizar el conocimiento (DKS) automáticamente.
    dks = _run_dks()

    # 4) Resumen final.
    _final_summary(state, result, paths, dks)


def _no_pending_summary(status: dict) -> None:
    rule = "=" * 51
    print(rule)
    print("No hay documentales pendientes.")
    print("Corpus actualizado:")
    print(f"  Documentales ... {status.get('documentaries_learned', 0)}")
    print(f"  Horas .......... {status.get('hours_learned', 0.0):.2f}")
    print(f"  Planos ......... {status.get('shots_analyzed', 0)}  ·  "
          f"Escenas: {status.get('scenes', 0)}")
    print(rule)
    print("Finalizado.")


def _run_dks() -> dict | None:
    """Ejecuta el DKS (synthesize_knowledge) reutilizando su CLI. Best-effort."""
    try:
        from app.cli import synthesize_knowledge
        print("\n[DKS] sintetizando la base de estilos…")
        return synthesize_knowledge.run(knowledge_root=_KNOWLEDGE)
    except Exception as exc:  # noqa: BLE001 — el DKS no debe romper el resumen
        print(f"[DKS] aviso: no se pudo sintetizar ({exc})")
        return None


def _final_summary(state, result, paths, dks=None) -> None:
    g, c = state.globals, state.corpus
    rule = "=" * 51
    print("\n" + rule)
    print("Learning Finished")
    print(rule)
    print(f"Documentales aprendidos .. {g.completed}")
    print(f"Horas de vídeo ........... {c.hours:.2f}")
    print(f"Planos ................... {c.shots}")
    print(f"Escenas .................. {c.scenes}")
    print(f"Tiempo total ............. {g.elapsed:.1f}s")
    print(f"Velocidad media .......... {g.videos_per_hour:.2f} vídeos/hora")
    print(f"Errores .................. {g.failed}")
    print(f"Knowledge Size ........... {c.knowledge_bytes / (1024 * 1024):.2f} MB")
    print(rule)
    print("Archivos generados:")
    print(f"  knowledge/  (documentaries/, learning_report.md, learning_statistics.json)")
    if dks and dks.get("paths"):
        print(f"  knowledge/styles/  ({len(dks['paths'])} perfiles DKS)")
    print(f"  {paths['history']}")
    print(f"  {paths['session']}")
    print(rule)


def main() -> None:
    p = argparse.ArgumentParser(description="DocumentaryAI — Learning Dashboard (DLM).")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--scene-threshold", type=float, default=0.27)
    args = p.parse_args()
    run(args.limit, args.scene_threshold)


if __name__ == "__main__":
    main()
