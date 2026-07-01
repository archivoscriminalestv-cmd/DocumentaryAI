"""Tests Fase B: orquestación multi-provider (registry + router). Sin red, sin IA."""

import pytest

from app.media.generation.provider_router import ProviderRouter
from app.media.providers.base import BaseProvider, ProviderUnavailable
from app.media.providers.provider_registry import ProviderMetadata, ProviderRegistry
from app.media.store.models import Asset


class FakeProvider(BaseProvider):
    """Provider falso: puede fallar las primeras ``fail_times`` llamadas."""

    def __init__(self, name: str, fail_times: int = 0) -> None:
        self.name = name
        self._fail = fail_times
        self.calls = 0

    def generate_image(self, prompt: str) -> Asset:
        self.calls += 1
        if self.calls <= self._fail:
            raise ProviderUnavailable(f"{self.name}: fail #{self.calls}")
        return Asset(asset_id=f"{self.name}-{self.calls}", type="image", prompt=prompt, provider=self.name)

    def generate_video(self, prompt: str) -> Asset:
        raise ProviderUnavailable(f"{self.name}: no video")


class Clock:
    def __init__(self, t: float = 1000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def _meta(name, *, priority=100, media_type="image", cost="free", hd=False, style=True, video=False, status="online"):
    return ProviderMetadata(
        name=name, media_type=media_type, priority=priority, cost=cost,
        supports_hd=hd, supports_style=style, supports_video=video, status=status,
    )


# --- registro + selección ----------------------------------------------------

def test_registers_multiple_providers():
    reg = ProviderRegistry()
    reg.register(FakeProvider("a"), _meta("a"))
    reg.register(FakeProvider("b"), _meta("b"))
    assert {m.name for m in reg.all_metadata()} == {"a", "b"}


def test_selects_by_priority():
    reg = ProviderRegistry()
    reg.register(FakeProvider("low"), _meta("low", priority=50))
    reg.register(FakeProvider("high"), _meta("high", priority=100))
    asset = reg.generate("p", "image")
    assert asset.provider == "high"  # mayor prioridad gana


def test_offline_provider_is_excluded():
    reg = ProviderRegistry()
    reg.register(FakeProvider("offline"), _meta("offline", priority=100, status="offline"))
    reg.register(FakeProvider("online"), _meta("online", priority=10, status="online"))
    asset = reg.generate("p", "image")
    assert asset.provider == "online"


def test_incompatible_media_type_excluded():
    reg = ProviderRegistry()
    reg.register(FakeProvider("img"), _meta("img", media_type="image"))
    with pytest.raises(ProviderUnavailable):
        reg.generate("p", "video")  # no hay providers de vídeo


def test_capability_filter_require_hd():
    reg = ProviderRegistry()
    reg.register(FakeProvider("sd"), _meta("sd", priority=100, hd=False))
    reg.register(FakeProvider("hd"), _meta("hd", priority=50, hd=True))
    asset = reg.generate("p", "image", require_hd=True)
    assert asset.provider == "hd"  # sólo el HD cumple la capacidad


def test_fallback_within_single_call():
    reg = ProviderRegistry()
    failing = FakeProvider("primary", fail_times=1)
    reg.register(failing, _meta("primary", priority=100))
    reg.register(FakeProvider("backup"), _meta("backup", priority=50))
    asset = reg.generate("p", "image")
    assert asset.provider == "backup" and failing.calls == 1


def test_repeated_failures_disable_then_recover():
    clock = Clock()
    reg = ProviderRegistry(max_failures=2, cooldown_seconds=60.0, clock=clock)
    primary = FakeProvider("primary", fail_times=2)  # falla 2 veces, luego OK
    backup = FakeProvider("backup")
    reg.register(primary, _meta("primary", priority=100))
    reg.register(backup, _meta("backup", priority=50))

    # 2 llamadas: primary falla las dos -> se deshabilita (failure_count>=2).
    assert reg.generate("p", "image").provider == "backup"
    assert reg.generate("p", "image").provider == "backup"
    assert reg.health_of("primary").disabled_until > 0

    # Dentro del cooldown: primary excluido (no se vuelve a llamar).
    assert reg.generate("p", "image").provider == "backup"
    assert primary.calls == 2

    # Pasado el cooldown: primary vuelve a ser elegible y ya se recupera (OK).
    clock.advance(61)
    asset = reg.generate("p", "image")
    assert asset.provider == "primary"            # recuperado
    assert reg.health_of("primary").failure_count == 0  # salud reseteada


def test_no_compatible_provider_raises():
    reg = ProviderRegistry()
    with pytest.raises(ProviderUnavailable):
        reg.generate("p", "image")


# --- compatibilidad: ProviderRouter sigue funcionando por listas -------------

def test_router_list_constructor_still_works():
    router = ProviderRouter(image_providers=[FakeProvider("only")])
    assert router.generate("p", "image").provider == "only"


def test_router_list_order_is_priority_with_fallback():
    primary = FakeProvider("primary", fail_times=1)
    router = ProviderRouter(image_providers=[primary, FakeProvider("backup")])
    asset = router.generate("p", "image")  # primary (orden 0) falla -> backup
    assert asset.provider == "backup"


def test_router_exposes_registry_for_future_registration():
    router = ProviderRouter(image_providers=[FakeProvider("a")])
    # Registrar un nuevo provider con prioridad superior -> pasa a seleccionarse,
    # sin tocar el resto del sistema (criterio de éxito Fase B).
    router.register_image_provider(FakeProvider("b"), priority=5000)
    asset = router.generate("p", "image")
    assert asset.provider == "b"
    assert "b" in {m.name for m in router.registry.all_metadata()}
