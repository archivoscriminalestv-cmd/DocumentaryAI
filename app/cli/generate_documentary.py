"""Render del documental con proveedores REALES + Provider Router automático.

    python -m app.cli.generate_documentary

Pasos:
  1. Carga ``.env`` (sin sobreescribir variables ya presentes; nunca hardcodea claves).
  2. Preflight completo: valida con una llamada real qué proveedores funcionan y
     muestra el motivo EXACTO de cualquier error (no se ocultan errores).
  3. Provider Router AUTOMÁTICO por prioridad (Imagen > OpenAI > HF > Replicate): si
     uno falla o devuelve una imagen inválida, usa el siguiente. Sin selección manual.
     Sin mock (objetivo: imágenes reales).
  4. Genera los 26 planos del documental "Coquito".
  5. Escribe output/documentary/{images/S01.png..S26.png, manifest.json, telemetry.json,
     render_report.md}.

No modifica VIS/VAI/VSC/Composer/Motion: todo es aditivo en la frontera del VPL.
"""

import json
import logging
import os
import sys

from app.alr import AssetLibrary
from app.cce import IdentityLockEngine, IdentityPromptBuilder, apply_identity_to_all
from app.cli.build_character_profile import load_character_bible
from app.cli.compile_coquito import build_shot_contexts
from app.cli.coquito import coquito_documentary
from app.cme import CinematicMotionEngine, CMEContext
from app.cme.persistence import write_outputs as write_cme_outputs
from app.sde import ShotDiversityEngine
from app.sde.persistence import write_outputs as write_sde_outputs
from app.cli.compile_coquito import build_requests
from app.infrastructure.config.runtime_secrets import SecretsManager
from app.vpl import VisualGenerationOrchestrator, VPLConfig
from app.vpl.preflight import format_full, run_preflight, valid_providers
from app.vpl.router import PRIORITY, build_router
from app.vpl.telemetry import build_render_report, build_report, build_telemetry

# Personaje del documental de prueba (la identidad la fija el CCE, no el VSC).
_DOCUMENTARY_CHARACTER = "Coquito"


def _ordered_available(valid: list[str]) -> list[str]:
    ordered = [n for n in PRIORITY if n in valid]
    ordered += [n for n in valid if n not in ordered]
    return ordered


