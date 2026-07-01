"""Tests de VAI (Visual AI Director). Determinista, sin red, sin IA, sin proveedor."""

import time

from app.media.generation.mgl import MediaGenerationLayer
from app.media.generation.provider_router import ProviderRouter
from app.media.providers.base import BaseProvider
from app.media.store.asset_store import AssetStore
from app.media.store.models import Asset
from app.vai import VisualContext, VisualDirector, build_context
from app.vis.models import PlannedShot
from app.vis import build_visual_plan
from app.rda.models import CinematicProfile
from app.domain.narrative.scene import Scene


def _shot(index=0, shot_type="impact", move="push_in", asset_type="image", reuse_key="") -> PlannedShot:
    return PlannedShot(
        id=f"scene-01::shot-{index:02d}", scene_id="scene-01", index=index, shot_type=shot_type,
        camera_move=move, camera_intensity=0.8, lighting="low-key chiaroscuro", duration=3.0,
        asset_type=asset_type, reuse_key=reuse_key, fact_ids=["f1"],
    )


_CTX = VisualContext(subject="a nuclear reactor", style="cinematic", color_temperature="cool",
                     saturation="muted", lighting_key="low-key", realism_level="ultra")


# --- motores producen decisiones ---------------------------------------------

def test_engines_contribute_descriptors():
    d = VisualDirector()
    spec = d.specify(_shot(), _CTX)
    for field in (spec.composition, spec.camera_language, spec.lens, spec.lighting,
                  spec.atmosphere, spec.color_grade, spec.realism, spec.quality, spec.negatives):
        assert field and all(isinstance(x, str) and x for x in field)


# --- el prompt final es rico y bien formado ----------------------------------

def test_prompt_is_rich_and_clean():
    req = VisualDirector().direct(_shot(), _CTX)
    p = req.prompt.lower()
    assert "a nuclear reactor" in p
    assert any(t in p for t in ("mm", "macro"))     # lente
    assert "light" in p                              # iluminación
    assert "grade" in p or "look" in p               # color grading
    assert "photorealistic" in p                     # realismo
    # sin repeticiones exactas de fragmentos
    frags = [f.strip() for f in req.prompt.split(",")]
    assert len(frags) == len({f.lower() for f in frags})


def test_negative_prompt_generated():
    req = VisualDirector().direct(_shot(), _CTX)
    n = req.negative_prompt.lower()
    for bad in ("cartoon", "watermark", "low quality", "deformed", "duplicate"):
        assert bad in n


# --- VAI NO modifica las decisiones de VIS -----------------------------------

def test_vai_preserves_vis_decisions():
    shot = _shot(move="drone", asset_type="image", reuse_key="motif-1")
    req = VisualDirector().direct(shot, _CTX)
    assert req.motion == {"move": "drone", "intensity": 0.8}   # cámara intacta
    assert req.media_type == "image"
    assert req.reuse_key == "motif-1"                          # reuse passthrough


# --- variación entre planos (anti-PowerPoint) --------------------------------

def test_consecutive_shots_vary():
    d = VisualDirector()
    a = d.direct(_shot(index=0, shot_type="wide"), _CTX)
    b = d.direct(_shot(index=1, shot_type="detail"), _CTX)
    assert a.prompt != b.prompt
    assert a.composition != b.composition or a.lens != b.lens


# --- independencia de proveedor ----------------------------------------------

def test_provider_independent_output():
    req = VisualDirector().direct(_shot(), _CTX)
    low = req.prompt.lower()
    for provider_token in ("--ar", "midjourney", "pollinations", "stable diffusion", "::"):
        assert provider_token not in low
    assert req.specification is not None          # representación ESTRUCTURADA disponible
    assert req.specification.lens                  # para proveedores con params


# --- el grade refleja el contexto (warm vs cool) -----------------------------

def test_color_grade_reflects_context():
    warm = VisualDirector().direct(_shot(), VisualContext(subject="x", color_temperature="warm"))
    cool = VisualDirector().direct(_shot(), VisualContext(subject="x", color_temperature="cool"))
    assert warm.prompt != cool.prompt
    assert "warm" in warm.prompt.lower() and "cold" in cool.prompt.lower()


