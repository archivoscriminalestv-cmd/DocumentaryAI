"""Proveedores externos (stubs preparados) — Fase 1 MGL.

Interfaces listas para integrar APIs free-tier reales más adelante. En Fase 1 no
hay integración accesible (sin clave/API directa y sin scraping), así que cada
uno lanza ``ProviderUnavailable`` y el Router hace fallback. Sustituir el cuerpo
de ``generate_*`` por la llamada real NO requiere tocar el Router ni el MGL.
"""

from app.media.providers.base import BaseProvider, ProviderUnavailable
from app.media.store.models import Asset


class _UnavailableImageProvider(BaseProvider):
    name = "unavailable"

    def generate_image(self, prompt: str) -> Asset:
        raise ProviderUnavailable(f"{self.name}: integración no configurada.")

    def generate_video(self, prompt: str) -> Asset:
        raise ProviderUnavailable(f"{self.name}: no soporta vídeo.")


class BingImageProvider(_UnavailableImageProvider):
    name = "bing-image-creator"


class LeonardoProvider(_UnavailableImageProvider):
    name = "leonardo-ai"


class PlaygroundProvider(_UnavailableImageProvider):
    name = "playground-ai"


class PikaVideoProvider(BaseProvider):
    name = "pika-labs"

    def generate_image(self, prompt: str) -> Asset:
        raise ProviderUnavailable(f"{self.name}: proveedor de vídeo, no de imagen.")

    def generate_video(self, prompt: str) -> Asset:
        raise ProviderUnavailable(f"{self.name}: integración de vídeo no configurada.")
