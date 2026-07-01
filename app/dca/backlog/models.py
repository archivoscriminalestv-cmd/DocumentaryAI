"""Modelos del Architectural Backlog (DCA-004).

El backlog es la MEMORIA ESTRATÉGICA permanente de DocumentaryAI: registra mejoras, ideas,
hipótesis y deuda arquitectónica detectadas durante el desarrollo. El documento humano vive en
``docs/roadmap/ARCHITECTURAL-BACKLOG.md``; estos modelos son su representación interna, cargada
por el DCA. Tipados, serializables, deterministas, sin timestamps.

El DCA solo PROPONE cambios (BacklogProposal); nunca reescribe el documento automáticamente.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.dca.backlog import BACKLOG_SCHEMA_VERSION


class EntryStatus:
    """Ciclo de vida de cualquier entrada del backlog (estados permitidos)."""

    IDEA = "IDEA"
    PLANNED = "PLANNED"
    DESIGNED = "DESIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    ALL = (IDEA, PLANNED, DESIGNED, IN_PROGRESS, COMPLETED, REJECTED)
    # Orden de progresión (para validar transiciones).
    ORDER = {IDEA: 0, PLANNED: 1, DESIGNED: 2, IN_PROGRESS: 3, COMPLETED: 4}


class Priority:
    P0 = "P0"   # imprescindibles antes de producción
    P1 = "P1"   # muy importantes
    P2 = "P2"   # mejoras futuras
    P3 = "P3"   # ideas de investigación
    ALL = (P0, P1, P2, P3)


class HypothesisStatus:
    UNKNOWN = "UNKNOWN"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    ALL = (UNKNOWN, VALIDATED, REJECTED)


class Section:
    VISION = "VISION"
    STRATEGIC_PRIORITIES = "STRATEGIC_PRIORITIES"
    OPEN_IDEAS = "OPEN_IDEAS"
    HYPOTHESES = "HYPOTHESES"
    TECHNICAL_DEBT = "TECHNICAL_DEBT"
    COMPLETED = "COMPLETED"
    ALL = (VISION, STRATEGIC_PRIORITIES, OPEN_IDEAS, HYPOTHESES, TECHNICAL_DEBT, COMPLETED)


@dataclass
class BacklogEntry:
    """Una entrada del backlog (mejora, idea, hipótesis o deuda)."""

    id: str
    title: str
    section: str
    status: str = EntryStatus.IDEA
    priority: str = ""                       # solo en Strategic Priorities
    hypothesis_status: str = ""              # solo en Hypotheses
    description: str = ""
    related: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArchitecturalBacklog:
    """Representación interna completa del documento del backlog."""

    vision: str = ""
    entries: list[BacklogEntry] = field(default_factory=list)
    source_path: str = ""
    schema_version: str = BACKLOG_SCHEMA_VERSION

    # --- consultas -------------------------------------------------------
    def get(self, entry_id: str) -> BacklogEntry | None:
        return next((e for e in self.entries if e.id == entry_id), None)

    def by_section(self, section: str) -> list[BacklogEntry]:
        return [e for e in self.entries if e.section == section]

    def by_status(self, status: str) -> list[BacklogEntry]:
        return [e for e in self.entries if e.status == status]

    def by_priority(self, priority: str) -> list[BacklogEntry]:
        return [e for e in self.entries if e.priority == priority]

    @property
    def counts(self) -> dict:
        by_status: dict[str, int] = {}
        by_priority: dict[str, int] = {}
        by_section: dict[str, int] = {}
        for e in self.entries:
            by_status[e.status] = by_status.get(e.status, 0) + 1
            by_section[e.section] = by_section.get(e.section, 0) + 1
            if e.priority:
                by_priority[e.priority] = by_priority.get(e.priority, 0) + 1
        return {
            "total": len(self.entries),
            "by_status": {k: by_status[k] for k in sorted(by_status)},
            "by_priority": {k: by_priority[k] for k in sorted(by_priority)},
            "by_section": {k: by_section[k] for k in sorted(by_section)},
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source_path": self.source_path,
            "vision": self.vision,
            "counts": self.counts,
            "entries": [e.to_dict() for e in self.entries],
        }


@dataclass
class ValidationIssue:
    level: str                               # ERROR | WARNING
    entry_id: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StatusChange:
    entry_id: str
    from_status: str
    to_status: str
    reason: str = ""
    accepted: bool = True                     # False si la transición no es válida
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NewIdea:
    title: str
    section: str = Section.OPEN_IDEAS
    status: str = EntryStatus.IDEA
    priority: str = ""
    description: str = ""
    related: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BacklogProposal:
    """PROPUESTA de cambios tras un sprint. El DCA propone; el humano aprueba y edita el .md.

    Nunca modifica el documento. Es un artefacto auditable (output/dca/backlog/)."""

    sprint: str
    resolved: list[str] = field(default_factory=list)
    status_changes: list[StatusChange] = field(default_factory=list)
    new_ideas: list[NewIdea] = field(default_factory=list)
    related_to_add: list[dict] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sprint": self.sprint,
            "resolved": list(self.resolved),
            "status_changes": [c.to_dict() for c in self.status_changes],
            "new_ideas": [n.to_dict() for n in self.new_ideas],
            "related_to_add": list(self.related_to_add),
            "issues": [i.to_dict() for i in self.issues],
            "notes": list(self.notes),
            "requires_manual_approval": True,
        }
