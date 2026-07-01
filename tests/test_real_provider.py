"""Tests Fase 2: provider REAL de imágenes + e2e Scene→MGL→Real→Store.

Las pruebas deterministas inyectan el acceso HTTP (sin red). Hay además una
prueba LIVE que llama al servicio real y se omite (skip) si no hay red.
"""

import os

import pytest

from app.media.generation.mgl import MediaGenerationLayer
from app.media.generation.provider_router import ProviderRouter
from app.media.providers.base import ProviderUnavailable
from app.media.providers.mock import MockImageProvider
from app.media.providers.real_image import RealImageProvider
from app.media.store.asset_store import AssetStore
from app.domain.narrative.scene import Scene

# JPEG mínimo (cabecera válida) para inyectar como "imagen real" sin red.
_FAKE_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 32 + b"\xff\xd9"


def _ok_http(_url, _timeout):
    return _FAKE_JPEG


# --- Provider real (con HTTP inyectado) --------------------------------------

def test_real_provider_downloads_and_structures_asset(tmp_path):
    provider = RealImageProvider(str(tmp_path), http_get=_ok_http)
    asset = provider.generate_image("a cinematic nuclear reactor at night")

    assert asset.provider == "pollinations.ai"
    assert asset.provider != "mock-image"          # NO es mock
    assert asset.type == "image"
    assert os.path.exists(asset.path) and os.path.getsize(asset.path) > 0  # archivo real
    assert asset.path.endswith(".jpg")
    assert asset.url.startswith("https://image.pollinations.ai/prompt/")
    assert "reactor" in asset.url


def test_real_provider_unavailable_on_network_error(tmp_path):
    def boom(_url, _timeout):
        raise OSError("network down")

    provider = RealImageProvider(str(tmp_path), http_get=boom)
    with pytest.raises(ProviderUnavailable):
        provider.generate_image("anything")


def test_real_provider_rejects_non_image_response(tmp_path):
    provider = RealImageProvider(str(tmp_path), http_get=lambda u, t: b"<html>error</html>")
    with pytest.raises(ProviderUnavailable):
        provider.generate_image("anything")


def test_real_provider_empty_prompt(tmp_path):
    provider = RealImageProvider(str(tmp_path), http_get=_ok_http)
    with pytest.raises(ProviderUnavailable):
        provider.generate_image("   ")


def test_real_provider_does_not_do_video(tmp_path):
    provider = RealImageProvider(str(tmp_path), http_get=_ok_http)
    with pytest.raises(ProviderUnavailable):
        provider.generate_video("anything")


# --- Router: real preferido, mock como fallback ------------------------------

def test_router_prefers_real_provider(tmp_path):
    router = ProviderRouter(image_providers=[RealImageProvider(str(tmp_path), http_get=_ok_http)])
    asset = router.generate("a prompt", media_type="image")
    assert asset.provider == "pollinations.ai"


def test_router_falls_back_to_mock_when_real_fails(tmp_path):
    failing_real = RealImageProvider(str(tmp_path), http_get=lambda u, t: (_ for _ in ()).throw(OSError("down")))
    router = ProviderRouter(image_providers=[failing_real, MockImageProvider(str(tmp_path))])
    asset = router.generate("a prompt", media_type="image")
    assert asset.provider == "mock-image"  # fallback offline preservado


# --- E2E OBLIGATORIO: Scene -> MGL -> Provider REAL -> Asset Store -----------

def test_end_to_end_scene_to_real_asset_in_store(tmp_path):
    store = AssetStore(base_dir=str(tmp_path / "store"))
    router = ProviderRouter(image_providers=[RealImageProvider(str(tmp_path / "imgs"), http_get=_ok_http)])
    mgl = MediaGenerationLayer(router=router, store=store)

    asset = mgl.generate_for_scene(Scene("sc1", "A nuclear reactor at night", "", []))

    # asset creado por provider REAL (no mock) y persistido con metadata
    assert asset.provider == "pollinations.ai" and asset.provider != "mock-image"
    assert asset.scene_id == "sc1"
    assert os.path.exists(asset.path) and os.path.getsize(asset.path) > 0  # archivo real
    assert store.get(asset.asset_id) is not None                          # en el store
    assert store.all()[0].url.startswith("https://image.pollinations.ai/")


# --- LIVE (red real): se omite si no hay conectividad ------------------------

def test_live_real_external_generation(tmp_path):
    provider = RealImageProvider(str(tmp_path), width=256, height=256, timeout=90)
    try:
        asset = provider.generate_image("a cinematic documentary still of a quiet forest at dawn")
    except ProviderUnavailable as exc:
        pytest.skip(f"sin red / servicio no disponible: {exc}")

    assert asset.provider != "mock-image"
    assert os.path.exists(asset.path) and os.path.getsize(asset.path) > 0
    with open(asset.path, "rb") as handle:
        head = handle.read(8)
    assert head[:3] == b"\xff\xd8\xff" or head[:8] == b"\x89PNG\r\n\x1a\n"  # imagen real
