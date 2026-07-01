"""Interfaz abstracta de proveedor de investigación (CRE).

Un proveedor recibe un ``CharacterRequest`` y devuelve un ``ResearchResult`` con
datos PARCIALES con forma de Character Bible (secciones), referencias visuales y
fuentes. El orquestador fusiona varios resultados. Añadir un proveedor NO requiere
modificar el resto del sistema: basta implementar esta interfaz y registrarlo.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.cre.models import CharacterRequest, VisualReference


@dataclass
class ResearchResult:
    provider: str
    available: bool
    data: dict[str, Any] = field(default_factory=dict)  # secciones parciales de la bible
    visual_references: list[VisualReference] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    notes: str = ""
    confidence: float = 0.5  # confianza del proveedor (trazabilidad/normalización)
    error: str = ""          # mensaje si el proveedor falló (queda en el manifest)


class ResearchProvider(ABC):
    name: str = "base"

    @abstractmethod
    def research(self, request: CharacterRequest) -> ResearchResult:
        """Investiga el personaje y devuelve datos parciales (o available=False)."""
        ...
