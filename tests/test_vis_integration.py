"""Validación de integración real RDA→VIS-1→VIS-2→MGL (slice). Sin red, sin LLM."""

import time

from app.media.generation.mgl import MediaGenerationLayer
from app.media.generation.provider_router import ProviderRouter
from app.media.providers.base import BaseProvider
from app.media.store.asset_store import AssetStore
from app.media.store.models import Asset
from app.rda.models import CinematicProfile
from app.vis import build_visual_plan, compile_execution
from app.domain.narrative.scene import Scene


def _profile(**over) -> CinematicProfile:
    base = dict(
        reference="ref", source_type="local", width=1920, height=1080,
        aspect_ratio="16:9", fps=24.0, duration=60.0, sample_fps=4.0,
        shot_count=20, avg_shot_length=3.0, median_shot_length=3.0,
        min_shot_length=1.0, max_shot_length=6.0, shot_length_stddev=1.0,
        cuts_per_minute=20.0, pacing_tier="moderate", shot_length_variety="moderate",
        brightness_mean=120.0, contrast_mean=40.0, lighting_tendency="balanced",
        warmth_mean=0.0, colorfulness_mean=25.0, color_temperature="neutral",
        saturation_tendency="moderate", motion_mean=0.04, movement_tendency="moderate",
    )
    base.update(over)
    return CinematicProfile(**base)


_FAST_DARK = _profile(
    reference="ref-A", avg_shot_length=2.0, pacing_tier="fast", movement_tendency="dynamic",
    lighting_tendency="low-key high-contrast", color_temperature="cool", saturation_tendency="muted",
    shot_length_variety="varied",
)
_SLOW_BRIGHT = _profile(
    reference="ref-B", avg_shot_length=6.0, pacing_tier="slow", movement_tendency="mostly_static",
    lighting_tendency="high-key flat", color_temperature="warm", saturation_tendency="vivid",
    shot_length_variety="metronomic",
)

_SCENE = Scene(id="scene-01", title="The collapse of an empire", narration="N", fact_ids=["f1"])


class _Echo(BaseProvider):
    name = "echo"

    def __init__(self):
        self.calls = 0

    def generate_image(self, prompt):
        self.calls += 1
        return Asset(asset_id=f"a{self.calls}", type="image", prompt=prompt, provider=self.name, timestamp=time.time())

    def generate_video(self, prompt):
        raise NotImplementedError


# --- 1) El RDA influye REALMENTE en VIS-1 ------------------------------------

def test_reference_changes_vis1_decisions():
    plan_a = build_visual_plan(_FAST_DARK, _SCENE, scene_duration=12.0)
    plan_b = build_visual_plan(_SLOW_BRIGHT, _SCENE, scene_duration=12.0)

    assert len(plan_a.shots) >= 5 and len(plan_b.shots) >= 5
    # distinto ritmo -> distinto nº de planos (fast genera más que slow)
    assert len(plan_a.shots) > len(plan_b.shots)
    # distinta tendencia de movimiento -> distinto repertorio de cámara
    moves_a = {s.camera_move for s in plan_a.shots}
    moves_b = {s.camera_move for s in plan_b.shots}
    assert moves_a != moves_b
    assert any(m in moves_a for m in ("tracking", "drone", "orbital"))   # dynamic
    # distinta iluminación y grade
    assert plan_a.shots[0].lighting != plan_b.shots[0].lighting
    assert plan_a.grade != plan_b.grade
    # distinta duración media de plano
    assert plan_a.total_duration != plan_b.total_duration


# --- 2/3) VIS-2 produce variación real y prompts únicos ----------------------

def test_vis2_enforces_variation_and_uniqueness():
    plan = build_visual_plan(_FAST_DARK, _SCENE, scene_duration=14.0)
    ep = compile_execution(plan, _SCENE)

    assert len(ep.requests) == len(plan.shots)
    # no se repite lente/ángulo/composición en planos consecutivos
    for a, b in zip(ep.requests, ep.requests[1:]):
        assert not (a.lens == b.lens and a.angle == b.angle and a.composition == b.composition)
        assert a.lens != b.lens
        assert a.angle != b.angle
        assert a.composition != b.composition
    # prompts y fingerprints únicos
    prompts = [r.prompt for r in ep.requests]
    assert len(set(prompts)) == len(prompts)
    assert len({r.fingerprint for r in ep.requests}) == len(ep.requests)
    # constraints duros en el prompt + negative anti-powerpoint
    for r in ep.requests:
        assert "documentary photography" in r.prompt
        assert any(lens in r.prompt for lens in ("mm", "macro"))
        assert "powerpoint" in r.negative_prompt and "duplicate" in r.negative_prompt


# --- 4) El MGL ejecuta VIS-2 sin colapsar en reutilización -------------------

def test_mgl_generates_unique_asset_per_shot(tmp_path):
    provider = _Echo()
    mgl = MediaGenerationLayer(router=ProviderRouter(image_providers=[provider]), store=AssetStore(base_dir=str(tmp_path)))

    plan = build_visual_plan(_FAST_DARK, _SCENE, scene_duration=14.0)
    ep = compile_execution(plan, _SCENE)
    assets = [mgl.generate_for_shot(r) for r in ep.requests]

    # un asset ÚNICO por plano (reuse_key="" => sin reutilización) -> NO colapso
    assert provider.calls == len(ep.requests)
    assert len({a.asset_id for a in assets}) == len(ep.requests)
    assert len({a.prompt for a in assets}) == len(ep.requests)


def test_mgl_reuses_only_explicit_motif(tmp_path):
    provider = _Echo()
    mgl = MediaGenerationLayer(router=ProviderRouter(image_providers=[provider]), store=AssetStore(base_dir=str(tmp_path)))

    from app.vis.models import ShotRequest

    def _req(shot_id, key):
        return ShotRequest(shot_id=shot_id, scene_id="s", media_type="image",
                           prompt=f"prompt {shot_id}", negative_prompt="n", reuse_key=key,
                           variation_seed=1, motion={}, lens="x", angle="y", composition="z", fingerprint=shot_id)

    a1 = mgl.generate_for_shot(_req("s1", "empire-flag"))   # genera motivo
    a2 = mgl.generate_for_shot(_req("s2", "empire-flag"))   # reutiliza motivo
    a3 = mgl.generate_for_shot(_req("s3", ""))              # único

    assert a2.asset_id == a1.asset_id        # motivo reutilizado
    assert a3.asset_id not in (a1.asset_id,) # único
    assert provider.calls == 2               # solo 2 generaciones reales (s1, s3)
