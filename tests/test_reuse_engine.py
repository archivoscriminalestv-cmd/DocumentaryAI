"""Tests del Asset Reuse Engine + integración MGL (Fase 3). Sin red, sin ML."""

import time

from app.media.generation.mgl import MediaGenerationLayer
from app.media.generation.provider_router import ProviderRouter
from app.media.providers.base import BaseProvider, ProviderUnavailable
from app.media.reuse.reuse_engine import ReuseEngine, find_best_match
from app.media.store.asset_store import AssetStore
from app.media.store.models import Asset
from app.domain.narrative.scene import Scene


# --- Provider falso que cuenta llamadas (para probar que NO se genera al reusar)

class _CountingProvider(BaseProvider):
    name = "fake-image"

    def __init__(self) -> None:
        self.calls = 0

    def generate_image(self, prompt: str) -> Asset:
        self.calls += 1
        return Asset(
            asset_id=f"asset-{self.calls}", type="image", prompt=prompt,
            provider=self.name, path=f"/tmp/{self.calls}.png", timestamp=time.time(),
        )

    def generate_video(self, prompt: str) -> Asset:
        raise ProviderUnavailable("fake no genera vídeo")


def _store(tmp_path) -> AssetStore:
    return AssetStore(base_dir=str(tmp_path))


def _asset(aid, prompt, type_="image", style_tags=None) -> Asset:
    return Asset(asset_id=aid, type=type_, prompt=prompt, style_tags=list(style_tags or []))


# --- ReuseEngine scoring -----------------------------------------------------

def test_identical_prompt_scores_high():
    engine = ReuseEngine()
    score = engine.score("a nuclear reactor exploding at night",
                         _asset("a1", "a nuclear reactor exploding at night"))
    assert score == 1.0


def test_distinct_prompt_scores_low():
    engine = ReuseEngine()
    score = engine.score("a calm sunny tropical beach",
                         _asset("a1", "a nuclear reactor exploding at night"))
    assert score < 0.75


def test_find_best_match_returns_asset_above_threshold(tmp_path):
    store = _store(tmp_path)
    store.add(_asset("a1", "a nuclear reactor exploding at night"))
    match = find_best_match("a nuclear reactor exploding at night", store)
    assert match is not None and match.asset_id == "a1"


def test_find_best_match_returns_none_when_no_match(tmp_path):
    store = _store(tmp_path)
    store.add(_asset("a1", "a nuclear reactor exploding at night"))
    assert find_best_match("a calm sunny tropical beach with palm trees", store) is None


def test_find_best_match_picks_highest_scoring(tmp_path):
    store = _store(tmp_path)
    store.add(_asset("a1", "a reactor at night near the river"))
    store.add(_asset("a2", "a nuclear reactor exploding at night"))
    match = find_best_match("a nuclear reactor exploding at night", store)
    assert match.asset_id == "a2"


def test_media_type_filter(tmp_path):
    store = _store(tmp_path)
    store.add(_asset("img", "a nuclear reactor exploding at night", type_="image"))
    store.add(_asset("vid", "a nuclear reactor exploding at night", type_="video"))
    assert find_best_match("a nuclear reactor exploding at night", store, media_type="video").asset_id == "vid"
    assert find_best_match("a nuclear reactor exploding at night", store, media_type="image").asset_id == "img"


def test_style_tags_metadata_influences_score():
    engine = ReuseEngine()
    asset = _asset("a1", "a reactor scene", style_tags=["cinematic", "dark"])
    with_match = engine.score("a reactor scene", asset, style_tags=["cinematic", "dark"])
    with_mismatch = engine.score("a reactor scene", asset, style_tags=["bright", "cartoon"])
    assert with_match > with_mismatch


# --- AssetStore tracking -----------------------------------------------------

def test_register_reuse_increments_and_records_scene(tmp_path):
    store = _store(tmp_path)
    asset = _asset("a1", "p"); asset.scene_id = "sc1"
    store.add(asset)
    store.register_reuse("a1", "sc2")
    store.register_reuse("a1", "sc3")
    store.register_reuse("a1", "sc2")  # duplicado -> no se repite
    updated = store.get("a1")
    assert updated.reuse_count == 3
    assert updated.reused_scene_ids == ["sc2", "sc3"]


def test_old_index_without_new_field_loads_with_default(tmp_path):
    # Compatibilidad: índice antiguo sin reused_scene_ids -> default [].
    legacy = Asset.from_dict({"asset_id": "a1", "type": "image", "prompt": "p"})
    assert legacy.reused_scene_ids == []
    assert legacy.reuse_count == 0


# --- Integración MGL: reutilizar vs generar ----------------------------------

def _mgl(tmp_path):
    provider = _CountingProvider()
    router = ProviderRouter(image_providers=[provider])
    mgl = MediaGenerationLayer(router=router, store=_store(tmp_path), reuse_threshold=0.75)
    return mgl, provider


def test_mgl_generates_then_reuses(tmp_path):
    mgl, provider = _mgl(tmp_path)

    a1 = mgl.generate_for_scene(Scene("sc1", "A nuclear reactor exploding at night", "", []))
    assert provider.calls == 1  # primera escena -> se genera

    a2 = mgl.generate_for_scene(Scene("sc2", "A nuclear reactor exploding at night", "", []))
    assert provider.calls == 1  # prompt similar -> REUSO, no se genera de nuevo
    assert a2.asset_id == a1.asset_id
    assert a2.reuse_count == 1
    assert "sc2" in a2.reused_scene_ids


def test_mgl_generates_new_for_distinct_prompt(tmp_path):
    mgl, provider = _mgl(tmp_path)
    mgl.generate_for_scene(Scene("sc1", "A nuclear reactor exploding at night", "", []))
    mgl.generate_for_scene(Scene("sc2", "A calm sunny tropical beach with palm trees", "", []))
    assert provider.calls == 2  # prompts distintos -> dos generaciones


def test_mgl_reuse_reduces_generation_across_many_scenes(tmp_path):
    mgl, provider = _mgl(tmp_path)
    for i in range(5):
        mgl.generate_for_scene(Scene(f"sc{i}", "A nuclear reactor exploding at night", "", []))
    assert provider.calls == 1  # 5 escenas iguales -> 1 sola generación
    asset = mgl._store.all()[0]
    assert asset.reuse_count == 4
    assert len(asset.reused_scene_ids) == 4


def test_mgl_persists_assets_in_store(tmp_path):
    mgl, _ = _mgl(tmp_path)
    mgl.generate_for_scene(Scene("sc1", "A nuclear reactor exploding at night", "", []))
    mgl.generate_for_scene(Scene("sc2", "A calm sunny tropical beach with palm trees", "", []))
    assert len(mgl._store.all()) == 2  # el store crece como base reutilizable
