"""EvidenceOrchestrator — coordina proveedores y produce el EvidenceGraph (ERE).

Pipeline:  ProjectQuery → [N EvidenceProviders] → GraphBuilder → EvidenceGraph.

Robustez: NUNCA rompe el pipeline. Cada proveedor se ejecuta dentro de un
``try/except`` (red de seguridad además del contrato del propio proveedor); si una
fuente falla o no existe, se registra el error en el manifest y se continúa.

Catálogos:
- ``default_providers()``: offline/determinista (prepared stubs + mock); tests.
- ``real_providers(client, lang, seed)``: fuentes reales (Wikipedia/Wikidata/
  Commons) + prepared stubs + seed opcional + mock; usado por la CLI.
"""

import time

from app.ere import ERE_VERSION, SCHEMA_VERSION
from app.ere.graph_builder import GraphBuilder
from app.ere.models import EvidenceGraph, ProjectQuery
from app.ere.providers.base import EvidenceProvider, EvidenceResult


def default_providers() -> list[EvidenceProvider]:
    from app.ere.providers.mock import MockEvidenceProvider
    from app.ere.providers.prepared import (
        ArchiveProvider,
        CourtDocumentsProvider,
        GoogleImagesProvider,
        NewsProvider,
        YoutubeProvider,
    )

    return [
        NewsProvider(),
        YoutubeProvider(),
        GoogleImagesProvider(),
        ArchiveProvider(),
        CourtDocumentsProvider(),
        MockEvidenceProvider(),
    ]


def real_providers(client=None, lang: str = "en", seed=None) -> list[EvidenceProvider]:
    """Catálogo de producción. ``client``/``seed`` inyectables (tests).

    ``seed`` puede ser una ruta a JSON, un dict, o un ``SeedEvidenceProvider`` ya
    construido; aporta evidencia pública curada por el Director (sin scraping).
    """
    from app.ere.providers.acquisition import (
        ArchiveOrgProvider,
        DoajProvider,
        EuropeanaProvider,
        GoogleBooksProvider,
        HemerotecaProvider,
        LibraryProvider,
        OpenAlexProvider,
        OpenverseProvider,
        RssProvider,
    )
    from app.ere.providers.commons import CommonsProvider
    from app.ere.providers.mock import MockEvidenceProvider
    from app.ere.providers.prepared import (
        ArchiveProvider,
        CourtDocumentsProvider,
        GoogleImagesProvider,
        NewsProvider,
        YoutubeProvider,
    )
    from app.ere.providers.seed import SeedEvidenceProvider
    from app.ere.providers.wikidata import WikidataProvider
    from app.ere.providers.wikipedia import WikipediaProvider

    providers: list[EvidenceProvider] = [
        WikipediaProvider(client=client, lang=lang),
        WikidataProvider(client=client, lang=lang),
        CommonsProvider(client=client, lang=lang),
        NewsProvider(client=client),
        YoutubeProvider(client=client),
        GoogleImagesProvider(client=client),
        ArchiveProvider(client=client),
        CourtDocumentsProvider(client=client),
        # ERE-003: adquisición multi-fuente (preparados)
        OpenverseProvider(client=client),
        EuropeanaProvider(client=client),
        ArchiveOrgProvider(client=client),
        RssProvider(client=client),
        LibraryProvider(client=client),
        HemerotecaProvider(client=client),
        GoogleBooksProvider(client=client),
        DoajProvider(client=client),
        OpenAlexProvider(client=client),
    ]
    if seed is not None:
        if isinstance(seed, SeedEvidenceProvider):
            providers.append(seed)
        elif isinstance(seed, dict):
            providers.append(SeedEvidenceProvider(data=seed))
        else:
            providers.append(SeedEvidenceProvider(path=str(seed)))
    providers.append(MockEvidenceProvider())
    return providers


