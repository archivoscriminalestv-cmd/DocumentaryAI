"""ArchiveFetcher — stub de recuperación (Sprint C-03).

Atiende ``SearchType.ARCHIVES`` y ``SearchType.GOVERNMENT`` pero todavía no
busca; devuelve ``[]``. Sin red, sin IA.
"""

from app.domain.search import SearchTask, SearchType
from app.domain.source.retrieved_source import RetrievedSource


class ArchiveFetcher:
    def handles(self, search_type: SearchType) -> bool:
        return search_type in (SearchType.ARCHIVES, SearchType.GOVERNMENT)

    def fetch(self, task: SearchTask) -> list[RetrievedSource]:
        return []
