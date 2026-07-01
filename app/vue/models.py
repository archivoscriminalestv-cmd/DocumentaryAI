"""Modelos del Visual Understanding Engine (VUE).

Modelos ESTABLES y versionados, preparados para crecer sin romper compatibilidad. Solo
representan HECHOS observables. ``confidence`` es ``None`` cuando no se ha medido (nunca
se inventa una puntuación). Los vocabularios incluyen siempre ``UNKNOWN``.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.vue import SCHEMA_VERSION, UNKNOWN

# --- vocabularios cinematográficos (cerrados pero ampliables; siempre con UNKNOWN) ---


class ShotSize:
    EXTREME_WIDE = "extreme_wide"
    WIDE = "wide"
    FULL = "full"
    AMERICAN = "american"
    MEDIUM = "medium"
    MEDIUM_CLOSE = "medium_close"
    CLOSE = "close"
    EXTREME_CLOSE = "extreme_close"
    UNKNOWN = UNKNOWN
    ALL = (EXTREME_WIDE, WIDE, FULL, AMERICAN, MEDIUM, MEDIUM_CLOSE, CLOSE, EXTREME_CLOSE, UNKNOWN)


class Composition:
    CENTERED = "centered"
    RULE_OF_THIRDS = "rule_of_thirds"
    SYMMETRY = "symmetry"
    LEADING_LINES = "leading_lines"
    NEGATIVE_SPACE = "negative_space"
    DIAGONAL = "diagonal"
    FOREGROUND_FRAMING = "foreground_framing"
    UNKNOWN = UNKNOWN
    ALL = (CENTERED, RULE_OF_THIRDS, SYMMETRY, LEADING_LINES, NEGATIVE_SPACE,
           DIAGONAL, FOREGROUND_FRAMING, UNKNOWN)


class SceneType:
    INTERVIEW = "interview"
    B_ROLL = "b_roll"
    ARCHIVAL = "archival"
    REENACTMENT = "reenactment"
    ESTABLISHING = "establishing"
    MAP = "map"
    DOCUMENT = "document"
    UNKNOWN = UNKNOWN
    ALL = (INTERVIEW, B_ROLL, ARCHIVAL, REENACTMENT, ESTABLISHING, MAP, DOCUMENT, UNKNOWN)


class EvidenceType:
    PHOTO = "photo"
    DOCUMENT = "document"
    MAP = "map"
    NEWSPAPER = "newspaper"
    SCREEN = "screen"
    OBJECT = "object"
    UNKNOWN = UNKNOWN
    ALL = (PHOTO, DOCUMENT, MAP, NEWSPAPER, SCREEN, OBJECT, UNKNOWN)


# Capacidades (una por detector). Crece añadiendo entradas, sin romper nada.
# VUE-002 añade (aditivo) las capacidades de visión clásica: color/edge/motion/geometry.
CAPABILITIES = (
    "shot_size", "composition", "face_layout", "text", "evidence",
    "scene_type", "object", "map", "document",
    "color", "edge_density", "motion_energy", "frame_geometry",
    # VUE-003 (disposición / localización; geometría objetiva, aún sin clasificar)
    "subject_localization", "layout_balance", "visual_weight", "empty_space",
)


# --- payloads tipados de hechos (todos UNKNOWN-friendly) ---------------------


@dataclass
class FaceLayout:
    face_count: int | None = None        # None = no medido
    regions: list[dict] = field(default_factory=list)  # [{x,y,w,h}] normalizado, futuro
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DetectedText:
    present: str = UNKNOWN                # "true" | "false" | UNKNOWN
    blocks: list[str] = field(default_factory=list)
    regions: list[dict] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ObjectDetection:
    objects: list[dict] = field(default_factory=list)  # [{label, box, ...}]
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# --- payloads de disposición/localización (VUE-003; aditivos, hechos objetivos) ---


@dataclass
class SubjectRegion:
    bbox: dict | None = None              # {x0,y0,x1,y1} normalizado 0..1; None = UNKNOWN
    center: dict | None = None           # {x,y}
    occupancy: float = 0.0               # área del bbox / área del frame
    distances: dict = field(default_factory=dict)   # {left,right,top,bottom} a los bordes
    free_margin: float = 0.0             # mínima distancia a un borde
    position: str = UNKNOWN              # p.ej. "top-left", "middle-center"
    method: str = ""
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LayoutBalance:
    horizontal: dict = field(default_factory=dict)   # {left,center,right}
    vertical: dict = field(default_factory=dict)     # {top,middle,bottom}
    horizontal_symmetry: float | None = None         # 0..1 (1 = simétrico)
    vertical_symmetry: float | None = None
    concentration: float = 0.0           # masa en la celda más densa (0..1)
    dispersion: float = 0.0              # 0..1 (1 = repartido)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VisualWeight:
    left: float = 0.0
    right: float = 0.0
    top: float = 0.0
    bottom: float = 0.0
    center_of_gravity: dict | None = None            # {x,y} normalizado
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EmptySpace:
    empty_fraction: float = 0.0          # fracción de zonas planas (sin detalle)
    largest_empty_fraction: float = 0.0  # mayor región vacía contigua / frame
    largest_empty_bbox: dict | None = None
    distribution: dict = field(default_factory=dict)  # vacío por tercios (3x3)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# --- observación universal de un detector + análisis del plano ----------------


@dataclass
class VisualObservation:
    """Salida universal de un detector: un HECHO objetivo sobre un fotograma."""

    detector: str
    capability: str
    value: Any = UNKNOWN                  # categoría del vocabulario o UNKNOWN
    confidence: float | None = None       # None = no medido (jamás inventado)
    facts: dict = field(default_factory=dict)   # payload objetivo (FaceLayout.to_dict()…)
    method: str = "not_implemented"       # cómo se obtuvo (det. real | not_implemented)
    schema_version: str = SCHEMA_VERSION

    def is_unknown(self) -> bool:
        return self.value == UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VisualAnalysis:
    """Resultado del VUE para UN fotograma: el conjunto de observaciones objetivas."""

    frame_id: str = ""
    frame_index: int = 0
    timestamp: float = 0.0
    schema_version: str = SCHEMA_VERSION
    observations: list[VisualObservation] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

    def by_capability(self, capability: str) -> VisualObservation | None:
        for o in self.observations:
            if o.capability == capability:
                return o
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "frame_id": self.frame_id,
            "frame_index": self.frame_index,
            "timestamp": self.timestamp,
            "observations": [o.to_dict() for o in self.observations],
            "errors": list(self.errors),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VisualAnalysis":
        obs = [VisualObservation(**{k: v for k, v in o.items()
                                    if k in VisualObservation.__dataclass_fields__})
               for o in data.get("observations", [])]
        return cls(
            frame_id=data.get("frame_id", ""), frame_index=data.get("frame_index", 0),
            timestamp=data.get("timestamp", 0.0),
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            observations=obs, errors=list(data.get("errors", [])),
        )