class EvidenceOrchestrator:
    def __init__(
        self,
        providers: list[EvidenceProvider],
        builder: GraphBuilder | None = None,
    ) -> None:
        self._providers = providers
        self._builder = builder or GraphBuilder()

    def _run_providers(
        self, query: ProjectQuery
    ) -> tuple[list[EvidenceResult], dict[str, float]]:
        results: list[EvidenceResult] = []
        timings: dict[str, float] = {}
        for provider in self._providers:
            name = getattr(provider, "name", provider.__class__.__name__)
            start = time.perf_counter()
            try:
                result = provider.research(query)
            except Exception as exc:  # red de seguridad: nunca rompe el pipeline
                result = EvidenceResult(name, False, error=f"excepción: {exc}"[:160])
            timings[name] = round((time.perf_counter() - start) * 1000.0, 1)
            results.append(result)
        return results, timings

    def research(self, query: ProjectQuery) -> tuple[EvidenceGraph, dict]:
        results, timings = self._run_providers(query)
        graph = self._builder.build(query, results)
        manifest = self._manifest(query, graph, results, timings)
        return graph, manifest

    def research_project(
        self,
        knowledge,
        *,
        query_builder=None,
        ranking=None,
        resolver=None,
        min_score: float = 0.15,
    ) -> tuple[EvidenceGraph, dict]:
        """Entrada ERE-002: ProjectKnowledge → Query Builder → Providers → Ranking →
        Entity Resolution → EvidenceGraph. No cambia la estructura del grafo."""
        from app.ere.entity_resolution import EntityResolver
        from app.ere.query_builder import QueryBuilder
        from app.ere.ranking import RankingEngine

        qb = query_builder or QueryBuilder()
        ranker = ranking or RankingEngine()
        resolver = resolver or EntityResolver()

        queries = qb.build(knowledge)
        base_query = knowledge.to_query()
        results, timings = self._run_providers(base_query)

        ranked_results: list[EvidenceResult] = []
        ranked_nodes = []
        for result in results:
            new_result, nodes = ranker.rank_result(result, knowledge, min_score)
            ranked_results.append(new_result)
            ranked_nodes.extend(nodes)

        graph = self._builder.build(base_query, ranked_results)
        graph = resolver.resolve(graph, knowledge)

        manifest = self._manifest(base_query, graph, ranked_results, timings)
        manifest["project_knowledge"] = knowledge.to_dict()
        manifest["query_builder"] = {
            "total": len(queries),
            "queries": [q.to_dict() for q in queries],
        }
        accepted = [n for n in ranked_nodes if n.accepted]
        rejected = [n for n in ranked_nodes if not n.accepted]
        manifest["ranking"] = {
            "min_score": min_score,
            "scored": len(ranked_nodes),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "rejected_nodes": sorted(
                ({"id": n.node_id, "kind": n.kind, "score": n.score} for n in rejected),
                key=lambda d: d["id"],
            ),
        }
        manifest["entity_resolution"] = {"entities_after": len(graph.entities)}
        return graph, manifest

    @staticmethod
    def _manifest(query, graph, results, timings) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "versions": {"schema": SCHEMA_VERSION, "ere": ERE_VERSION},
            "project": {"name": query.name, "location": query.location, "date": query.date},
            "subject_id": query.subject_id(),
            "providers": [
                {
                    "provider": r.provider,
                    "available": r.available,
                    "confidence": r.confidence,
                    "entities": len(r.entities),
                    "articles": len(r.articles),
                    "images": len(r.images),
                    "videos": len(r.videos),
                    "court_documents": len(r.court_documents),
                    "relationships": len(r.relationships),
                    "sources": len(r.sources),
                    "elapsed_ms": timings.get(r.provider, 0.0),
                    "error": r.error,
                    "notes": r.notes,
                }
                for r in results
            ],
            "statistics": {
                "providers_consulted": len(results),
                "providers_available": sum(1 for r in results if r.available),
                "entities": len(graph.entities),
                "events": len(graph.events),
                "articles": len(graph.articles),
                "images": len(graph.images),
                "videos": len(graph.videos),
                "court_documents": len(graph.court_documents),
                "relationships": len(graph.relationships),
                "conflicts": len(graph.conflicts),
                "sources": len(graph.sources),
            },
            "coverage": _coverage(graph),
        }


def _coverage(graph: EvidenceGraph) -> dict:
    buckets = {
        "entities": graph.entities,
        "events": graph.events,
        "articles": graph.articles,
        "images": graph.images,
        "videos": graph.videos,
        "court_documents": graph.court_documents,
        "relationships": graph.relationships,
    }
    present = sum(1 for v in buckets.values() if v)
    return {
        "buckets_with_data": present,
        "buckets_total": len(buckets),
        "ratio": round(present / len(buckets), 3),
    }
