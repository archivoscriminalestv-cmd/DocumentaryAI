"""Source Registry (EAE-003) — registro público de proveedores de descubrimiento.

El orquestador NO hardcodea decisiones: consulta el registro. Cada proveedor declara sus
capacidades; el registro permite listarlos, filtrarlos por medio soportado y ordenarlos
por prioridad (determinista).
"""

from app.eae.discovery.providers.base import DiscoveryProvider


class SourceRegistry:
    def __init__(self, providers: list[DiscoveryProvider] | None = None) -> None:
        self._providers: list[DiscoveryProvider] = []
        for provider in providers or []:
            self.register(provider)

    def register(self, provider: DiscoveryProvider) -> None:
        self._providers.append(provider)

    def all(self) -> list[DiscoveryProvider]:
        return sorted(self._providers, key=lambda p: (p.priority(), p.name))

    def available(self) -> list[DiscoveryProvider]:
        return [p for p in self.all() if p.available()]

    def by_media(self, category: str) -> list[DiscoveryProvider]:
        """Proveedores que soportan ese medio, ordenados por prioridad (asc) y nombre."""
        return [p for p in self.all() if category in p.supported_media()]

    def capabilities(self) -> list[dict]:
        out = []
        for provider in self.all():
            cap = getattr(provider, "capability", None)
            out.append(cap().to_dict() if callable(cap) else {"name": provider.name})
        return out


def default_registry(http=None, cache=None) -> SourceRegistry:
    """Registro por defecto. Con ``http`` los proveedores reales quedan operativos; sin él
    actúan como contratos (descubrimiento offline determinista)."""
    from app.eae.discovery.providers.catalog import default_providers
    return SourceRegistry(default_providers(http, cache))
