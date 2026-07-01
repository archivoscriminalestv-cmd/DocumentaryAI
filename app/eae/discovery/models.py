"""Modelos del Case Discovery Engine (EAE-003).

Tipados, serializables, deterministas, sin marcas de tiempo. ``DiscoveredEvidence`` es un
PUNTERO rico a material que existe (no el binario). ``DiscoveryPlan`` agrega cobertura por
necesidad. ``DiscoveryManifest`` es el registro extremadamente rico (cadena de custodia,
estado, duplicados, referencias cruzadas, relaciones). UNKNOWN/None antes que inventar.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.eae import UNKNOWN
from app.eae.discovery import DISCOVERY_SCHEMA_VERSION


class Availability:
    AVAILABLE = "AVAILABLE"
    RESTRICTED = "RESTRICTED"
    PAID = "PAID"
    UNKNOWN = UNKNOWN


class DiscoveryState:
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COVERED = "COVERED"


@dataclass
class DiscoveredEvidence:
    """Puntero rico a una evidencia localizada (sin descargar)."""

    id: str
    need_id: str = ""
    target: str = ""
    category: str = UNKNOWN
    title: str = ""
    url: str = ""
    provider: str = ""
    media_type: str = UNKNOWN
    license: str = UNKNOWN
    resolution: str = UNKNOWN
    duration: float | None = None
    language: str = UNKNOWN
    fmt: str = UNKNOWN                    # formato (jpg/pdf/mp4/…)
    size_bytes: int | None = None
    hash: str = ""                       # si la fuente lo expone; nunca se inventa
    reliability: str = UNKNOWN           # declarada por el proveedor
    date: str = UNKNOWN
    availability: str = Availability.UNKNOWN
    restrictions: list[str] = field(default_factory=list)
    priority: str = UNKNOWN
    query_used: list[str] = field(default_factory=list)   # consulta que la localizó (auditable)
    # datos estructurados específicos del proveedor para que la ADQUISICIÓN futura no tenga
    # que volver a consultar (coordenadas, bbox, qid, identifier, mime, thumbnail, …).
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NeedCoverage:
    need_id: str
    category: str
    target: str
    priority: str
    minimum: int = 0
    ideal: int = 0
    discovered: int = 0
    state: str = DiscoveryState.PENDING
    candidate_providers: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    # auditoría por proveedor: {provider, available, selected, reason, results, cost}
    provider_decisions: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SourceCapability:
    name: str
    available: bool = False
    media: list[str] = field(default_factory=list)
    licenses: list[str] = field(default_factory=list)
    priority: int = 100
    cost: str = UNKNOWN
    rate_limits: dict = field(default_factory=dict)
    reliability: str = UNKNOWN
    capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiscoveryPlan:
    case_id: str
    title: str = ""
    schema_version: str = DISCOVERY_SCHEMA_VERSION
    totals: dict = field(default_factory=dict)            # required/discovered/pending
    by_category: dict = field(default_factory=dict)       # cat -> counts + state + candidatas
    by_provider: dict = field(default_factory=dict)       # provider -> nº resultados
    needs: list[NeedCoverage] = field(default_factory=list)
    discovered: list[DiscoveredEvidence] = field(default_factory=list)
    sources_consulted: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    # tiempos de búsqueda por proveedor (NO determinista → excluido de to_dict; va al manifest)
    timings: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        # NOTA: ``timings`` se omite a propósito (no determinista). El resto es reproducible.
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "title": self.title,
            "totals": self.totals,
            "by_category": self.by_category,
            "by_provider": self.by_provider,
            "needs": [n.to_dict() for n in self.needs],
            "discovered": [d.to_dict() for d in self.discovered],
            "sources_consulted": list(self.sources_consulted),
            "notes": list(self.notes),
        }


@dataclass
class ManifestEntry:
    """Entrada extremadamente rica del manifest (cadena de custodia completa)."""

    evidence_id: str
    category: str = UNKNOWN
    target: str = ""
    provider: str = ""
    origin: str = ""                     # URL/identificador de origen
    chain_of_custody: list[str] = field(default_factory=list)
    status: str = "DISCOVERED"           # DISCOVERED | PENDING | ...
    downloaded: bool = False
    validated: bool = False
    duplicates: list[str] = field(default_factory=list)
    hash: str = ""
    license: str = UNKNOWN
    permitted_use: str = UNKNOWN
    cross_references: list[str] = field(default_factory=list)
    related_people: list[str] = field(default_factory=list)
    related_locations: list[str] = field(default_factory=list)
    related_events: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    query_used: list[str] = field(default_factory=list)
    selection_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DiscoveryManifest:
    case_id: str
    title: str = ""
    schema_version: str = DISCOVERY_SCHEMA_VERSION
    totals: dict = field(default_factory=dict)
    entries: list[ManifestEntry] = field(default_factory=list)
    pending_needs: list[str] = field(default_factory=list)
    people: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    provider_audit: list[dict] = field(default_factory=list)  # provider -> results/search_ms/cost

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "title": self.title,
            "totals": self.totals,
            "entries": [e.to_dict() for e in self.entries],
            "pending_needs": list(self.pending_needs),
            "people": list(self.people),
            "locations": list(self.locations),
            "timeline": list(self.timeline),
            "provider_audit": list(self.provider_audit),
        }
