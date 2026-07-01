"""Modelos del Evidence Investigation Planner (EAE-002).

Tipados, serializables, deterministas y versionados. No almacenan binarios: solo
PLANIFICACIÓN (qué se necesita, prioridad, cobertura, tareas). Nunca inventan: lo no
conseguido cuenta como pendiente (acquired=0).
"""

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

from app.eae.planner import PLANNER_SCHEMA_VERSION


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii").lower()
    slug = "".join(ch if ch.isalnum() else "_" for ch in norm)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "x"


class EvidenceCategory:
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"
    PRESS_CONFERENCE = "PRESS_CONFERENCE"
    NEWS = "NEWS"
    NEWSPAPER = "NEWSPAPER"
    COURT_DOCUMENT = "COURT_DOCUMENT"
    POLICE_DOCUMENT = "POLICE_DOCUMENT"
    MAP = "MAP"
    SATELLITE = "SATELLITE"
    INTERVIEW = "INTERVIEW"
    TV_REPORT = "TV_REPORT"
    SOCIAL_POST = "SOCIAL_POST"
    BOOK = "BOOK"
    AUDIO = "AUDIO"
    TIMELINE = "TIMELINE"
    PUBLIC_RECORD = "PUBLIC_RECORD"
    OFFICIAL_STATEMENT = "OFFICIAL_STATEMENT"
    FORENSIC_IMAGE = "FORENSIC_IMAGE"
    SCENE_PHOTO = "SCENE_PHOTO"
    ARCHIVE_VIDEO = "ARCHIVE_VIDEO"
    ALL = (PHOTO, VIDEO, PRESS_CONFERENCE, NEWS, NEWSPAPER, COURT_DOCUMENT, POLICE_DOCUMENT,
           MAP, SATELLITE, INTERVIEW, TV_REPORT, SOCIAL_POST, BOOK, AUDIO, TIMELINE,
           PUBLIC_RECORD, OFFICIAL_STATEMENT, FORENSIC_IMAGE, SCENE_PHOTO, ARCHIVE_VIDEO)


class EvidencePriority:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    OPTIONAL = "OPTIONAL"
    RANK = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, OPTIONAL: 4}


class ResearchStage:
    DISCOVERY = "DISCOVERY"
    VERIFICATION = "VERIFICATION"
    ACQUISITION = "ACQUISITION"
    ORGANIZATION = "ORGANIZATION"
    ORDER = (DISCOVERY, VERIFICATION, ACQUISITION, ORGANIZATION)


class CoverageState:
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COVERED = "COVERED"


def _only(data: dict, cls) -> dict:
    """Filtra un dict a los campos del dataclass ``cls`` (ignora claves extra/derivadas)."""
    valid = set(getattr(cls, "__dataclass_fields__", {}))
    return {k: v for k, v in (data or {}).items() if k in valid}


@dataclass
class CaseProfile:
    """Entrada ÚNICA del planner. Describe el caso a investigar (sin material todavía)."""

    case_id: str
    title: str = ""
    genre: str = "generic"               # true_crime | history | biography | nature | generic
    subject: str = ""
    people: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    time_period: str = ""
    constraints: list[str] = field(default_factory=list)
    license_requirements: list[str] = field(default_factory=list)
    priority_sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CaseProfile":
        return cls(**_only(data, cls))


@dataclass
class CoverageRequirement:
    minimum: int = 0
    ideal: int = 0
    acquired: int = 0                    # siempre 0 en planificación (nunca inventa)

    @property
    def missing(self) -> int:
        return max(0, self.minimum - self.acquired)

    @property
    def coverage_percent(self) -> float:
        return round(min(1.0, self.acquired / self.minimum), 4) if self.minimum else 1.0

    @property
    def state(self) -> str:
        if self.acquired >= self.minimum and self.minimum > 0:
            return CoverageState.COVERED
        if self.acquired > 0:
            return CoverageState.PARTIAL
        return CoverageState.PENDING

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.update(missing=self.missing, coverage_percent=self.coverage_percent, state=self.state)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "CoverageRequirement":
        return cls(minimum=int(data.get("minimum", 0)), ideal=int(data.get("ideal", 0)),
                   acquired=int(data.get("acquired", 0)))


