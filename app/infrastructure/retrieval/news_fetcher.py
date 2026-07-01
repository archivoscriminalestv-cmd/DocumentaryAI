"""NewsFetcher — stub de recuperación (Sprint C-03).

Atiende ``SearchType.NEWS`` pero todavía no busca; devuelve ``[]``. Sin red, sin IA.
"""

from app.domain.search import SearchTask, SearchType
from app.domain.source.retrieved_source import RetrievedSource


class NewsFetcher:
    def handles(self, search_type: SearchType) -> bool:
        return search_type == SearchType.NEWS

    def fetch(self, task: SearchTask) -> list[RetrievedSource]:
        return []