# --- determinismo ------------------------------------------------------------

def test_deterministic():
    a = VisualDirector().direct(_shot(), _CTX)
    b = VisualDirector().direct(_shot(), _CTX)
    assert a.prompt == b.prompt and a.negative_prompt == b.negative_prompt


# --- Visual Memory almacena decisiones ---------------------------------------

def test_visual_memory_records():
    d = VisualDirector()
    req = d.direct(_shot(), _CTX)
    stored = d.memory.get(req.shot_id)
    assert stored is not None and stored.subject == "a nuclear reactor"


# --- build_context desde escena + perfil RDA ---------------------------------

def test_build_context_from_profile():
    scene = Scene(id="s", title="The eruption", narration="N", fact_ids=[])
    profile = CinematicProfile(
        reference="r", source_type="rda", width=1920, height=1080, aspect_ratio="16:9", fps=24.0,
        duration=10.0, sample_fps=4.0, shot_count=5, avg_shot_length=2.0, median_shot_length=2.0,
        min_shot_length=1.0, max_shot_length=3.0, shot_length_stddev=0.5, cuts_per_minute=30.0,
        pacing_tier="fast", shot_length_variety="varied", brightness_mean=50.0, contrast_mean=70.0,
        lighting_tendency="low-key high-contrast", warmth_mean=20.0, colorfulness_mean=60.0,
        color_temperature="warm", saturation_tendency="vivid", motion_mean=0.1, movement_tendency="dynamic",
    )
    ctx = build_context(scene, profile, style="cinematic")
    assert ctx.subject == "The eruption" and ctx.color_temperature == "warm"
    assert ctx.saturation == "vivid" and ctx.lighting_key == "low-key"


# --- Integración VIS -> VAI -> MGL (cadena real) -----------------------------

class _Echo(BaseProvider):
    name = "echo"

    def __init__(self): self.calls = 0

    def generate_image(self, prompt):
        self.calls += 1
        return Asset(asset_id=f"a{self.calls}", type="image", prompt=prompt, provider=self.name, timestamp=time.time())

    def generate_video(self, prompt):
        raise NotImplementedError


def test_vis_to_vai_to_mgl_chain(tmp_path):
    scene = Scene(id="scene-01", title="A collapsing bridge", narration="A long narration about the event", fact_ids=["f1"])
    plan = build_visual_plan(_neutral_profile(), scene, scene_duration=12.0)
    ctx = build_context(scene, _neutral_profile(), style="documentary")
    director = VisualDirector()

    provider = _Echo()
    mgl = MediaGenerationLayer(router=ProviderRouter(image_providers=[provider]), store=AssetStore(base_dir=str(tmp_path)))

    assets = []
    for ps in plan.shots:
        req = director.direct(ps, ctx)
        assets.append(mgl.generate_for_shot(req))

    assert provider.calls == len(plan.shots)                 # un asset por plano
    assert len({a.asset_id for a in assets}) == len(plan.shots)  # únicos (sin colapso)
    assert len({a.prompt for a in assets}) == len(plan.shots)    # prompts distintos


def _neutral_profile() -> CinematicProfile:
    return CinematicProfile(
        reference="n", source_type="default", width=1920, height=1080, aspect_ratio="16:9", fps=24.0,
        duration=0.0, sample_fps=4.0, shot_count=0, avg_shot_length=2.5, median_shot_length=2.5,
        min_shot_length=1.0, max_shot_length=5.0, shot_length_stddev=1.0, cuts_per_minute=24.0,
        pacing_tier="fast", shot_length_variety="varied", brightness_mean=120.0, contrast_mean=40.0,
        lighting_tendency="balanced", warmth_mean=0.0, colorfulness_mean=25.0, color_temperature="neutral",
        saturation_tendency="moderate", motion_mean=0.04, movement_tendency="dynamic",
    )
