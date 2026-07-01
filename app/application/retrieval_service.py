"""RetrievalService — orquesta fetchers: SearchTask[] -> RetrievedSource[] (C-03).

Aplicación pura: enruta cada ``SearchTask`` al/los fetcher(s) que atienden su
``type``, recolecta resultados, deduplica por (url o título) y asigna ids
deterministas. No usa IA. No accede a la red directamente (eso vive en los
fetchers). Es determinista dada la salida de los fetchers.

Degradación: si un fetcher falla, su contribución es ``[]`` y el resto continúa
(defensa adicional al try/except interno de cada fetcher).
"""

from app.application.source_fetcher import SourceFetcher
from app.domain.search import SearchTask
from app.domain.source.retrieved_source import RetrievedSource


class RetrievalService:
    def __init__(self, fetchers: list[SourceFetcher]) -> None:
        self._fetchers = list(fetchers)

    def retrieve(self, tasks: list[SearchTask]) -> list[RetrievedSource]:
        collected: list[RetrievedSource] = []
        for task in tasks:
            for fetcher in self._fetchers:
                try:
                    if not fetcher.handles(task.type):
                        continue
                    results = fetcher.fetch(task) or []
                except Exception:
                    results = []  # ningún fetcher puede tumbar la recuperación
                collected.extend(results)
        return self._dedupe(collected)

    def _dedupe(self, sources: list[RetrievedSource]) -> list[RetrievedSource]:
        # Duplicado si coincide la url O el título (normalizados). Sin url ni
        # título no hay identidad -> se descarta.
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()
        unique: list[RetrievedSource] = []
        for source in sources:
            url = (source.url or "").strip().lower()
            title = (source.title or "").strip().lower()
            if not url and not title:
                continue
            if (url and url in seen_urls) or (title and title in seen_titles):
                continue
            if url:
                seen_urls.add(url)
            if title:
                seen_titles.add(title)
            unique.append(source)
        for index, source in enumerate(unique, start=1):
            source.id = f"src-{index:02d}"
        return unique
