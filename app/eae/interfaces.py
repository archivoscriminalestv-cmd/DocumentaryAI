"""Interfaces públicas (Protocols) del EAE. Sin implementación.

Definen los contratos de adquisición, verificación, organización y resolución de
evidencias. El orquestador solo conoce estas interfaces.
"""

from dataclasses import dataclass, field
from typing import Protocol

from app.eae.models import (
    Evidence,
    EvidenceCollection,
    EvidenceReference,
    EvidenceVerification,
)


@dataclass
class EvidenceQuery:
    """Petición de adquisición: el caso y los criterios de búsqueda."""

    case_id: str
    subject: str = ""
    terms: list[str] = field(default_factory=list)
    kinds: list[str] = field(default_factory=list)   # filtra por EvidenceKind
    since: str = ""
    until: str = ""
    language: str = ""
    limit: int = 0


class EvidenceProvider(Protocol):
    """Una fuente de evidencias (YouTube, Wikimedia, Internet Archive, prensa, gobierno…)."""

    name: str

    def available(self) -> bool:
        ...

    def search(self, query: EvidenceQuery) -> list[EvidenceReference]:
        ...

    def fetch(self, reference: EvidenceReference) -> Evidence:
        ...


class EvidenceSearcher(Protocol):
    def search(self, query: EvidenceQuery) -> list[EvidenceReference]:
        ...


class EvidenceCollector(Protocol):
    def collect(self, query: EvidenceQuery) -> EvidenceCollection:
        ...


class EvidenceVerifier(Protocol):
    def verify(self, evidence: Evidence) -> EvidenceVerification:
        ...


class EvidenceDeduplicator(Protocol):
    def is_duplicate(self, evidence: Evidence, existing: list[Evidence]) -> str:
        """Devuelve 'yes' | 'no' | UNKNOWN (nunca inventa)."""
        ...

    def find_duplicates(self, evidence: list[Evidence]) -> list[tuple[str, str]]:
        ...


class EvidenceRanker(Protocol):
    def rank(self, evidence: list[Evidence]) -> list[Evidence]:
        ...


class EvidenceResolver(Protocol):
    def resolve(self, references: list[EvidenceReference]) -> list[EvidenceReference]:
        ...


class EvidenceStorage(Protocol):
    def layout(self) -> dict:
        ...

    def store(self, evidence: Evidence) -> str:
        """Organiza la evidencia y devuelve su ruta planificada (sin binarios todavía)."""
        ...
