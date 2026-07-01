"""Tests del Cinematic Motion Engine (CME) — deterministas, sin red, sin aleatoriedad."""

import pytest

from app.cme import CinematicMotionEngine, CMEContext
from app.cme.continuity import assert_identity_safe
from app.cme.director import NarrativeMotionDirector
from app.cme.motion_catalog import CATALOG, compatible
from app.cme.physics import MAX_ZOOM_PCT, MotionParameters, compute_parameters


def _ctx(shot_id="s1", scene="scene-01", style="observational documentary", role="", hint="",
         dur=3.0):
    return CMEContext(shot_id=shot_id, scene_id=scene, asset_id="asset_x",
                      documentary_style=style, shot_role=role, motion_hint=hint,
                      shot_duration=dur, identity="vid_x", character_name="Coquito")


def _plan(style="observational documentary", role="", n=8):
    eng = CinematicMotionEngine()
    for i in range(n):
        eng.plan_shot(_ctx(shot_id=f"s{i}", style=style, role=role))
    eng.finalize()
    return eng


# --- determinismo / sin aleatoriedad -----------------------------------------

def test_engine_is_deterministic():
    a = [s.motion_type for s in _plan().shots]
    b = [s.motion_type for s in _plan().shots]
    assert a == b


def test_no_random_import_in_package():
    import importlib
    import pkgutil

    import app.cme as pkg
    for mod in pkgutil.iter_modules(pkg.__path__):
        source = importlib.import_module(f"app.cme.{mod.name}")
        assert "random" not in getattr(source, "__dict__", {})


# --- narrativa preservada (cada movimiento tiene razón) ----------------------

def test_narrative_intent_drives_motion():
    d = NarrativeMotionDirector()
    assert d.base_motion("interview", "", "")[0] == "SLOW_PUSH_IN"
    assert d.base_motion("any", "establishing", "")[0] == "REVEAL"
    assert d.base_motion("any", "detail", "")[0] == "MACRO_SLIDE"
    assert d.base_motion("any", "transition", "")[0] == "STATIC"
    assert d.base_motion("reconstruction", "", "")[0] == "HANDHELD_SUBTLE"


def test_every_shot_has_purpose():
    eng = _plan()
    assert all(s.purpose for s in eng.shots)
    assert all(s.justification for s in eng.shots)


# --- continuidad de escena ---------------------------------------------------

def test_steady_scene_has_no_handheld():
    eng = _plan(style="intimate documentary")
    assert all(s.family in ("static", "steady") for s in eng.shots)


def test_handheld_scene_stays_in_family():
    eng = _plan(style="reconstruction documentary")
    assert all(s.family in ("static", "handheld") for s in eng.shots)
    assert any(s.family == "handheld" for s in eng.shots)   # sí usa handheld


def test_scene_class_never_mixes_incompatible():
    eng = _plan(style="reconstruction")
    for s in eng.shots:
        assert compatible("handheld", s.motion_type)


# --- diversidad --------------------------------------------------------------

def test_avoids_repeating_same_motion():
    eng = _plan(style="observational documentary", n=10)
    types = [s.motion_type for s in eng.shots]
    assert len(set(types)) >= 5                              # no 10 push-in
    assert eng.average_diversity() > 0.5


def test_diversity_score_bounds():
    eng = _plan(n=6)
    assert 0.0 <= eng.average_diversity() <= 1.0


# --- identidad nunca se deforma ----------------------------------------------

def test_motion_params_within_identity_limits():
    eng = _plan(n=12)
    for s in eng.shots:
        assert_identity_safe(s.parameters)                  # no lanza


def test_assert_identity_safe_rejects_extreme():
    with pytest.raises(ValueError):
        assert_identity_safe(MotionParameters(zoom_pct=999.0))


def test_physics_clamps_long_durations():
    p = compute_parameters("zoom", "in", duration=1000.0, easing="ease_in_out", stability=0.9)
    assert abs(p.zoom_pct) <= MAX_ZOOM_PCT


# --- provider independence ---------------------------------------------------

def test_manifest_is_provider_agnostic():
    eng = _plan()
    blob = str(eng.manifest()).lower()
    for token in ("ffmpeg", "runway", "veo", "pika", "kling", "openai", "huggingface"):
        assert token not in blob


# --- timeline ----------------------------------------------------------------

def test_timeline_accumulates():
    eng = _plan(n=4)
    shots = eng.shots
    assert shots[0].start == 0.0
    for prev, nxt in zip(shots, shots[1:]):
        assert nxt.start == prev.end
    assert eng.timeline.total_duration == round(sum(s.duration for s in shots), 3)
    assert shots[-1].transition_out == 1.0                  # finalize: salida del último


# --- catálogo / física -------------------------------------------------------

def test_catalog_has_grammar():
    for name in ("STATIC", "SLOW_PUSH_IN", "PARALLAX", "DRONE_REVEAL", "HANDHELD_NERVOUS"):
        assert name in CATALOG
    assert CATALOG["SLOW_PUSH_IN"].primary == "zoom"
    assert CATALOG["STATIC"].primary == "none"


def test_static_has_no_movement():
    p = compute_parameters("none", "none", 3.0, "linear", 1.0)
    assert p.zoom_pct == 0.0 and p.pan_deg == 0.0 and p.translate_x == 0.0


# --- pipeline intacto + no muta entradas -------------------------------------

def test_pipeline_build_requests_unaffected_count():
    from app.cli.compile_coquito import build_requests, build_shot_contexts
    reqs = build_requests()
    ctxs = build_shot_contexts()
    assert len(reqs) == 26 and len(ctxs) == 26


def test_cme_does_not_mutate_context():
    ctx = _ctx()
    before = (ctx.shot_id, ctx.motion_hint, ctx.documentary_style)
    CinematicMotionEngine().plan_shot(ctx)
    assert (ctx.shot_id, ctx.motion_hint, ctx.documentary_style) == before
