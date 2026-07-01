"""Tests de la estrategia de proveedores con prioridad + fallback (VPL-003)."""

import pytest

from app.vpl import ProviderChain, VPLConfig, build_chain, build_provider, make_provider
from app.vpl.models import GeneratedAsset, ProviderCapabilities
from app.vpl.provider import ProviderError
from app.vpl.strategy import resolve_chain_names
from app.vsc.models import VisualGenerationRequest


def _req(shot_id="s1"):
    return VisualGenerationRequest(
        shot_id=shot_id, scene_id="sc", media_type="image", prompt="a reactor", negative_prompt="cartoon",
        global_style="g", scene_style="s", shot_style="sh", camera="FX6", lens="35mm",
        lighting="soft", composition="thirds", color="muted", environment="Almassora", subject="Coquito",
        provider_constraints={"width": 1280, "height": 720, "aspect_ratio": "16:9"},
        reuse_key="", seed=7, seed_strategy="per_scene", motion_hint="locked",
    )


class FakeProvider:
    """Proveedor de prueba con disponibilidad y resultado configurables."""

    def __init__(self, name, *, available=True, fail=False, transient=False, cost=0.04):
        self.name = name
        self.model = f"{name}-model"
        self._available = available
        self._fail = fail
        self._transient = transient
        self._cost = cost
        self.calls = 0

    def is_available(self):
        return self._available

    def capabilities(self):
        return ProviderCapabilities(name=self.name, model=self.model, cost_per_image=self._cost,
                                    available=self._available)

    def generate(self, request):
        self.calls += 1
        if self._fail:
            raise ProviderError(f"{self.name} falló", transient=self._transient)
        return GeneratedAsset(
            shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=self.model,
            prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
            width=1280, height=720, cost=self._cost, image_bytes=b"\x89PNG" + self.name.encode(),
            metadata={"src": self.name},
        )


# --- fallback ----------------------------------------------------------------

def test_primary_failure_falls_back_to_secondary():
    primary = FakeProvider("openai", fail=True)
    secondary = FakeProvider("imagen")
    chain = ProviderChain([primary, secondary])
    asset = chain.generate(_req())
    assert asset.provider == "imagen"
    assert primary.calls == 1 and secondary.calls == 1
    assert asset.metadata["chain_winner"] == "imagen"
    assert asset.metadata["chain_fallback"] is True
    assert asset.metadata["chain_attempted"] == ["openai:error", "imagen:ok"]


def test_unavailable_provider_is_skipped():
    primary = FakeProvider("openai", available=False)
    secondary = FakeProvider("mock")
    chain = ProviderChain([primary, secondary])
    asset = chain.generate(_req())
    assert asset.provider == "mock"
    assert primary.calls == 0                       # no se intenta si no está disponible
    assert "openai:unavailable" in asset.metadata["chain_attempted"]


def test_winner_without_fallback_has_clean_metadata():
    chain = ProviderChain([FakeProvider("openai"), FakeProvider("mock")])
    asset = chain.generate(_req())
    assert asset.provider == "openai"
    assert asset.metadata["chain_fallback"] is False
    assert asset.metadata["chain_attempted"] == ["openai:ok"]


def test_all_providers_fail_raises():
    chain = ProviderChain([FakeProvider("openai", fail=True), FakeProvider("imagen", available=False)])
    with pytest.raises(ProviderError):
        chain.generate(_req())


def test_chain_preserves_transient_for_retry():
    chain = ProviderChain([FakeProvider("openai", fail=True, transient=True)])
    with pytest.raises(ProviderError) as exc:
        chain.generate(_req())
    assert exc.value.transient is True


def test_chain_is_available_if_any_link_available():
    assert ProviderChain([FakeProvider("a", available=False), FakeProvider("b")]).is_available() is True
    assert ProviderChain([FakeProvider("a", available=False)]).is_available() is False


# --- resolución / construcción ----------------------------------------------

def test_resolve_chain_appends_mock_and_dedups():
    cfg = VPLConfig(provider_chain=["openai", "openai", "imagen"])
    assert resolve_chain_names(cfg) == ["openai", "imagen", "mock"]


def test_resolve_chain_default_from_primary():
    assert resolve_chain_names(VPLConfig(provider="flux")) == ["flux", "mock"]


def test_resolve_chain_drops_unknown_names():
    cfg = VPLConfig(provider_chain=["bogus", "imagen"])
    assert resolve_chain_names(cfg) == ["imagen", "mock"]


def test_build_chain_constructs_real_adapters():
    chain = build_chain(VPLConfig(provider_chain=["openai", "mock"]))
    assert [p.name for p in chain.providers] == ["openai", "mock"]
    assert chain.name == "openai>mock"


def test_build_provider_returns_chain_when_fallback_enabled():
    chain = build_provider(VPLConfig(provider="openai", fallback=True))
    assert isinstance(chain, ProviderChain)
    assert chain.providers[-1].name == "mock"


def test_build_provider_returns_single_when_no_fallback():
    provider = build_provider(VPLConfig(provider="mock"))
    assert not isinstance(provider, ProviderChain)
    assert provider.name == "mock"


def test_chain_reaches_mock_when_real_unconfigured(monkeypatch):
    # Sin claves reales, la cadran cae hasta mock y SIEMPRE produce imagen.
    for var in ("OPENAI_API_KEY", "GOOGLE_API_KEY", "FLUX_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    chain = build_chain(VPLConfig(provider_chain=["openai", "imagen", "flux", "mock"]))
    asset = chain.generate(_req())
    assert asset.provider == "mock"
    assert asset.image_bytes
