"""DirectedScene — escena anotada por el director (Sprint C-08).

Objeto de dominio puro y aditivo. Es una ``Scene`` con decisiones de dirección
(pacing/emphasis/tone). NO añade ni cambia hechos: ``fact_ids`` pasa intacto, y
``title``/``narration`` conservan su significado. Es serializable a JSON
directamente (``tone`` es una cadena de un conjunto cerrado).
"""

from dataclasses import dataclass, field


@dataclass
class DirectedScene:
    id: str
    title: str
    narration: str
    fact_ids: list[str] = field(default_factory=list)
    duration_hint: float = 0.0
    emphasis: float = 0.0
    tone: str = "neutral"
