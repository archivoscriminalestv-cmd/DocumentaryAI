"""SearchTask — qué buscar, decidido a partir del ResearchPlan (Sprint C-02).

Objetos de dominio puros. El Research Executor produce una lista determinista de
``SearchTask`` que describen QUÉ búsquedas deberían ejecutarse más adelante.
Aquí NO se busca ni se accede a la red: solo se planifican las tareas.

``SearchType``/``SearchPriority`` son ``StrEnum`` para que las tareas sean
serializables a JSON directamente (``json.dumps`` las emite como su cadena).
"""

from dataclasses import dataclass
from enum import StrEnum


class SearchType(StrEnum):
    WIKIPEDIA = "wikipedia"
    ACADEMIC = "academic"
    BOOKS = "books"
    NEWS = "news"
    GOVERNMENT = "government"
    YOUTUBE = "youtube"
    ARCHIVES = "archives"
    SCIENTIFIC_PAPERS = "scientific_papers"


class SearchPriority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SearchTask:
    id: str
    type: SearchType
    query: str
    priority: SearchPriority
    reason: str
