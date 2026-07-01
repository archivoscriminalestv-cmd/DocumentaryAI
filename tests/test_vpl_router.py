"""Tests del Provider Router (prioridad automática, validación, circuit-breaker)."""

import io

import pytest
from PIL import Image

from app.vpl.models import GeneratedAsset
from app.vpl.provider import ProviderError
from app.vpl.router import ProviderRouter, build_router, validate_image
from app.vsc.models import VisualGenerationRequest


def _png_bytes(color=(10, 20, 30)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (64, 36), color).save(buf, "PNG")
    return buf.getvalue()


_VALID_PNG = _png_bytes()


def _req(shot_id="s1"):
    return VisualGenerationRequest(
        shot_id=shot_id, scene_id="sc", media_type="image", prompt="a reactor", negative_prompt="cartoon",
        global_style="g", scene_style="s", shot_style="sh", camera="FX6", lens="35mm",
        lighting="soft", composition="thirds", color="muted", environment="Almassora", subject="Coquito",
        provider_constraints={"width": 1280, "height": 720, "aspect_ratio": "16:9"},
        reuse_key="", seed=7, seed_strategy="per_scene", motion_hint="locked",
    )


class FakeProvider:
    def __init__(self, name, *, available=True, fail=None, image=_VALID_PNG):
        self.name = name
        self.model = f"{name}-model"
        self._available = available
        self._fail = fail              # None | ProviderError
        self._image = image
        self.calls = 0

    def is_available(self):
        return self._available

    def generate(self, request):
        self.calls += 1
        if self._fail is not None:
            raise self._fail
        return GeneratedAsset(
            shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=self.model,
            prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
            width=1280, height=720, image_bytes=self._image, metadata={},
        )


# --- validación de calidad ---------------------------------------------------

def test_validate_image_accepts_real_png():
    a = GeneratedAsset(shot_id="s", scene_id="sc", provider="p", model="m", prompt="", negative_prompt="",
                       seed=0, width=64, height=36, image_bytes=_VALID_PNG)
    validate_image(a)  # no lanza


def test_validate_image_rejects_empty():
    a = GeneratedAsset(shot_id="s", scene_id="sc", provider="p", model="m", prompt="", negative_prompt="",
                       seed=0, width=0, height=0, image_bytes=b"")
    with pytest.raises(ProviderError):
        validate_image(a)


def test_validate_image_rejects_corrupt():
    a = GeneratedAsset(shot_id="s", scene_id="sc", provider="p", model="m", prompt="", negative_prompt="",
                       seed=0, width=8, height=8, image_bytes=b"\x00" * 4096)
    with pytest.raises(ProviderError):
        validate_image(a)


# --- enrutado y fallback -----------------------------------------------------

def test_router_uses_first_available_and_annotates():
    primary, secondary = FakeProvider("imagen"), FakeProvider("openai")
    asset = ProviderRouter([primary, secondary]).generate(_req())
    assert asset.provider == "imagen"
    assert primary.calls == 1 and secondary.calls == 0
    assert asset.metadata["router_winner"] == "imagen"
    assert asset.metadata["router_fallback"] is False


def test_router_falls_back_on_error():
    primary = FakeProvider("imagen", fail=ProviderError("boom", transient=True))
    secondary = FakeProvider("openai")
    asset = ProviderRouter([primary, secondary]).generate(_req())
    assert asset.provider == "openai"
    assert asset.metadata["router_fallback"] is True
    assert asset.metadata["router_attempted"] == ["imagen:error", "openai:ok"]


def test_router_regenerates_on_invalid_image():
    bad = FakeProvider("imagen", image=b"not-an-image")
    good = FakeProvider("openai")
    asset = ProviderRouter([bad, good]).generate(_req())
    assert asset.provider == "openai"
    assert any("invalid_image" in a for a in asset.metadata["router_attempted"])


def test_router_circuit_breaker_disables_permanent_failure():
    dead = FakeProvider("openai", fail=ProviderError("billing hard limit", transient=True))
    good = FakeProvider("huggingface")
    router = ProviderRouter([dead, good])
    router.generate(_req("s1"))
    router.generate(_req("s2"))
    # 'openai' falla por facturación (hard) -> deshabilitado tras el 1er intento.
    assert dead.calls == 1
    assert good.calls == 2


def test_router_skips_unavailable():
    a = FakeProvider("imagen", available=False)
    b = FakeProvider("huggingface")
    asset = ProviderRouter([a, b]).generate(_req())
    assert asset.provider == "huggingface" and a.calls == 0


def test_router_all_fail_raises():
    a = FakeProvider("imagen", fail=ProviderError("x", transient=False))
    b = FakeProvider("openai", fail=ProviderError("y", transient=False))
    with pytest.raises(ProviderError):
        ProviderRouter([a, b]).generate(_req())


# --- build_router por prioridad ---------------------------------------------

def test_build_router_orders_by_priority(monkeypatch):
    for var in ("OPENAI_API_KEY", "GOOGLE_API_KEY", "HF_TOKEN", "REPLICATE_API_TOKEN"):
        monkeypatch.setenv(var, "x")
    router = build_router(["replicate", "openai", "imagen", "huggingface"])
    assert [p.name for p in router.providers] == ["imagen", "openai", "huggingface", "replicate"]


def test_build_router_excludes_mock_and_requires_valid():
    with pytest.raises(ProviderError):
        build_router([])
    with pytest.raises(ProviderError):
        build_router(["mock"])
