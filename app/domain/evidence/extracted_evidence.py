"""ExtractedEvidence — evidencia derivada de una RetrievedSource (Sprint C-04).

Objeto de dominio puro y DISTINTO del ``Evidence`` existente (pipeline:
id/research_id/source_id/content). Aquí modelamos una afirmación (``claim``)
extraída del texto de una fuente recuperada, con su contexto y una confianza
heurística. Es aditivo: no toca ``evidence.py`` ni el pipeline existente.

Procedencia: ``source_id`` enlaza con ``RetrievedSource.id`` (que a su vez lleva
a la SearchTask/Plan/Topic), preservando la cadena completa.
``confidence`` es ``float`` -> serializable a JSON directamente.
"""

from dataclasses import dataclass


@dataclass
class ExtractedEvidence:
    id: str
    source_id: str
    claim: str
    context: str
    confidence: float
