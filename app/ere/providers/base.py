"""Interfaz de proveedor de evidencia (ERE).

Un ``EvidenceProvider`` recibe un ``ProjectQuery`` y devuelve un ``EvidenceResult``
con nodos parciales del grafo (entidades, eventos, artículos, imágenes, vídeos,
documentos judiciales, relaciones) y sus fuentes. El orquestador fusiona varios
resultados en un único ``EvidenceGraph``. Añadir un proveedor NO requiere tocar el
resto del sistema: basta implementar esta interfaz y registrarlo.

Contrato de robustez: un proveedor nunca debe romper el pipeline. Si una fuente no
existe o falla, devuelve ``available=False`` con ``error`` (el orquestador, además,
captura cualquier excepción como red de seguridad).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.ere.models import (
    Article,
    CourtDocument,
    Entity,
    Event,
    ImageAsset,
    ProjectQuery,
    Relationship,
    SourceRef,
    VideoAsset,
)


@dataclass
class EvidenceResult:
    provider: str
    available: bool
    entities: list[Entity] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    articles: list[Article] = field(default_factory=list)
    images: list[ImageAsset] = field(default_factory=list)
    videos: list[VideoAsset] = field(default_factory=list)
    court_documents: list[CourtDocument] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    sources: list[SourceRef] = field(default_factory=list)
    confidence: float = 0.5
    error: str = ""
    notes: str = ""


class EvidenceProvider(ABC):
    name: str = "base"

    @abstractmethod
    def research(self, query: ProjectQuery) -> EvidenceResult:
        """Investiga el caso y devuelve evidencia parcial (o available=False)."""
        ...
