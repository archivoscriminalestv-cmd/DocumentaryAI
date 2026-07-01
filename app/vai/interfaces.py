"""Interfaces (puertos) de VAI — contratos entre director y especialistas.

Cada motor especialista implementa ``VisualEngine``: dado un Shot (duck-typed) y
un ``VisualContext``, aporta descriptores de su categoría. El director compone la
``VisualSpecification`` con las aportaciones de todos. Añadir o sustituir un motor
NO obliga a tocar los demás (desacoplamiento total).
"""

from typing import Protocol

from app.vai.models import VisualContext, VisualSpecification


class VisualEngine(Protocol):
    """Motor especialista de una dimensión fotográfica."""

    category: str

    def contribute(self, shot, context: VisualContext) -> list[str]:
        """Descriptores deterministas de esta categoría para el plano."""
        ...


class PromptOptimizer(Protocol):
    def optimize(self, spec: VisualSpecification, context: VisualContext) -> str: ...


class NegativePromptEngine(Protocol):
    def contribute(self, shot, context: VisualContext) -> list[str]: ...


class VisualMemory(Protocol):
    def record(self, shot_id: str, spec: VisualSpecification) -> None: ...
    def get(self, shot_id: str) -> VisualSpecification | None: ...
