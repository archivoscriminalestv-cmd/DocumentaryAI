"""YouTubeFetcher — stub de recuperación (Sprint C-03).

Preparado para el futuro: atiende ``SearchType.YOUTUBE`` pero todavía no busca;
devuelve ``[]`` (degradación elegante por diseño). No accede a la red ni usa IA.
"""

from app.domain.search import SearchTask, SearchType
from app.domain.source.retrieved_source import RetrievedSource


class YouTubeFetcher:
    def handles(self, search_type: SearchType) -> bool:
        return search_type == SearchType.YOUTUBE

    def fetch(self, task: SearchTask) -> list[RetrievedSource]:
        return []
