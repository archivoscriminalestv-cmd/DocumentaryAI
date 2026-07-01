"""Evidence Acquisition Engine (EAE) — Sprint EAE-001 (foundation).

Motor permanente para LOCALIZAR, ADQUIRIR, ORGANIZAR y VERIFICAR evidencias reales de un
caso documental. El EAE no busca imágenes: busca **evidencias** (foto, vídeo, documento,
noticia, mapa, rueda de prensa, entrevista, PDF, archivo judicial, publicación oficial,
cronología, comunicado, audio, red social pública). Toda evidencia rastrea SIEMPRE su
origen (cadena de custodia).

Este sprint es SOLO arquitectura: modelos, interfaces (Protocols) y contratos. NO descarga
contenido, NO hace peticiones reales, NO scraping, NO IA/LLM. Separa por completo
adquisición / verificación / organización / narrativa / generación. Escribe solo en
``output/eae/`` (nunca en ``knowledge/``).
"""

SCHEMA_VERSION = "0.1"
UNKNOWN = "UNKNOWN"
NOT_IMPLEMENTED = "not_implemented"

from app.eae.interfaces import (
    EvidenceCollector,
    EvidenceDeduplicator,
    EvidenceProvider,
    EvidenceQuery,
    EvidenceRanker,
    EvidenceResolver,
    EvidenceSearcher,
    EvidenceStorage,
    EvidenceVerifier,
)
from app.eae.models import (
    Evidence,
    EvidenceCase,
    EvidenceCollection,
    EvidenceEvent,
    EvidenceHash,
    EvidenceKind,
    EvidenceLicense,
    EvidenceLocation,
    EvidenceMetadata,
    EvidencePerson,
    EvidenceReference,
    EvidenceSource,
    EvidenceTimeline,
    EvidenceVerification,
    VerificationStatus,
)
from app.eae.orchestrator import EvidenceAcquisitionEngine

__all__ = [
    "SCHEMA_VERSION",
    "UNKNOWN",
    "NOT_IMPLEMENTED",
    "EvidenceAcquisitionEngine",
    # interfaces
    "EvidenceProvider", "EvidenceVerifier", "EvidenceCollector", "EvidenceStorage",
    "EvidenceDeduplicator", "EvidenceRanker", "EvidenceResolver", "EvidenceSearcher",
    "EvidenceQuery",
    # models
    "Evidence", "EvidenceSource", "EvidenceCollection", "EvidenceReference",
    "EvidenceMetadata", "EvidenceLicense", "EvidenceHash", "EvidenceVerification",
    "EvidenceTimeline", "EvidencePerson", "EvidenceLocation", "EvidenceEvent",
    "EvidenceCase", "EvidenceKind", "VerificationStatus",
]
