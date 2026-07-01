"""Interfaz provider-neutral del VPL.

TODO proveedor implementa exactamente ``VisualProvider.generate(request) ->
GeneratedAsset``. Ninguna lógica específica de proveedor sale de los adapters.
``ProviderError(transient=...)`` distingue fallos reintentables (red/timeouts/rate
limits) de permanentes (auth, no implementado).
"""

from typing import Protocol

from app.vpl.models import GeneratedAsset, ProviderCapabilities


class ProviderError(Exception):
    def __init__(self, message: str, *, transient: bool = False) -> None:
        super().__init__(message)
        self.transient = transient


class VisualProvider(Protocol):
    name: str
    model: str

    def generate(self, request) -> GeneratedAsset:
        """VisualGenerationRequest -> GeneratedAsset (con ``image_bytes``)."""
        ...

    def is_available(self) -> bool:
        """¿Tiene el proveedor lo que necesita (credenciales) para ejecutar?"""
        ...

    def capabilities(self) -> ProviderCapabilities:
        """Capacidades declarativas del proveedor (coste, negativos, resolución…)."""
        ...
