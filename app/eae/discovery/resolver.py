"""Source Resolver (EAE-004) — selección de proveedores por capacidad, sin hardcodear.

Escoge los proveedores para una necesidad según: tipo de evidencia (medio soportado),
licencia requerida, idioma, coste, fiabilidad y capacidad declarada. Devuelve los
seleccionados (ordenados, pensando como documentalista: prioridad → fiabilidad → coste) y
los descartados con su motivo (auditable). No consulta red.
"""

from app.eae.discovery.providers.base import DiscoveryProvider
from app.eae.discovery.registry import SourceRegistry

_RELIABILITY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "UNKNOWN": 3}
_COST_RANK = {"free": 0, "restricted": 1, "paid": 2, "UNKNOWN": 3}


def _license_ok(provider: DiscoveryProvider, reqs: list[str]) -> bool:
    if not reqs:
        return True
    supported = set(provider.supported_licenses())
    return bool(supported & set(reqs)) or "UNKNOWN" in supported


class SourceResolver:
    def __init__(self, registry: SourceRegistry) -> None:
        self._registry = registry

    def select(self, category: str, *, license_requirements=None, max_cost=None,
               min_reliability=None, capability=None):
        """Devuelve ``(seleccionados, descartados)``.

        ``descartados`` es una lista de ``(provider, motivo)``. ``seleccionados`` va
        ordenado de forma determinista (prioridad asc, fiabilidad, coste, nombre)."""
        reqs = [r for r in (license_requirements or []) if r]
        selected, discarded = [], []
        for provider in self._registry.by_media(category):
            reason = self._reject_reason(provider, reqs, max_cost, min_reliability, capability)
            if reason:
                discarded.append((provider, reason))
            else:
                selected.append(provider)
        selected.sort(key=lambda p: (
            p.priority(), _RELIABILITY_RANK.get(p.reliability(), 9),
            _COST_RANK.get(p.cost(), 9), p.name))
        return selected, discarded

    @staticmethod
    def _reject_reason(provider, reqs, max_cost, min_reliability, capability) -> str:
        if not _license_ok(provider, reqs):
            return f"licencia incompatible (requiere {reqs})"
        if max_cost is not None and _COST_RANK.get(provider.cost(), 9) > _COST_RANK.get(max_cost, 9):
            return f"coste '{provider.cost()}' supera el máximo '{max_cost}'"
        if min_reliability is not None and \
                _RELIABILITY_RANK.get(provider.reliability(), 9) > _RELIABILITY_RANK.get(min_reliability, 9):
            return f"fiabilidad '{provider.reliability()}' por debajo de '{min_reliability}'"
        if capability is not None and capability not in provider.capabilities():
            return f"no declara la capacidad '{capability}'"
        return ""

    # Compatibilidad: lista simple de candidatos (selección sin filtros estrictos).
    def candidates(self, category: str, license_requirements=None) -> list[DiscoveryProvider]:
        selected, _ = self.select(category, license_requirements=license_requirements)
        return selected
