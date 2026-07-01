"""Modelos del Self Evaluation Engine (DCA-003).

Tipados, deterministas, serializables, sin marcas de tiempo. Miden la distancia entre la
generación y el corpus; nunca interpretan ni opinan.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.dca.evaluation import EVAL_SCHEMA_VERSION, EVAL_VERSION

UNKNOWN = "UNKNOWN"


class MetricStatus:
    ALIGNED = "aligned"
    DIFFERS = "differs"
    UNKNOWN = "unknown"


@dataclass
class ComparisonMetric:
    dimension: str
    corpus_value: Any = UNKNOWN
    generated_value: Any = UNKNOWN
    deviation: float | None = None        # 0..1 (numérico) o 1.0/0.0 (categórico); None si UNKNOWN
    kind: str = "categorical"             # numeric | categorical | coverage
    status: str = MetricStatus.UNKNOWN
    unit: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Gap:
    id: str
    dimension: str
    description: str               # hecho, nunca opinión ("shot duration differs 48%")
    magnitude: float = 0.0         # 0..1
    owner: str = UNKNOWN           # subsistema responsable
    kind: str = "generation"       # generation | architecture

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ImprovementItem:
    id: str
    target: str                    # subsistema a mejorar
    rationale: str = ""
    metrics: dict = field(default_factory=dict)   # señales objetivas (consumers/magnitude/…)
    priority_rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SystemHealth:
    knowledge_utilization: Any = UNKNOWN
    generation_coverage: Any = UNKNOWN
    evidence_coverage: Any = UNKNOWN
    corpus_alignment: Any = UNKNOWN
    unknown_decisions: Any = UNKNOWN
    integrated_capabilities: Any = UNKNOWN
    missing_capabilities: Any = UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvaluationResult:
    schema_version: str = EVAL_SCHEMA_VERSION
    eval_version: str = EVAL_VERSION
    comparisons: list[ComparisonMetric] = field(default_factory=list)
    gaps: list[Gap] = field(default_factory=list)
    roadmap: list[ImprovementItem] = field(default_factory=list)
    health: SystemHealth = field(default_factory=SystemHealth)
    summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "eval_version": self.eval_version,
            "comparisons": [c.to_dict() for c in self.comparisons],
            "gaps": [g.to_dict() for g in self.gaps],
            "roadmap": [i.to_dict() for i in self.roadmap],
            "health": self.health.to_dict(),
            "summary": self.summary,
        }

    def generation_vs_corpus(self) -> dict:
        return {c.dimension: {"corpus": c.corpus_value, "generated": c.generated_value,
                              "deviation": c.deviation, "status": c.status}
                for c in self.comparisons}