@dataclass
class EvidenceNeed:
    id: str
    category: str
    priority: str
    target: str = "case"                 # "case" | nombre de persona/lugar/evento
    requirement: CoverageRequirement = field(default_factory=CoverageRequirement)
    sources: list[str] = field(default_factory=list)   # proveedores prioritarios sugeridos
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["requirement"] = self.requirement.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "EvidenceNeed":
        return cls(
            id=data["id"], category=data["category"], priority=data["priority"],
            target=data.get("target", "case"),
            requirement=CoverageRequirement.from_dict(data.get("requirement", {})),
            sources=list(data.get("sources", [])), rationale=data.get("rationale", ""),
        )


@dataclass
class ExpectedEvidence:
    target: str
    category: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InvestigationTarget:
    id: str
    kind: str                            # person | location | event | case
    name: str = ""
    need_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SearchTask:
    id: str
    need_id: str
    category: str
    target: str
    priority: str
    query_terms: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


    @classmethod
    def from_dict(cls, data: dict) -> "SearchTask":
        return cls(id=data["id"], need_id=data["need_id"], category=data["category"],
                   target=data["target"], priority=data["priority"],
                   query_terms=list(data.get("query_terms", [])),
                   sources=list(data.get("sources", [])))


@dataclass
class AcquisitionTask:
    id: str
    need_id: str
    category: str
    target: str
    priority: str
    target_count: int = 0                # cantidad MÍNIMA a adquirir (minimiza descargas)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceManifest:
    """Descripción completa del proyecto documental (planificación; sin binarios)."""

    case_id: str
    title: str = ""
    schema_version: str = PLANNER_SCHEMA_VERSION
    people: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    expected_material: list[ExpectedEvidence] = field(default_factory=list)
    desired_coverage: dict = field(default_factory=dict)    # categoría -> min/ideal
    priority_sources: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    licenses: list[str] = field(default_factory=list)
    coverage_status: dict = field(default_factory=dict)
    pending_material: list[str] = field(default_factory=list)
    acquired_material: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["expected_material"] = [e.to_dict() for e in self.expected_material]
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "EvidenceManifest":
        m = cls(case_id=data.get("case_id", ""), title=data.get("title", ""))
        m.people = list(data.get("people", []))
        m.locations = list(data.get("locations", []))
        m.timeline = list(data.get("timeline", []))
        m.desired_coverage = dict(data.get("desired_coverage", {}))
        m.priority_sources = list(data.get("priority_sources", []))
        m.constraints = list(data.get("constraints", []))
        m.licenses = list(data.get("licenses", []))
        m.pending_material = list(data.get("pending_material", []))
        return m


@dataclass
class InvestigationPlan:
    case_id: str
    schema_version: str = PLANNER_SCHEMA_VERSION
    profile: CaseProfile | None = None
    manifest: EvidenceManifest | None = None
    targets: list[InvestigationTarget] = field(default_factory=list)
    needs: list[EvidenceNeed] = field(default_factory=list)
    search_tasks: list[SearchTask] = field(default_factory=list)
    acquisition_tasks: list[AcquisitionTask] = field(default_factory=list)
    stages: list[str] = field(default_factory=list)
    coverage_summary: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "profile": self.profile.to_dict() if self.profile else None,
            "manifest": self.manifest.to_dict() if self.manifest else None,
            "targets": [t.to_dict() for t in self.targets],
            "needs": [n.to_dict() for n in self.needs],
            "search_tasks": [s.to_dict() for s in self.search_tasks],
            "acquisition_tasks": [a.to_dict() for a in self.acquisition_tasks],
            "stages": list(self.stages),
            "coverage_summary": self.coverage_summary,
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InvestigationPlan":
        return cls(
            case_id=data.get("case_id", ""),
            schema_version=data.get("schema_version", PLANNER_SCHEMA_VERSION),
            profile=CaseProfile.from_dict(data["profile"]) if data.get("profile") else None,
            manifest=EvidenceManifest.from_dict(data["manifest"]) if data.get("manifest") else None,
            needs=[EvidenceNeed.from_dict(n) for n in data.get("needs", [])],
            search_tasks=[SearchTask.from_dict(s) for s in data.get("search_tasks", [])],
            stages=list(data.get("stages", [])),
            notes=list(data.get("notes", [])),
        )
