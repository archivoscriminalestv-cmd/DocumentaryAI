"""Tests del Production Context (PCX-001) + integración VIS por composición.

Deterministas, solo lectura, sin red. No se ejecuta la suite completa.
"""

import json
import os

from app.pcx.builder import ProductionContextBuilder
from app.pcx.loader import decisions_from_generation_knowledge
from app.pcx.models import ProductionContext

# GenerationKnowledge en forma de dict (como el JSON del KBG); incluye UNKNOWN a filtrar.
_GK = {
    "genre": "true_crime",
    "sections": {
        "storytelling": [
            {"key": "pacing", "value": "moderate", "confidence": 0.49, "origin": "DKS:editing"},
            {"key": "average_shot_duration", "value": 2.0, "confidence": 0.5, "origin": "DKS:editing"},
            {"key": "structure", "value": "UNKNOWN", "confidence": 0.0, "origin": "UNKNOWN"},
        ],
        "cinematography": [
            {"key": "color_temperature", "value": "cool", "confidence": 0.45, "origin": "DKS:lighting"},
            {"key": "lighting", "value": "low-key", "confidence": 0.57, "origin": "DKS:lighting"},
            {"key": "dominant_movement", "value": "static", "confidence": 0.7, "origin": "DKS:motion"},
            {"key": "dominant_shot_size", "value": "UNKNOWN", "confidence": 0.0, "origin": "UNKNOWN"},
        ],
    },
}


# --- modelos / loader / builder ----------------------------------------------
def test_loader_filters_unknown():
    decs = decisions_from_generation_knowledge(_GK)
    assert decs["storytelling"]["pacing"].value == "moderate"
    assert "structure" not in decs["storytelling"]            # UNKNOWN fuera
    assert "dominant_shot_size" not in decs["cinematography"]


def test_builder_from_injected_gk():
    ctx = ProductionContextBuilder().build(generation_knowledge=_GK, genre="true_crime")
    assert ctx.genre == "true_crime"
    assert ctx.get("storytelling", "pacing") == "moderate"
    assert ctx.get("cinematography", "color_temperature") == "cool"
    assert ctx.get("cinematography", "dominant_shot_size") is None   # UNKNOWN -> None
    assert ctx.has("cinematography", "lighting")
    assert not ctx.has("storytelling", "structure")


def test_get_respects_min_confidence():
    ctx = ProductionContextBuilder().build(generation_knowledge=_GK)
    assert ctx.get("storytelling", "pacing", min_confidence=0.9, default="X") == "X"
    assert ctx.get("cinematography", "dominant_movement", min_confidence=0.5) == "static"


def test_builder_tolerates_missing_artifacts():
    ctx = ProductionContextBuilder().build()                  # sin nada
    assert isinstance(ctx, ProductionContext) and ctx.is_empty
    assert ctx.get("storytelling", "pacing") is None


def test_builder_from_json_path(tmp_path):
    p = tmp_path / "GenerationKnowledge.json"
    p.write_text(json.dumps(_GK), encoding="utf-8")
    ctx = ProductionContextBuilder().build(gk_json_path=str(p), genre="true_crime")
    assert ctx.get("cinematography", "lighting") == "low-key"


def test_builder_is_deterministic():
    a = ProductionContextBuilder().build(generation_knowledge=_GK)
    b = ProductionContextBuilder().build(generation_knowledge=_GK)
    assert a.to_dict() == b.to_dict()


def test_reserved_fields_present_for_future():
    ctx = ProductionContext()
    for fieldname in ("evidence_coverage", "recreation_policy", "target_platform",
                      "duration", "audience", "language", "case_metadata"):
        assert hasattr(ctx, fieldname)


