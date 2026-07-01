"""Modelos del Production Advisor (scaffold).

Todo serializable y versionado. Los valores desconocidos valen ``None``/``UNKNOWN``
(nunca se inventan): el corpus aún no expone todas las señales (entrevistas, mapas,
documentos…), así que la cobertura de muchas capacidades será UNKNOWN en este sprint.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.advisor import SCHEMA_VERSION, UNKNOWN


class Dimension:
    """Dimensiones por las que se comparan corpus y pipeline."""
    PACING = "pacing"
    SHOT_DIVERSITY = "shot_diversity"
    MOTION = "motion"
    LIGHTING = "lighting"
    COLOR = "color"
    AUDIO = "audio"
    NARRATION = "narration"
    CAPABILITY = "capability"


class Severity:
    INFO = "INFO"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class Impact:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Effort:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CoverageStatus:
    SUPPORTED = "SUPPORTED"   # corpus lo mide y el pipeline lo produce
    MISSING = "MISSING"       # el pipeline NO lo produce (hecho conocido)
    UNKNOWN = "UNKNOWN"       # sin evidencia pública para comparar


class Confidence:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


def confidence_from(observations: int, *, high: int, medium: int) -> str:
    """Confianza SOLO por tamaño muestral (sin pesos subjetivos)."""
    if observations >= high:
        return Confidence.HIGH
    if observations >= medium:
        return Confidence.MEDIUM
    return Confidence.LOW


# Umbrales de tamaño muestral (planos vs documentales).
SHOT_CONFIDENCE = {"high": 5000, "medium": 500}
DOC_CONFIDENCE = {"high": 40, "medium": 10}

# Dimensiones cinematográficas medibles en el corpus (DKS) y su soporte en el pipeline.
DIMENSIONS = ("movement", "lighting", "color_temperature", "dominant_color",
              "shot_size", "composition", "pacing_tier")
_DIMENSION_PIPELINE_SUPPORT = {
    "movement": "yes", "lighting": "yes", "color_temperature": "yes",
    "dominant_color": "yes", "shot_size": "yes", "composition": "yes", "pacing_tier": "yes",
}


# Capacidades de producción cuya cobertura en el corpus interesa medir (taxonomía
# estable; la detección real llegará cuando el corpus exponga estas señales).
CAPABILITIES = (
    "real_footage", "interviews", "maps", "documents", "archival_photos",
    "reenactments", "on_screen_text", "b_roll", "narration", "music",
)


@dataclass
class CapabilityUsage:
    capability: str
    corpus_percent: float | None = None     # 0..1 del corpus que la usa; None = UNKNOWN
    pipeline_supported: str = UNKNOWN        # yes | no | UNKNOWN
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CorpusSnapshot:
    """Fotografía agregada del corpus leída de artefactos PÚBLICOS de knowledge/."""

    schema_version: str = SCHEMA_VERSION
    available: bool = False                  # False si no hay corpus legible
    documentaries: int = 0
    hours: float = 0.0
    shots: int = 0
    scenes: int = 0
    average_shot_length: float | None = None
    cuts_per_minute: float | None = None
    pacing_distribution: dict = field(default_factory=dict)
    shot_size_distribution: dict = field(default_factory=dict)
    movement_distribution: dict = field(default_factory=dict)
    lighting_distribution: dict = field(default_factory=dict)
    color_temperature_distribution: dict = field(default_factory=dict)
    capabilities: list[CapabilityUsage] = field(default_factory=list)
    sources_read: list[str] = field(default_factory=list)
    # ADV-002: distribuciones medidas {dim: {counts, fractions, total}} y stats numéricas.
    dimensions: dict = field(default_factory=dict)
    numeric: dict = field(default_factory=dict)
    measured_shots: int = 0                 # total de planos según las distribuciones DKS
    documentaries_measured: int = 0         # documentales según DKS

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


@dataclass
class CapabilityMatrixRow:
    name: str
    kind: str                               # dimension | capability
    corpus_observed: bool = False
    corpus_fraction: float | None = None    # cobertura/dominante observada; None = UNKNOWN
    observations: int = 0
    pipeline: str = UNKNOWN                  # yes | no | UNKNOWN
    status: str = "UNKNOWN"                  # CoverageStatus
    confidence: str = "LOW"
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompletenessFinding:
    dimension: str
    category: str
    fraction: float
    observations: int
    confidence: str = "LOW"
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Discovery:
    id: str
    statement: str
    dimension: str
    value: str = ""
    fraction: float | None = None
    observations: int = 0
    confidence: str = "LOW"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GapFinding:
    id: str
    title: str
    dimension: str
    severity: str = Severity.INFO
    corpus_value: Any = None
    pipeline_value: Any = None
    rationale: str = ""
    # ADV-002: evidencia medida que respalda el gap (frecuencia observada + muestra).
    frequency: float | None = None          # 0..1; None = no cuantificable (sin evidencia)
    observations: int = 0
    confidence: str = "LOW"
    rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Recommendation:
    id: str
    title: str
    impact: str = Impact.MEDIUM
    effort: str = Effort.MEDIUM
    priority: float = 0.0                     # mayor = antes
    rationale: str = ""
    addresses: list[str] = field(default_factory=list)   # ids de GapFinding

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdvisorReport:
    schema_version: str = SCHEMA_VERSION
    generated_from: str = ""                  # raíz de knowledge usada
    snapshot: CorpusSnapshot = field(default_factory=CorpusSnapshot)
    gaps: list[GapFinding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    roadmap: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    # ADV-002
    capability_matrix: list[CapabilityMatrixRow] = field(default_factory=list)
    completeness: list[CompletenessFinding] = field(default_factory=list)
    discoveries: list[Discovery] = field(default_factory=list)
    confidence_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_from": self.generated_from,
            "snapshot": self.snapshot.to_dict(),
            "capability_matrix": [r.to_dict() for r in self.capability_matrix],
            "gaps": [g.to_dict() for g in self.gaps],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "completeness": [c.to_dict() for c in self.completeness],
            "discoveries": [d.to_dict() for d in self.discoveries],
            "roadmap": list(self.roadmap),
            "confidence_notes": list(self.confidence_notes),
            "notes": list(self.notes),
        }
