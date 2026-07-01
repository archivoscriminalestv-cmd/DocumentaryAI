"""DCA Self Evaluation (DCA-003): mide la distancia generación↔corpus y propone el siguiente
motor a mejorar.

    python -m app.cli.self_evaluation --genre true_crime [--ece-coverage <coverage_report.json>]

Smoke del ciclo completo: KBG (corpus) → ProductionContext → VIS (storyboard base) →
DCA.evaluate → output/dca/{evaluation,generation_vs_corpus,improvement_plan,system_health}.json
+ evaluation_report.md. Solo lectura, determinista, sin IA. No escribe en knowledge/.
"""

import argparse
import json
import os
import sys

from app.dca.evaluation.persistence import write_evaluation_outputs
from app.dca.orchestrator import DocumentaryChiefArchitect
from app.pcx.builder import ProductionContextBuilder


def _baseline_plan(scene_duration: float):
    """Storyboard 'base' (generación actual sin contexto) para medir el hueco con el corpus."""
    from app.rda.models import CinematicProfile
    from app.domain.narrative.scene import Scene
    from app.vis import build_visual_plan
    profile = CinematicProfile(
        reference="baseline", source_type="local", width=1920, height=1080, aspect_ratio="16:9",
        fps=24.0, duration=60.0, sample_fps=4.0, shot_count=20, avg_shot_length=4.6,
        median_shot_length=4.6, min_shot_length=1.0, max_shot_length=9.0, shot_length_stddev=1.0,
        cuts_per_minute=13.0, pacing_tier="slow", shot_length_variety="moderate",
        brightness_mean=120.0, contrast_mean=40.0, lighting_tendency="balanced flat",
        warmth_mean=0.0, colorfulness_mean=25.0, color_temperature="neutral",
        saturation_tendency="moderate", motion_mean=0.5, movement_tendency="dynamic")
    scene = Scene(id="scene-01", title="t", narration="N", fact_ids=["f1"])
    return build_visual_plan(profile, scene, scene_duration=scene_duration)   # context=None (base)


def run(genre: str = "true_crime", styles_root: str = os.path.join("knowledge", "styles"),
        ece_coverage: str = "", out_dir: str | None = None) -> dict:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    out_dir = out_dir or os.path.join("output", "dca")
    ctx = ProductionContextBuilder().build(styles_root=styles_root, genre=genre)
    gk = None
    try:
        from app.kbg.bridge import KnowledgeBridge
        gk = KnowledgeBridge(styles_root=styles_root).build(genre=genre)
    except Exception:
        gk = None
    coverage = None
    if ece_coverage and os.path.isfile(ece_coverage):
        try:
            coverage = json.load(open(ece_coverage, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            coverage = None

    plan = _baseline_plan(scene_duration=18.0)
    result = DocumentaryChiefArchitect().evaluate(
        production_context=ctx, visual_plans=[plan], ece_coverage=coverage,
        generation_knowledge=gk)
    paths = write_evaluation_outputs(out_dir, result)

    s = result.summary
    print(f"Self Evaluation (género: {genre}) — {s['aligned']} alineadas / {s['differs']} "
          f"difieren / {s['unknown']} desconocidas · huecos: {s['gaps']}")
    print(f"Corpus alignment: {result.health.corpus_alignment} · knowledge_utilization: "
          f"{result.health.knowledge_utilization}")
    for g in result.gaps:
        print(f"  [{g.owner}] {g.description}")
    print(f"Siguiente motor a mejorar: {s['next_improvement']}")
    for name, path in paths.items():
        print(f"  {name:26} -> {path}")
    return {"result": result, "paths": paths}


def main() -> None:
    p = argparse.ArgumentParser(description="DCA Self Evaluation (DCA-003).")
    p.add_argument("--genre", default="true_crime")
    p.add_argument("--styles-root", default=os.path.join("knowledge", "styles"))
    p.add_argument("--ece-coverage", default="")
    p.add_argument("--out", default=None)
    args = p.parse_args()
    run(args.genre, args.styles_root, args.ece_coverage, args.out)


if __name__ == "__main__":
    main()
