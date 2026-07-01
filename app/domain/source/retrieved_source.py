"""RetrievedSource — una fuente DESCUBIERTA por el motor de recuperación (C-03).

Objeto de dominio puro y distinto de ``Source`` (que representa material ya
registrado dentro de una Research con ``research_id``/``content``). Aquí modelamos
el resultado de una búsqueda: de dónde viene (``type``), su título, URL y un
extracto. Es aditivo: no toca ``source.py`` ni el pipeline existente.

``type`` es ``SearchType`` (StrEnum) -> el objeto es serializable a JSON
directamente con ``dataclasses.asdict`` + ``json.dumps``.
"""

from dataclasses import dataclass

from app.domain.search import SearchType


@dataclass
class RetrievedSource:
    id: str
    type: SearchType
    title: str
    url: str
    snippet: str = ""
    query: str = ""  # procedencia: la query que produjo esta fuente
