"""StaticCatalogProvider (EAE-003) — proveedor de descubrimiento por catálogo inyectado.

Permite descubrir evidencias de forma DETERMINISTA y SIN RED a partir de un catálogo
explícito (tests y demos), y sirve de plantilla para un proveedor real (que solo cambiaría
``discover`` por una llamada a una API oficial). No descarga binarios.

Catálogo: lista de entradas ``{"category", "target"?, "count"?, "license"?, "url"?,
"reliability"?, "media_type"?, "fmt"?}``. ``discover`` genera punteros para las entradas
cuya categoría (y target, si se indica) coincidan con la consulta.
"""

from app.eae import UNKNOWN
from app.eae.discovery.models import Availability, DiscoveredEvidence
from app.eae.discovery.providers.base import BaseDiscoveryProvider, DiscoveryQuery


class StaticCatalogProvider(BaseDiscoveryProvider):
    def __init__(self, name: str, *, media: tuple, catalog: list[dict],
                 licenses: tuple = ("UNKNOWN",), priority: int = 10,
                 cost: str = "free", reliability: str = "HIGH") -> None:
        self.name = name
        self._media = tuple(media)
        self._licenses = tuple(licenses)
        self._priority = priority
        self._cost = cost
        self._reliability = reliability
        self._capabilities = ("search", "metadata")
        self._catalog = list(catalog)

    def available(self) -> bool:
        return True

    def discover(self, query: DiscoveryQuery) -> list[DiscoveredEvidence]:
        out: list[DiscoveredEvidence] = []
        for idx, entry in enumerate(self._catalog):
            if entry.get("category") != query.category:
                continue
            if "target" in entry and entry["target"] != query.target:
                continue
            count = int(entry.get("count", 1))
            for i in range(count):
                eid = f"{self.name}:{query.need_id or query.category}:{idx}:{i}"
                out.append(DiscoveredEvidence(
                    id=eid, need_id=query.need_id, target=query.target,
                    category=query.category, title=entry.get("title", ""),
                    url=entry.get("url", ""), provider=self.name,
                    media_type=entry.get("media_type", query.category),
                    license=entry.get("license", self._licenses[0] if self._licenses else UNKNOWN),
                    fmt=entry.get("fmt", UNKNOWN),
                    reliability=self._reliability,
                    availability=entry.get("availability", Availability.AVAILABLE),
                    priority=query.priority,
                ))
        return out
