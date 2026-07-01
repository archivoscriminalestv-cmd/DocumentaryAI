"""Tests del provider de vídeo real (FFmpeg) + orquestación + MGL (Fase C-video)."""

import os

import pytest

from app.media.generation.mgl import MediaGenerationLayer
from app.media.generation.provider_router import ProviderRouter, default_router
from app.media.providers.base import ProviderUnavailable
from app.media.providers.ffmpeg_video import FfmpegVideoProvider
from app.media.providers.provider_registry import ProviderMetadata, ProviderRegistry
from app.media.store.asset_store import AssetStore
from app.domain.narrative.scene import Scene


def _fake_runner(creates_valid=True):
    """Runner inyectado: simula ffmpeg escribiendo (o no) un .mp4 en cmd[-1]."""
    def run(cmd):
        out = cmd[-1]
        if creates_valid:
            with open(out, "wb") as handle:
                handle.write(b"\x00\x00\x00\x18ftypmp42fake mp4 bytes")
            return 0
        return 1
    return run


def _video_provider(tmp_path, **kw):
    # ffmpeg_exe ficticio + runner inyectado -> no se ejecuta ffmpeg real.
    return FfmpegVideoProvider(str(tmp_path), ffmpeg_exe="ffmpeg", runner=_fake_runner(), **kw)


# --- Provider (con runner inyectado, sin ffmpeg real) ------------------------

def test_generates_real_mp4_asset(tmp_path):
    asset = _video_provider(tmp_path).generate_video("a quiet harbor at dawn")
    assert asset.type == "video"
    assert asset.provider == "ffmpeg-video"
    assert asset.path.endswith(".mp4")
    assert os.path.exists(asset.path) and os.path.getsize(asset.path) > 0
    with open(asset.path, "rb") as handle:
        assert b"ftyp" in handle.read(16)  # contenedor mp4 real


def test_video_provider_does_not_do_image(tmp_path):
    with pytest.raises(ProviderUnavailable):
        _video_provider(tmp_path).generate_image("anything")


def test_empty_prompt_unavailable(tmp_path):
    with pytest.raises(ProviderUnavailable):
        _video_provider(tmp_path).generate_video("   ")


def test_ffmpeg_failure_degrades(tmp_path):
    provider = FfmpegVideoProvider(str(tmp_path), ffmpeg_exe="ffmpeg", runner=_fake_runner(creates_valid=False))
    with pytest.raises(ProviderUnavailable):
        provider.generate_video("a prompt")


# --- Orquestación: selección por media_type=video ----------------------------

def test_registry_selects_video_provider(tmp_path):
    reg = ProviderRegistry()
    reg.register(
        _video_provider(tmp_path),
        ProviderMetadata(name="ffmpeg-video", media_type="video", priority=100, supports_video=True),
    )
    asset = reg.generate("a scene", "video")
    assert asset.type == "video" and asset.provider == "ffmpeg-video"


def test_video_request_ignores_image_only_providers(tmp_path):
    reg = ProviderRegistry()
    reg.register(_video_provider(tmp_path), ProviderMetadata(name="vid", media_type="video", supports_video=True))
    # pedir imagen no debe devolver el provider de vídeo
    with pytest.raises(ProviderUnavailable):
        reg.generate("a scene", "image")


def test_default_router_registers_a_video_provider(tmp_path):
    router = default_router(str(tmp_path))
    metas = {m.name: m for m in router.registry.all_metadata()}
    assert "ffmpeg-video" in metas
    assert metas["ffmpeg-video"].media_type == "video"


# --- E2E: Scene -> MGL(media_type=video) -> provider -> Asset Store ----------

def test_mgl_generates_and_stores_video_asset(tmp_path):
    store = AssetStore(base_dir=str(tmp_path / "store"))
    router = ProviderRouter(registry=ProviderRegistry())
    router.register_video_provider(_video_provider(tmp_path / "vids"), priority=100)
    mgl = MediaGenerationLayer(router=router, store=store)

    asset = mgl.generate_for_scene(Scene("sc1", "A lighthouse in a storm", "", []), media_type="video")

    assert asset.type == "video" and asset.provider == "ffmpeg-video"
    assert asset.scene_id == "sc1"
    assert os.path.exists(asset.path) and os.path.getsize(asset.path) > 0
    assert store.get(asset.asset_id) is not None  # persistido en el Asset Store


def test_mgl_reuses_video_asset_for_similar_scene(tmp_path):
    store = AssetStore(base_dir=str(tmp_path / "store"))
    router = ProviderRouter(registry=ProviderRegistry())
    provider = _video_provider(tmp_path / "vids")
    router.register_video_provider(provider, priority=100)
    mgl = MediaGenerationLayer(router=router, store=store)

    a1 = mgl.generate_for_scene(Scene("sc1", "A lighthouse in a storm", "", []), media_type="video")
    a2 = mgl.generate_for_scene(Scene("sc2", "A lighthouse in a storm", "", []), media_type="video")
    assert a2.asset_id == a1.asset_id and a2.reuse_count == 1  # reuse engine compatible


# --- REAL ffmpeg (sin runner inyectado): produce un .mp4 reproducible --------

def test_live_real_ffmpeg_mp4(tmp_path):
    provider = FfmpegVideoProvider(str(tmp_path), duration=1.0, width=320, height=180)
    try:
        asset = provider.generate_video("a cinematic still of a calm forest")
    except ProviderUnavailable as exc:
        pytest.skip(f"ffmpeg no disponible: {exc}")
    assert os.path.exists(asset.path) and os.path.getsize(asset.path) > 0
    with open(asset.path, "rb") as handle:
        assert b"ftyp" in handle.read(32)  # mp4 real generado por ffmpeg