# --- integración VIS por composición -----------------------------------------
def _profile():
    from app.rda.models import CinematicProfile
    return CinematicProfile(
        reference="ref", source_type="local", width=1920, height=1080, aspect_ratio="16:9",
        fps=24.0, duration=60.0, sample_fps=4.0, shot_count=20, avg_shot_length=6.0,
        median_shot_length=6.0, min_shot_length=1.0, max_shot_length=12.0,
        shot_length_stddev=1.0, cuts_per_minute=10.0, pacing_tier="slow",
        shot_length_variety="metronomic", brightness_mean=120.0, contrast_mean=40.0,
        lighting_tendency="high-key flat", warmth_mean=0.0, colorfulness_mean=25.0,
        color_temperature="warm", saturation_tendency="vivid", motion_mean=0.5,
        movement_tendency="dynamic")


def _scene():
    from app.domain.narrative.scene import Scene
    return Scene(id="scene-01", title="t", narration="N", fact_ids=["f1"])


def test_vis_unchanged_without_context():
    from app.vis import build_visual_plan
    profile, scene = _profile(), _scene()
    base = build_visual_plan(profile, scene, scene_duration=12.0)
    none_ctx = build_visual_plan(profile, scene, scene_duration=12.0, context=None)
    empty = build_visual_plan(profile, scene, scene_duration=12.0,
                              context=ProductionContextBuilder().build())
    assert base == none_ctx == empty            # comportamiento idéntico


def test_vis_uses_known_context_decisions():
    from app.vis import build_visual_plan
    profile, scene = _profile(), _scene()
    ctx = ProductionContextBuilder().build(generation_knowledge=_GK, genre="true_crime")
    base = build_visual_plan(profile, scene, scene_duration=12.0)
    ctxed = build_visual_plan(profile, scene, scene_duration=12.0, context=ctx)

    # average_shot_duration 2.0 (ctx) << 6.0 (perfil) -> más planos
    assert len(ctxed.shots) > len(base.shots)
    # dominant_movement 'static' -> mostly_static (mapeado); base era 'dynamic'
    assert ctxed.movement_tendency == "mostly_static" and base.movement_tendency == "dynamic"
    # lighting 'low-key' (ctx) cambia la iluminación de los planos
    assert "low-key" in ctxed.shots[0].lighting and ctxed.shots[0].lighting != base.shots[0].lighting
    # color_temperature 'cool' (ctx) cambia el grade; base era 'warm'
    assert "cool" in ctxed.grade and "warm" in base.grade
    assert ctxed.pacing_tier == "moderate"      # pacing del contexto


def test_vis_ignores_unknown_context_decisions():
    from app.vis import build_visual_plan
    profile, scene = _profile(), _scene()
    # contexto SIN average_shot_duration (solo lighting) -> asl sigue siendo el del perfil
    gk = {"genre": "true_crime", "sections": {"cinematography": [
        {"key": "lighting", "value": "low-key", "confidence": 0.6, "origin": "DKS:lighting"}]}}
    ctx = ProductionContextBuilder().build(generation_knowledge=gk)
    base = build_visual_plan(profile, scene, scene_duration=12.0)
    ctxed = build_visual_plan(profile, scene, scene_duration=12.0, context=ctx)
    assert len(ctxed.shots) == len(base.shots)              # asl no cambió (UNKNOWN ignorado)
    assert "low-key" in ctxed.shots[0].lighting             # lo conocido sí se aplicó


# --- desacoplamiento: VIS no conoce KBG/knowledge ----------------------------
def test_vis_does_not_depend_on_knowledge_sources():
    import app.vis.planner as planner
    # Solo las líneas de import cuentan (el docstring puede mencionar esos nombres en prosa).
    import_lines = [ln.strip().lower() for ln in open(planner.__file__, encoding="utf-8")
                    if ln.strip().startswith(("import ", "from "))]
    for forbidden in ("app.kbg", "app.knowledge", "knowledge.", "app.dks", "app.dle",
                      "app.ece", "app.eae", "app.dks", "app.yie", "app.vue"):
        assert not any(forbidden in ln for ln in import_lines), forbidden
