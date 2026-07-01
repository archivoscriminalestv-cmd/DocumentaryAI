"""Tests del Visual Scene Compiler (VSC). Determinista, sin red, provider-agnóstico."""

import json
from dataclasses import asdict

from app.vai import VisualDirector, VisualContext
from app.vis.models import PlannedShot
from app.vsc import (
    AssetCache,
    CachingVisualProvider,
    GlobalStyle,
    MockVisualProvider,
    SceneVisualContext,
    VisualSceneCompiler,
)
from app.vsc.models import GeneratedAsset


def _scene_ctx(**over) -> SceneVisualContext:
    base = dict(
        scene_id="scene-01", identity="coquito_home", location="a flat in Almassora, Spain",
        season="January", time_of_day="afternoon", weather="overcast", color_palette="muted cold tones",
        camera_package="Sony FX6", lens_family="35mm prime", lighting_language="soft overcast natural light",
        documentary_style="intimate documentary", realism_level="high",
        negative_prompts=("toy-like",), seed_strategy="per_scene", seed=1001, reuse_policy="shot",
    )
    base.update(over)
    return SceneVisualContext(**base)


def _shot(index=0, shot_type="impact", move="push_in", reuse_key="") -> PlannedShot:
    return PlannedShot(
        id=f"scene-01::shot-{index:02d}", scene_id="scene-01", index=index, shot_type=shot_type,
        camera_move=move, camera_intensity=0.7, lighting="", duration=3.0, asset_type="image",
        reuse_key=reuse_key, fact_ids=["f1"],
    )


def _request(shot, subject="Coquito the dog"):
    director = VisualDirector()
    ctx = VisualContext(subject=subject, style="documentary")
    return director.direct(shot, ctx)


# --- compilación + continuidad -----------------------------------------------

def test_compiles_request_with_all_fields():
    vgr = VisualSceneCompiler().compile(_request(_shot()), _scene_ctx())
    p = vgr.prompt.lower()
    assert "coquito the dog" in p
    assert "sony fx6" in p and "35mm prime" in p          # cámara/lente de escena
    assert "muted cold tones" in p and "overcast" in p     # paleta/clima de escena
    assert "cinematic documentary" in p                    # estilo global
    assert vgr.global_style and vgr.scene_style and vgr.shot_style  # capas explícitas
    assert vgr.camera == "Sony FX6" and vgr.lens == "35mm prime"


def test_continuity_within_scene():
    scene = _scene_ctx()
    a = VisualSceneCompiler().compile(_request(_shot(0, "establishing", "drone")), scene)
    b = VisualSceneCompiler().compile(_request(_shot(1, "detail", "ken_burns")), scene)
    # continuidad: cámara, lente, color, iluminación, entorno IDÉNTICOS
    assert (a.camera, a.lens, a.color, a.lighting, a.environment) == (b.camera, b.lens, b.color, b.lighting, b.environment)
    # variación: el shot_style difiere
    assert a.shot_style != b.shot_style


def test_negatives_merged():
    vgr = VisualSceneCompiler().compile(_request(_shot()), _scene_ctx())
    n = vgr.negative_prompt.lower()
    assert "cartoon" in n        # global
    assert "toy-like" in n       # escena
    assert "watermark" in n


def test_motion_hint_mapping():
    push = VisualSceneCompiler().compile(_request(_shot(move="push_in")), _scene_ctx())
    locked = VisualSceneCompiler().compile(_request(_shot(move="static")), _scene_ctx())
    assert push.motion_hint == "slow_push_in"
    assert locked.motion_hint == "locked"


def test_seed_strategy():
    per_scene = _scene_ctx(seed_strategy="per_scene", seed=42)
    a = VisualSceneCompiler().compile(_request(_shot(0)), per_scene)
    b = VisualSceneCompiler().compile(_request(_shot(1)), per_scene)
    assert a.seed == b.seed == 42                          # per_scene -> mismo seed
    per_shot = _scene_ctx(seed_strategy="per_shot", seed=42)
    c = VisualSceneCompiler().compile(_request(_shot(0)), per_shot)
    d = VisualSceneCompiler().compile(_request(_shot(1)), per_shot)
    assert c.seed != d.seed                                # per_shot -> distinto


def test_reuse_policy_off():
    vgr = VisualSceneCompiler().compile(_request(_shot(reuse_key="loc")), _scene_ctx(reuse_policy="off"))
    assert vgr.reuse_key == ""


def test_provider_independent_and_serializable():
    vgr = VisualSceneCompiler().compile(_request(_shot()), _scene_ctx())
    low = vgr.prompt.lower()
    for tok in ("--ar", "midjourney", "pollinations", "::", "stable diffusion"):
        assert tok not in low
    decoded = json.loads(json.dumps(asdict(vgr), ensure_ascii=False))
    assert decoded["shot_id"] and decoded["provider_constraints"]["aspect_ratio"] == "16:9"


def test_deterministic():
    a = VisualSceneCompiler().compile(_request(_shot()), _scene_ctx())
    b = VisualSceneCompiler().compile(_request(_shot()), _scene_ctx())
    assert asdict(a) == asdict(b)


# --- caché + proveedor -------------------------------------------------------

def test_asset_cache_basics():
    cache = AssetCache()
    asset = GeneratedAsset(shot_id="s1", reuse_key="loc-1", provider="mock", uri="u", prompt="p")
    assert cache.get("loc-1") is None
    cache.put(asset)
    assert cache.has("loc-1") and cache.get("loc-1").uri == "u"
    cache.put(GeneratedAsset(shot_id="x", reuse_key="", provider="mock", uri="u2", prompt="p"))
    assert cache.get("") is None     # clave vacía nunca cachea


def test_caching_provider_reuses_by_key():
    provider = MockVisualProvider()
    caching = CachingVisualProvider(provider)
    scene = _scene_ctx()
    compiler = VisualSceneCompiler()
    r1 = compiler.compile(_request(_shot(0, "establishing", reuse_key="corner_finestrelles")), scene)
    r2 = compiler.compile(_request(_shot(1, "wide", reuse_key="corner_finestrelles")), scene)
    r3 = compiler.compile(_request(_shot(2, "impact")), scene)  # reuse_key ""

    a1 = caching.generate(r1)
    a2 = caching.generate(r2)
    a3 = caching.generate(r3)

    assert a1.cached is False and a2.cached is True          # localización reutilizada
    assert a2.uri == a1.uri
    assert a3.cached is False
    assert provider.calls == 2                                # solo 2 generaciones reales


# --- ejemplo Coquito completo ------------------------------------------------

def test_coquito_example_compiles_all_shots():
    from app.cli.compile_coquito import build_requests
    requests = build_requests()
    assert len(requests) >= 10                               # varias escenas x varios planos
    assert all(r.prompt and r.negative_prompt for r in requests)
    # continuidad por escena: todos los planos de scene-01 comparten cámara/lente
    s1 = [r for r in requests if r.scene_id == "scene-01"]
    assert len({(r.camera, r.lens, r.color) for r in s1}) == 1
