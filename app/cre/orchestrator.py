"""ResearchOrchestrator — coordina proveedores y produce la CharacterBible (CRE).

Pipeline:  CharacterRequest → [N ResearchProviders] → Normalizer → CharacterBible.
Devuelve también un ``manifest`` que registra qué proveedores se consultaron, su
disponibilidad, confianza, aportación, errores y tiempos. Añadir proveedores es solo
pasarlos en la lista; el orquestador no conoce ninguno en concreto.

Dos catálogos:
- ``default_providers()``: offline y determinista (stubs + mock); usado por los tests.
- ``real_providers(client)``: fuentes reales (Wikipedia, Wikidata, Commons) + stubs
  preparados (News, Archive) + mock como red de seguridad; usado por la CLI.
"""

import time

from app.cre import SCHEMA_VERSION
from app.cre.models import CharacterBible, CharacterRequest, slugify
from app.cre.normalizer import ResearchNormalizer
from app.cre.providers.base import ResearchProvider

CRE_VERSION = "CRE-002"


def default_providers() -> list[ResearchProvider]:
    """Conjunto offline/determinista: stubs externos (no disponibles) + Mock."""
    from app.cre.providers.external import (
        ArchiveProvider,
        FutureImageReferenceProvider,
        NewsProvider,
        WikipediaProvider,
    )
    from app.cre.providers.mock import MockResearchProvider

    return [
        WikipediaProvider(),
        NewsProvider(),
        ArchiveProvider(),
        FutureImageReferenceProvider(),
        MockResearchProvider(),
    ]


def real_providers(client=None, lang: str = "en") -> list[ResearchProvider]:
    """Catálogo de producción: fuentes reales + stubs preparados + mock de respaldo.

    ``client`` es un ``HttpClient`` inyectable (en tests se pasa un cliente falso;
    en producción se usa el ``JsonHttpClient`` por defecto de cada proveedor).
    """
    from app.cre.providers.commons import CommonsProvider
    from app.cre.providers.external import ArchiveProvider, NewsProvider
    from app.cre.providers.mock import MockResearchProvider
    from app.cre.providers.wikidata import WikidataProvider
    from app.cre.providers.wikipedia import WikipediaProvider as RealWikipediaProvider

    return [
        RealWikipediaProvider(client=client, lang=lang),
        WikidataProvider(client=client, lang=lang),
        CommonsProvider(client=client, lang=lang),
        NewsProvider(),
        ArchiveProvider(),
        MockResearchProvider(),
    ]


class ResearchOrchestrator:
    def __init__(
        self,
        providers: list[ResearchProvider],
        normalizer: ResearchNormalizer | None = None,
    ) -> None:
        self._providers = providers
        self._normalizer = normalizer or ResearchNormalizer()

    def research(self, request: CharacterRequest) -> tuple[CharacterBible, dict]:
        results = []
        timings: dict[str, float] = {}
        for provider in self._providers:
            start = time.perf_counter()
            result = provider.research(request)
            timings[result.provider] = round((time.perf_counter() - start) * 1000.0, 1)
            results.append(result)

        bible = self._normalizer.normalize(request, results)

        manifest = {
            "schema_version": SCHEMA_VERSION,
            "versions": {"schema": SCHEMA_VERSION, "cre": CRE_VERSION},
            "character_id": bible.identity.id or slugify(request.name),
            "request": {"name": request.name, "aliases": list(request.aliases)},
            "providers": [
                {
                    "provider": r.provider,
                    "available": r.available,
                    "confidence": r.confidence,
                    "sections": sorted((r.data or {}).keys()),
                    "visual_references": len(r.visual_references),
                    "sources": len(r.sources),
                    "elapsed_ms": timings.get(r.provider, 0.0),
                    "error": r.error,
                    "notes": r.notes,
                }
                for r in results
            ],
            "totals": {
                "providers_consulted": len(results),
                "providers_available": sum(1 for r in results if r.available),
                "visual_references": len(bible.visual_references),
                "conflicts": len(bible.conflicts),
            },
        }
        return bible, manifest