def run() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # 1) .env -> entorno (no sobreescribe lo ya definido).
    secrets = SecretsManager()
    secrets.load_env()

    # 2) Preflight con validación real.
    results = run_preflight()
    valid = valid_providers(results)
    available = _ordered_available(valid)
    print(format_full(results, available))

    if not available:
        print("\n[VPL] ERROR: ningún proveedor real disponible. Revisa los motivos de "
              "arriba (auth/facturación/permisos/modelo) y corrige .env. No se genera "
              "nada mock: el objetivo es comprobar el estado REAL.")
        return

    # 3) Provider Router automático por prioridad.
    router = build_router(available)
    print(f"\n[VPL] Provider Router -> {' > '.join(p.name for p in router.providers)}")

    # 4) Render. El orquestador usa el router como 'proveedor' (provider-agnóstico).
    # 4.a) CCE: identidad visual permanente del personaje (se necesita antes para el SDE).
    profile = IdentityLockEngine().lock(load_character_bible(_DOCUMENTARY_CHARACTER))

    # 4.b) SDE: Director de Fotografía determinista. Diversifica la composición de cada
    # plano (VIS -> VAI -> SDE -> VSC). No toca identidad, escena, VPL ni ALR.
    sde = ShotDiversityEngine()
    requests = build_requests(sde=sde, character_name=profile.canonical_name,
                              identity=profile.visual_identity_id)
    print(f"[SDE] diversidad media {sde.average_diversity():.2f} en {len(requests)} planos "
          f"({sde.stats()['variations_applied']} variaciones aplicadas)")

    # 4.c) CCE: se antepone un bloque fijo de identidad a CADA petición (solo el prompt).
    requests = apply_identity_to_all(requests, profile)
    print(f"[CCE] identidad fija {profile.visual_identity_id} "
          f"(completeness {profile.completeness:.0%}) aplicada a {len(requests)} planos")
    print(f"[CCE] bloque: {IdentityPromptBuilder().build_identity_block(profile)}")

    output_dir = os.path.join("output", "documentary")
    print(f"[VSC] Coquito -> {len(requests)} planos\n")
    config = VPLConfig.from_env()
    manifest = VisualGenerationOrchestrator(config=config, provider=router).generate(
        requests, documentary_id="coquito", output_dir=output_dir
    )

    # 5) Artefactos del render (temporal): manifest.json + telemetry.json + render_report.md.
    with open(os.path.join(output_dir, "telemetry.json"), "w", encoding="utf-8") as handle:
        json.dump(build_telemetry(manifest), handle, ensure_ascii=False, indent=2)
    with open(os.path.join(output_dir, "render_report.md"), "w", encoding="utf-8") as handle:
        handle.write(build_render_report(manifest))

    # SDE: historial + informe de diversidad cinematográfica.
    write_sde_outputs(output_dir, sde)

    # 6) ALR: ingestar en la BIBLIOTECA PERMANENTE (nunca borra ni sobreescribe).
    # output/documentary/images es solo temporal; la verdad vive en library/.
    library = AssetLibrary()
    result = library.ingest_render(
        manifest, project="coquito", character_identity=profile.visual_identity_id,
        character_name=profile.canonical_name, images_dir=os.path.join(output_dir, "images"),
    )
    doc_manifest_path = result["manifest"].write(os.path.join(output_dir, "documentary_manifest.json"))
    report_path = library.write_report()
    s = result["summary"]

    # 7) CME: Director de Cámara. Plan de movimiento por plano (VSC -> CME -> Composer).
    # No renderiza ni anima: solo construye un MotionPlan provider-agnóstico.
    asset_ids = result["manifest"].to_dict()["asset_ids"]
    contexts = build_shot_contexts()
    cme = CinematicMotionEngine()
    for i, (req, meta) in enumerate(zip(requests, contexts)):
        cme.plan_shot(CMEContext(
            shot_id=req.shot_id, scene_id=req.scene_id,
            asset_id=asset_ids[i] if i < len(asset_ids) else "",
            documentary_style=meta["documentary_style"], shot_role=meta["shot_role"],
            motion_hint=getattr(req, "motion_hint", ""), shot_duration=meta["shot_duration"],
            identity=profile.visual_identity_id, character_name=profile.canonical_name,
        ))
    cme.finalize()
    cme_paths = write_cme_outputs(output_dir, cme, project="coquito")
    cme_stats = cme.stats()

    print("=== TELEMETRY ===")
    print(build_report(manifest))
    print(f"\n=== ASSET LIBRARY (ALR) ===")
    print(f"Ingesta: {s['new']} nuevos, {s['referenced']} referencias a existentes, "
          f"{s['new_possible_duplicate']} nuevos~similares")
    print(f"Biblioteca permanente: {result['library_size']} assets en library/ (nunca se borran)")
    print(f"\nRender temp:   {output_dir}/images/ (sobrescribible)")
    print(f"Biblioteca:    library/images/asset_*.{{png}}  ({library.storage.registry_path})")
    print(f"Doc manifest:  {doc_manifest_path}  (referencia asset_id, no imágenes)")
    print(f"Library report:{report_path}")

    print(f"\n=== CINEMATIC MOTION (CME) ===")
    print(f"{cme_stats['total_shots']} MotionShots  ·  diversidad {cme_stats['average_diversity']:.2f}  ·  "
          f"energía {cme_stats['cinematic_energy']:.2f}  ·  timeline {cme_stats['total_duration']:.1f}s")
    print(f"Movimientos: {cme_stats['by_motion_type']}")
    print(f"Motion manifest: {cme_paths['manifest']}  |  report: {cme_paths['report']}")

    # 8) COMPOSER: ejecuta el plan -> documentary.mp4 (clips + movimiento + audio + transiciones).
    from app.composer import DocumentaryComposer
    from app.infrastructure.voice.narrator import build_speech_synthesizer

    asset_paths = [r.library_path for refs in result["manifest"].scenes.values() for r in refs]
    narration_by_scene = {scene.id: scene.narration for scene, _svc, _d in coquito_documentary()}
    print(f"\n[COMPOSER] ejecutando {len(cme.shots)} planos -> clips + movimiento + audio…")
    composer = DocumentaryComposer(synthesizer=build_speech_synthesizer(secrets))
    comp = composer.run(
        motion_shots=cme.shots, asset_paths=asset_paths,
        narration_by_scene=narration_by_scene, output_dir=output_dir, project="coquito",
        music_path=os.environ.get("MUSIC_TRACK"), cache_hits=manifest.cache_hits,
    )

    print(f"\n=== DOCUMENTARY (COMPOSER) ===")
    print(f"MP4: {comp.output_path}  ·  {comp.total_duration:.1f}s  ·  {comp.width}x{comp.height}@{comp.fps}  "
          f"·  {comp.bitrate or 'n/a'}")
    print(f"Clips: {len(comp.clips)} en {output_dir}/clips/  ·  render {comp.render_seconds:.1f}s")
    print(f"Audio sync: video {comp.video_duration:.1f}s == audio {comp.audio_duration:.1f}s -> "
          f"{'OK' if comp.in_sync else 'DESINCRONIZADO'}")
    print(f"Narración: {comp.narration_provider}  ·  Música: {comp.music_provider}")
    print(f"Transiciones: {comp.transitions_used}")
    print(f"Manifest: {output_dir}/composer_manifest.json  |  report: {output_dir}/composer_report.md")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
