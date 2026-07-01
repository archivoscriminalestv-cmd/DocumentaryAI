"""AcademicFetcher — stub de recuperación (Sprint C-03).

Atiende ``SearchType.ACADEMIC`` y ``SearchType.SCIENTIFIC_PAPERS`` pero todavía
no busca; devuelve ``[]``. Sin red, sin IA.
"""

from app.domain.search import SearchTask, SearchType
from app.domain.source.retrieved_source import RetrievedSource


class AcademicFetcher:
    def handles(self, search_type: SearchType) -> bool:
        return search_type in (SearchType.ACADEMIC, SearchType.SCIENTIFIC_PAPERS)

    def fetch(self, task: SearchTask) -> list[RetrievedSource]:
        return []
