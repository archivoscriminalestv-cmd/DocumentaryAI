"""Contrato de proveedor de descubrimiento (EAE-003).

Cada proveedor DECLARA sus capacidades públicas (medios soportados, licencias, prioridad,
coste, límites, fiabilidad, capacidades) y descubre punteros a evidencia — NUNCA descarga,
NUNCA hace scraping/Selenium/Playwright/HTML; solo APIs oficiales o fuentes definidas. El
orquestador no toma decisiones hardcodeadas: consulta estas declaraciones.

``BaseDiscoveryProvider`` es un CONTRATO: ``available()`` es False y ``discover()`` devuelve
``[]``. Las implementaciones reales (futuras) solo sobreescriben ``discover``/``available``.
"""

from dataclasses import dataclass, field
from typing import Protocol

from app.eae import UNKNOWN
from app.eae.discovery.models import DiscoveredEvidence, SourceCapability


@dataclass
class DiscoveryQuery:
    case_id: str
    need_id: str = ""
    category: str = UNKNOWN
    target: str = ""
    terms: list[str] = field(default_factory=list)
    priority: str = UNKNOWN
    license_requirements: list[str] = field(default_factory=list)
    language: str = ""
    limit: int = 25


class DiscoveryProvider(Protocol):
    name: str

    def available(self) -> bool: ...
    def supported_media(self) -> tuple: ...
    def supported_licenses(self) -> tuple: ...
    def priority(self) -> int: ...
    def cost(self) -> str: ...
    def rate_limits(self) -> dict: ...
    def capabilities(self) -> tuple: ...
    def reliability(self) -> str: ...
    def discover(self, query: DiscoveryQuery) -> list[DiscoveredEvidence]: ...


class BaseDiscoveryProvider:
    name = "base"
    _media: tuple = ()
    _licenses: tuple = (UNKNOWN,)
    _priority: int = 100
    _cost: str = UNKNOWN
    _rate_limits: dict = {}
    _capabilities: tuple = ("search", "metadata")
    _reliability: str = UNKNOWN

    def available(self) -> bool:
        return False                      # contrato: aún sin integración real

    def supported_media(self) -> tuple:
        return self._media

    def supported_licenses(self) -> tuple:
        return self._licenses

    def priority(self) -> int:
        return self._priority

    def cost(self) -> str:
        return self._cost

    def rate_limits(self) -> dict:
        return dict(self._rate_limits)

    def capabilities(self) -> tuple:
        return self._capabilities

    def reliability(self) -> str:
        return self._reliability

    def discover(self, query: DiscoveryQuery) -> list[DiscoveredEvidence]:
        return []                         # contrato: aún no descubre (sin red)

    def capability(self) -> SourceCapability:
        return SourceCapability(
            name=self.name, available=self.available(), media=list(self._media),
            licenses=list(self._licenses), priority=self._priority, cost=self._cost,
            rate_limits=dict(self._rate_limits), reliability=self._reliability,
            capabilities=list(self._capabilities),
        )
