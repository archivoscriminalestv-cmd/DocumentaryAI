"""Modelos tipados de la arquitectura de DocumentaryAI (DCA).

Versionados, deterministas y serializables. Representan el sistema completo: dominios,
subsistemas (motores), capacidades, dependencias, pipeline, objetivos, huecos, cuellos de
botella, mejoras, recomendaciones, roadmap y un snapshot global.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.dca import DCA_VERSION, SCHEMA_VERSION, UNKNOWN


class Status:
    IMPLEMENTED = "implemented"
    NOT_INTEGRATED = "implemented_not_integrated"
    DESIGN = "design"
    PLANNED = "planned"
    UNKNOWN = UNKNOWN
    # orden de prioridad para el roadmap (menor = se aborda antes)
    RANK = {NOT_INTEGRATED: 0, DESIGN: 1, PLANNED: 2, UNKNOWN: 3, IMPLEMENTED: 4}


@dataclass
class Subsystem:
    name: str
    domain: str = UNKNOWN
    responsibility: str = ""
    status: str = Status.UNKNOWN
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)   # nombres de otros subsistemas
    produces: list[str] = field(default_factory=list)       # capacidades
    consumes: list[str] = field(default_factory=list)       # capacidades
    docs: list[str] = field(default_factory=list)           # ADR/RFC/SPEC relacionados

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Capability:
    name: str
    producers: list[str] = field(default_factory=list)
    consumers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Dependency:
    source: str
    target: str
    kind: str = "direct"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Domain:
    name: str
    subsystems: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Pipeline:
    name: str
    stages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Goal:
    id: str
    name: str
    status: str = UNKNOWN
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Gap:
    id: str
    kind: str                       # missing_capability | not_integrated | duplicate | unused | knowledge_unused
    description: str = ""
    related: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Bottleneck:
    id: str
    subsystem: str
    reason: str = ""
    consumers: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Improvement:
    id: str
    target: str
    rationale: str = ""
    metrics: dict = field(default_factory=dict)   # señales objetivas (counts/bools)
    priority_rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Recommendation:
    id: str
    title: str
    target: str
    rationale: str = ""
    priority_rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Roadmap:
    schema_version: str = SCHEMA_VERSION
    items: list[Improvement] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version,
                "items": [i.to_dict() for i in self.items]}


@dataclass
class SystemArchitecture:
    schema_version: str = SCHEMA_VERSION
    dca_version: str = DCA_VERSION
    domains: list[Domain] = field(default_factory=list)
    subsystems: list[Subsystem] = field(default_factory=list)
    capabilities: list[Capability] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)
    pipelines: list[Pipeline] = field(default_factory=list)
    goals: list[Goal] = field(default_factory=list)
    coverage: dict = field(default_factory=dict)
    docs_index: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "dca_version": self.dca_version,
            "domains": [d.to_dict() for d in self.domains],
            "subsystems": [s.to_dict() for s in self.subsystems],
            "capabilities": [c.to_dict() for c in self.capabilities],
            "dependencies": [d.to_dict() for d in self.dependencies],
            "pipelines": [p.to_dict() for p in self.pipelines],
            "goals": [g.to_dict() for g in self.goals],
            "coverage": self.coverage,
            "docs_index": self.docs_index,
        }


@dataclass
class ArchitectureSnapshot:
    schema_version: str = SCHEMA_VERSION
    dca_version: str = DCA_VERSION
    architecture: SystemArchitecture = field(default_factory=SystemArchitecture)
    totals: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "dca_version": self.dca_version,
            "totals": self.totals,
            "architecture": self.architecture.to_dict(),
        }
