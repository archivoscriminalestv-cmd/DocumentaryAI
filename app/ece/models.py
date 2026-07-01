"""Modelos del Evidence Correlation Engine (ECE).

Tipados, serializables, deterministas, sin marcas de tiempo. El grafo y los análisis solo
reflejan hechos OBSERVABLES de las evidencias; nada se infiere ni se decide.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.ece import ECE_VERSION, SCHEMA_VERSION


class NodeType:
    PERSON = "Person"
    EVENT = "Event"
    LOCATION = "Location"
    EVIDENCE = "Evidence"
    TIMELINE = "Timeline"
    ORGANIZATION = "Organization"


class RelationType:
    SAME_EVENT = "SAME_EVENT"
    SAME_LOCATION = "SAME_LOCATION"
    SAME_PERSON = "SAME_PERSON"
    REFERENCES = "REFERENCES"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    MENTIONS = "MENTIONS"
    DERIVED_FROM = "DERIVED_FROM"


class CoverageState:
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"


@dataclass
class GraphNode:
    id: str
    type: str
    label: str = ""
    attributes: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GraphRelation:
    source_id: str
    relation: str
    target_id: str
    evidence_ids: list[str] = field(default_factory=list)   # hechos que soportan la relación
    basis: str = ""                                         # qué se observó (auditable)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceGraph:
    schema_version: str = SCHEMA_VERSION
    nodes: list[GraphNode] = field(default_factory=list)
    relations: list[GraphRelation] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "nodes": [n.to_dict() for n in self.nodes],
            "relations": [r.to_dict() for r in self.relations],
        }


@dataclass
class Conflict:
    id: str
    kind: str                       # date | location | name | other
    subject_id: str                 # nodo afectado (evento/persona/lugar)
    field: str
    candidates: list[dict] = field(default_factory=list)   # [{value, evidence_id, provider}]
    requires_verification: bool = True                     # SIEMPRE: no se decide aquí

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CoverageDimension:
    name: str
    required: int = 0
    discovered: int = 0
    state: str = CoverageState.MISSING
    evidence_ids: list[str] = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CoverageReport:
    schema_version: str = SCHEMA_VERSION
    case_id: str = ""
    dimensions: list[CoverageDimension] = field(default_factory=list)
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "summary": self.summary,
        }


@dataclass
class RecreationCandidate:
    """Dónde PODRÍA hacer falta una recreación (no se genera nada)."""

    id: str
    story_segment: str
    reason: str = ""
    existing_coverage: str = CoverageState.MISSING
    suggested_type: str = "illustration"   # scene_reconstruction | animated_map | 3d | ...
    available_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    factual_basis: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CorrelationResult:
    case_id: str = ""
    ece_version: str = ECE_VERSION
    graph: EvidenceGraph = field(default_factory=EvidenceGraph)
    coverage: CoverageReport = field(default_factory=CoverageReport)
    conflicts: list[Conflict] = field(default_factory=list)
    recreation_candidates: list[RecreationCandidate] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "ece_version": self.ece_version,
            "graph": self.graph.to_dict(),
            "coverage": self.coverage.to_dict(),
            "conflicts": [c.to_dict() for c in self.conflicts],
            "recreation_candidates": [r.to_dict() for r in self.recreation_candidates],
        }
