"""BaseProvider — interfaz abstracta de proveedor de media (Fase 1 MGL).

Invierte la dependencia: el Provider Router y el MGL dependen solo de esta
abstracción, nunca de un proveedor concreto. ``ProviderUnavailable`` señala que
un proveedor no puede atender la petición (sin clave, sin integración, fallo de
red): el Router lo usa para hacer fallback al siguiente proveedor.
"""

from abc import ABC, abstractmethod

from app.media.store.models import Asset


class ProviderUnavailable(Exception):
    """El proveedor no puede generar el asset (se debe intentar otro)."""


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate_image(self, prompt: str) -> Asset:
        """Genera una imagen para ``prompt`` y devuelve un Asset normalizado."""
        ...

    @abstractmethod
    def generate_video(self, prompt: str) -> Asset:
        """Genera un vídeo para ``prompt`` y devuelve un Asset normalizado."""
        ...
