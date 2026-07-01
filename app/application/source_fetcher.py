"""SourceFetcher — puerto de un recuperador de fuentes (Sprint C-03).

Cada implementación declara qué ``SearchType`` atiende y sabe convertir una
``SearchTask`` en ``RetrievedSource``. Las implementaciones concretas viven en
``app/infrastructure/retrieval/`` (Wikipedia real; el resto stubs por ahora).
Contrato de degradación: ``fetch`` NUNCA debe lanzar; ante cualquier fallo
devuelve ``[]``.
"""

from typing import Protocol

from app.domain.search import SearchTask, SearchType
from app.domain.source.retrieved_source import RetrievedSource


class SourceFetcher(Protocol):
    def handles(self, search_type: SearchType) -> bool: ...
    def fetch(self, task: SearchTask) -> list[RetrievedSource]: ...
