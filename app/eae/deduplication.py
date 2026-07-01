"""Arquitectura de DEDUPLICACIÓN del EAE (EAE-001) — solo contratos.

Define las estrategias de deduplicación (hash perceptual, hash exacto, hash de metadatos,
identidad de fuente). NO implementa nada todavía: el deduplicador base devuelve UNKNOWN.
"""

from app.eae import NOT_IMPLEMENTED, UNKNOWN
from app.eae.models import Evidence


class DeduplicationStrategy:
    PERCEPTUAL_HASH = "perceptual_hash"
    EXACT_HASH = "exact_hash"
    METADATA_HASH = "metadata_hash"
    SOURCE_IDENTITY = "source_identity"
    ALL = (PERCEPTUAL_HASH, EXACT_HASH, METADATA_HASH, SOURCE_IDENTITY)


class BaseEvidenceDeduplicator:
    """Implementa ``EvidenceDeduplicator`` como contrato. No deduplica todavía."""

    name = "base"
    strategies = DeduplicationStrategy.ALL

    def is_duplicate(self, evidence: Evidence, existing: list[Evidence]) -> str:
        return UNKNOWN  # contrato: aún no se compara (nunca inventa)

    def find_duplicates(self, evidence: list[Evidence]) -> list[tuple[str, str]]:
        return []       # contrato: sin cálculo todavía

    def method(self) -> str:
        return NOT_IMPLEMENTED
