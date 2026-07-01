"""Proveedores externos de investigación (stubs preparados) — CRE.

Interfaces listas para integrar fuentes reales (sin scraping en este sprint). Cada
uno devuelve ``available=False`` hasta que se implemente su integración; el
orquestador los omite. Sustituir el cuerpo de ``research`` por la llamada real NO
requiere tocar el orquestador, el normalizer ni el resto del sistema.
"""

from app.cre.models import CharacterRequest
from app.cre.providers.base import ResearchProvider, ResearchResult


class _UnavailableProvider(ResearchProvider):
    name = "unavailable"

    def research(self, request: CharacterRequest) -> ResearchResult:
        return ResearchResult(
            provider=self.name,
            available=False,
            notes="Integración no implementada en este sprint (interfaz preparada).",
        )


class WikipediaProvider(_UnavailableProvider):
    name = "wikipedia"


class NewsProvider(_UnavailableProvider):
    name = "news"


class ArchiveProvider(_UnavailableProvider):
    name = "archive"


class FutureImageReferenceProvider(_UnavailableProvider):
    """Reservado: poblará ``visual_references`` (sin descargar imágenes todavía)."""

    name = "future-image-reference"
