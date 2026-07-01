"""ProviderRouter — orquestador desacoplado de providers (Fase A→B).

Evolución del router a un verdadero orquestador: la selección y la salud viven en
``ProviderRegistry`` (fuente de verdad, basada en metadata declarativa). El Router
conserva su interfaz previa (constructor por listas + ``generate``) para no romper
el resto del sistema ni los tests existentes: cuando se construye con listas, se
les asigna metadata automática (prioridad por orden), y la orquestación se delega
al registry. NO contiene lógica específica de ningún proveedor.
"""

from app.media.providers.base import BaseProvider, ProviderUnavailable
from app.media.providers.provider_registry import ProviderMetadata, ProviderRegistry
from app.media.store.models import Asset

_PRIORITY_BASE = 1000
_PRIORITY_STEP = 10


def _auto_metadata(provider: BaseProvider, media_type: str, priority: int) -> ProviderMetadata:
    """Metadata derivada de un provider sin declaración explícita (compat listas).

    El provider puede declarar atributos opcionales (cost/supports_*/status/...);
    si no, se usan defaults sensatos.
    """
    return ProviderMetadata(
        name=getattr(provider, "name", "provider"),
        media_type=media_type,
        priority=priority,
        cost=getattr(provider, "cost", "free"),
        supports_style=getattr(provider, "supports_style", True),
        supports_hd=getattr(provider, "supports_hd", False),
        supports_video=getattr(provider, "supports_video", media_type == "video"),
        status=getattr(provider, "status", "online"),
        max_resolution=getattr(provider, "max_resolution", ""),
    )


class ProviderRouter:
    def __init__(
        self,
        image_providers: list[BaseProvider] | None = None,
        video_providers: list[BaseProvider] | None = None,
        registry: ProviderRegistry | None = None,
    ) -> None:
        self._registry = registry or ProviderRegistry()
        if registry is None:
            for index, provider in enumerate(image_providers or []):
                self._registry.register(
                    provider, _auto_metadata(provider, "image", _PRIORITY_BASE - index * _PRIORITY_STEP)
                )
            for index, provider in enumerate(video_providers or []):
                self._registry.register(
                    provider, _auto_metadata(provider, "video", _PRIORITY_BASE - index * _PRIORITY_STEP)
                )

    @property
    def registry(self) -> ProviderRegistry:
        return self._registry

    def register_image_provider(self, provider: BaseProvider, priority: int = 100) -> None:
        self._registry.register(provider, _auto_metadata(provider, "image", priority))

    def register_video_provider(self, provider: BaseProvider, priority: int = 100) -> None:
        self._registry.register(provider, _auto_metadata(provider, "video", priority))

    def generate(self, prompt: str, media_type: str = "image", **requirements) -> Asset:
        return self._registry.generate(prompt, media_type, **requirements)


def default_router(asset_output_dir: str) -> ProviderRouter:
    """Router por defecto: registry con metadata declarativa.

    Provider REAL preferido (prioridad alta) + Mock local como red de seguridad
    offline (prioridad baja). Añadir Leonardo/Bing/Playground/Pika/Haiper en el
    futuro es SOLO ``registry.register(provider, ProviderMetadata(...))``.
    """
    from app.media.providers.ffmpeg_video import FfmpegVideoProvider
    from app.media.providers.mock import MockImageProvider
    from app.media.providers.real_image import RealImageProvider

    registry = ProviderRegistry()
    registry.register(
        RealImageProvider(asset_output_dir),
        ProviderMetadata(
            name="pollinations.ai", media_type="image", priority=100, cost="free",
            supports_style=True, supports_hd=True, supports_video=False,
            status="online", max_resolution="1280x720",
        ),
    )
    registry.register(
        MockImageProvider(asset_output_dir),
        ProviderMetadata(
            name="mock-image", media_type="image", priority=10, cost="free",
            supports_style=True, supports_hd=False, supports_video=False,
            status="online", max_resolution="1280x720",
        ),
    )
    registry.register(
        FfmpegVideoProvider(asset_output_dir),
        ProviderMetadata(
            name="ffmpeg-video", media_type="video", priority=100, cost="free",
            supports_style=True, supports_hd=False, supports_video=True,
            status="online", max_resolution="1280x720",
        ),
    )
    return ProviderRouter(registry=registry)


__all__ = ["ProviderRouter", "ProviderUnavailable", "default_router"]
