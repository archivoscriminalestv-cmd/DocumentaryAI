"""Modelos del Evidence Acquisition Engine (EAE).

Tipados, versionados, serializables y deterministas (sin marcas de tiempo). El núcleo es
``Evidence`` (una unidad de evidencia con su ORIGEN siempre presente) y ``EvidenceCase``
(el contenedor del caso documental). Todos los valores desconocidos son ``UNKNOWN``.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.eae import SCHEMA_VERSION, UNKNOWN


class EvidenceKind:
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    NEWS = "news"
    MAP = "map"
    PRESS_CONFERENCE = "press_conference"
    INTERVIEW = "interview"
    PDF = "pdf"
    COURT_RECORD = "court_record"
    OFFICIAL_PUBLICATION = "official_publication"
    TIMELINE = "timeline"
    STATEMENT = "statement"
    AUDIO = "audio"
    SOCIAL_POST = "social_post"
    UNKNOWN = UNKNOWN
    ALL = (PHOTO, VIDEO, DOCUMENT, NEWS, MAP, PRESS_CONFERENCE, INTERVIEW, PDF,
           COURT_RECORD, OFFICIAL_PUBLICATION, TIMELINE, STATEMENT, AUDIO, SOCIAL_POST, UNKNOWN)


class VerificationStatus:
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    FAILED = "FAILED"
    UNKNOWN = UNKNOWN


class ConfidenceLevel:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = UNKNOWN


@dataclass
class EvidenceLicense:
    name: str = UNKNOWN
    url: str = ""
    redistributable: str = UNKNOWN       # yes | no | UNKNOWN
    attribution_required: str = UNKNOWN
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceHash:
    sha256: str = ""
    phash: str = ""
    ahash: str = ""
    metadata_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceSource:
    """Origen de una evidencia (raíz de la cadena de custodia). SIEMPRE presente."""

    provider: str = ""                   # youtube | wikimedia | internet_archive | ...
    url: str = ""
    source_id: str = ""
    publisher: str = ""
    accessed_via: str = ""               # cómo se accedió (api/archivo/…)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceReference:
    """Puntero a una evidencia + su origen (resultado de una búsqueda, antes de adquirir)."""

    evidence_id: str = ""
    kind: str = UNKNOWN
    source: EvidenceSource = field(default_factory=EvidenceSource)
    title: str = ""
    role: str = ""                       # p.ej. "primary" | "supporting"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceMetadata:
    title: str = ""
    description: str = ""
    author: str = ""
    date: str = ""                       # fecha del HECHO/publicación (no de descarga)
    language: str = UNKNOWN
    mime_type: str = ""
    width: int = 0
    height: int = 0
    duration: float = 0.0
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceVerification:
    status: str = VerificationStatus.UNVERIFIED
    confidence: str = ConfidenceLevel.UNKNOWN
    source_verified: str = UNKNOWN       # yes | no | UNKNOWN
    hash_verified: str = UNKNOWN
    chain_of_custody: list[str] = field(default_factory=list)   # pasos auditables
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidencePerson:
    id: str
    name: str = ""
    aliases: list[str] = field(default_factory=list)
    role: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceLocation:
    id: str
    name: str = ""
    latitude: float | None = None
    longitude: float | None = None
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceEvent:
    id: str
    description: str = ""
    date: str = ""
    location_id: str = ""
    person_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceTimeline:
    events: list[EvidenceEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"events": [e.to_dict() for e in self.events]}


@dataclass
class Evidence:
    """Unidad de evidencia. El binario NO se almacena aquí (solo ``local_path`` futuro)."""

    id: str
    kind: str = UNKNOWN
    schema_version: str = SCHEMA_VERSION
    metadata: EvidenceMetadata = field(default_factory=EvidenceMetadata)
    source: EvidenceSource = field(default_factory=EvidenceSource)
    license: EvidenceLicense = field(default_factory=EvidenceLicense)
    hashes: EvidenceHash = field(default_factory=EvidenceHash)
    verification: EvidenceVerification = field(default_factory=EvidenceVerification)
    local_path: str = ""                 # ruta en la biblioteca (cuando se adquiera)
    references: list[EvidenceReference] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceCollection:
    name: str
    kind: str = UNKNOWN
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceCase:
    """Contenedor permanente de un caso documental (la biblioteca de evidencias)."""

    case_id: str
    title: str = ""
    schema_version: str = SCHEMA_VERSION
    people: list[EvidencePerson] = field(default_factory=list)
    locations: list[EvidenceLocation] = field(default_factory=list)
    timeline: EvidenceTimeline = field(default_factory=EvidenceTimeline)
    collections: list[EvidenceCollection] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    sources: list[EvidenceSource] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "title": self.title,
            "people": [p.to_dict() for p in self.people],
            "locations": [loc.to_dict() for loc in self.locations],
            "timeline": self.timeline.to_dict(),
            "collections": [c.to_dict() for c in self.collections],
            "evidence": [e.to_dict() for e in self.evidence],
            "sources": [s.to_dict() for s in self.sources],
            "notes": list(self.notes),
        }
