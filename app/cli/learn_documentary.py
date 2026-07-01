"""Aprende conocimiento cinematográfico de un documental real (DLE).

    python -m app.cli.learn_documentary --youtube https://youtube.com/watch?v=...
    python -m app.cli.learn_documentary --video documentary.mp4

Descarga/accede al vídeo, lo analiza por completo, construye la base de conocimiento y
las estadísticas, genera un informe Markdown y lo almacena permanentemente en
``knowledge/``. Re-ejecutar el mismo documental NO duplica (usa ``--force`` para forzar).
NO modifica el pipeline de generación.
"""

import argparse
import sys

from app.dle import DocumentaryLearningEngine
from app.infrastructure.config.runtime_secrets import SecretsManager


def run(youtube: str | None, video: str | None, force: bool,
        scene_threshold: float = 0.27) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    SecretsManager().load_env()

    engine = DocumentaryLearningEngine(scene_threshold=scene_threshold)
    print(f"[DLE] storage mode: {engine.storage_policy.mode} "
          f"(LEARNING_STORAGE_MODE; TEMPORARY borra el vídeo tras aprender)")
    result = engine.learn(youtube=youtube, video=video, force=force)

    status = result.get("status")
    if status == "error":
        print("[DLE] ERROR: no se pudo procesar la fuente:")
        for e in result.get("errors", []):
            print(f"   - {e['stage']}: {e['message']}")
        return
    if status == "skipped":
        print(f"[DLE] '{result['documentary_id']}' ya está aprendido (no se duplica). "
              f"Usa --force para re-analizar.\n      {result['doc_dir']}")
        return

    k = result["knowledge"]
    s = k.statistics
    print(f"[DLE] Aprendido: {k.documentary_id}")
    print(f"  Fuente:   {k.metadata.source_type}  ·  {k.metadata.duration:.1f}s  ·  "
          f"{k.metadata.width}x{k.metadata.height}@{k.metadata.fps}")
    print(f"  Planos:   {s.shot_count}  ·  Escenas: {s.scene_count}  ·  Cortes: {s.cut_count}")
    print(f"  Ritmo:    plano medio {s.average_shot_length:.2f}s ({s.pacing_tier}), "
          f"{s.cuts_per_minute:.1f} cortes/min")
    print(f"  Color:    {s.color_temperature_distribution}")
    print(f"  Luz:      {s.lighting_distribution}")
    print(f"  Transcripción: {k.transcript.provider} "
          f"({'disponible' if k.transcript.available else 'no disponible'})")
    if k.errors:
        print(f"  Errores (no bloqueantes): {len(k.errors)}")
    print(f"\n  Conocimiento: {result['doc_dir']}/  (documentary.json, scenes.json, "
          f"shots.json, statistics.json, transcript.json, report.md)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Documentary Learning Engine (DLE).")
    parser.add_argument("--youtube", help="URL de YouTube del documental")
    parser.add_argument("--video", help="Ruta a un vídeo local del documental")
    parser.add_argument("--force", action="store_true", help="Re-analizar aunque ya exista")
    parser.add_argument("--scene-threshold", type=float, default=0.27,
                        help="Sensibilidad de detección de cortes (0.27 footage real; baja para fundidos)")
    args = parser.parse_args()
    run(args.youtube, args.video, args.force, args.scene_threshold)


if __name__ == "__main__":
    main()
