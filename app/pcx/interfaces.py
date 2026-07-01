"""Contrato público del Production Context (PCX).

Los motores de generación dependen ÚNICAMENTE de este contrato (no de la clase concreta ni
del origen del conocimiento). Permite sustituir/extender el contexto sin tocar los motores.
"""

from typing import Any, Protocol


class ProductionContextLike(Protocol):
    """Lo único que un motor de generación necesita saber del contexto."""

    genre: str

    def has(self, section: str, key: str, *, min_confidence: float = 0.0) -> bool:
        ...

    def get(self, section: str, key: str, *, min_confidence: float = 0.0, default: Any = None) -> Any:
        ...
