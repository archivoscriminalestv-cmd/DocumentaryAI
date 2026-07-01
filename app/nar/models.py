"""Estructuras del Narrative Intelligence Engine (NAR-001).

Todo el "plano de la historia" como DATOS: tipados, serializables, deterministas, sin
timestamps y sin prosa. El NAR produce un ``NarrativeBlueprint`` —nunca un guion— compuesto
por estas piezas. Cada decisión lleva un ``reason`` objetivo (trazabilidad), y cuando no hay
base se marca ``UNKNOWN`` (nunca se inventa).

Incluye también ``NarrativeContext``: la entrada YA NORMALIZADA (capa anticorrupción). El NAR
nunca depende de las clases internas de otros motores; ``inputs.py`` traduce sus JSON a este
contexto.
"""

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

from app.nar import NAR_SCHEMA_VERSION
from app.nar.contracts import NAR_DECIDES, NAR_DELEGATES, NarrativeDirective
from app.nar.vocabulary import UNKNOWN


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii").lower()
    slug = "".join(ch if ch.isalnum() else "_" for ch in norm)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "x"


# ===========================================================================
# ENTRADA NORMALIZADA (capa anticorrupción)
# ===========================================================================

@dataclass
class CoverageDimension:
    """Una dimensión del coverage report del ECE (p.ej. photographs, maps, news…)."""

    name: str
    required: int = 0
    discovered: int = 0
    state: str = "MISSING"            # COMPLETE | PARTIAL | MISSING
    evidence_ids: list[str] = field(default_factory=list)
    detail: dict = field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        return self.state == "COMPLETE"

    @property
    def is_missing(self) -> bool:
        return self.state == "MISSING"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RecreationCandidate:
    """Candidato a recreación detectado por el ECE (solo donde NO hay evidencia real)."""

    category: str
    existing_coverage: str = "MISSING"
    factual_basis: dict = field(default_factory=dict)
    available_evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NarrativeContext:
    """Entrada única y NORMALIZADA del NAR. Decide CÓMO contar a partir de hechos objetivos."""

    case_id: str
    title: str = ""
    genre: str = "generic"
    subject: str = ""
    people: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    time_period: str = ""
    coverage: dict[str, CoverageDimension] = field(default_factory=dict)
    conflicts: list[dict] = field(default_factory=list)
    graph_nodes: list[dict] = field(default_factory=list)
    graph_relations: list[dict] = field(default_factory=list)
    recreation_candidates: list[RecreationCandidate] = field(default_factory=list)
    timeline_events: list[str] = field(default_factory=list)
    knowledge: dict = field(default_factory=dict)          # secciones KBG (raw)
    inputs_present: list[str] = field(default_factory=list)
    inputs_missing: list[str] = field(default_factory=list)

    # --- señales objetivas (sin opinión) -----------------------------------
    def dimension(self, name: str) -> CoverageDimension | None:
        return self.coverage.get(name)

    def count(self, name: str) -> int:
        dim = self.coverage.get(name)
        return dim.discovered if dim else 0

    def is_complete(self, name: str) -> bool:
        dim = self.coverage.get(name)
        return bool(dim and dim.is_complete)

    def is_missing(self, name: str) -> bool:
        dim = self.coverage.get(name)
        return dim is None or dim.is_missing

    @property
    def total_discovered(self) -> int:
        return sum(d.discovered for d in self.coverage.values())

    @property
    def complete_dimensions(self) -> list[str]:
        return sorted(n for n, d in self.coverage.items() if d.is_complete)

    @property
    def missing_dimensions(self) -> list[str]:
        return sorted(n for n, d in self.coverage.items() if d.is_missing)

    @property
    def conflict_count(self) -> int:
        return len(self.conflicts)

    @property
    def chronology_complete(self) -> bool:
        return self.is_complete("chronology")

    def recreation_for(self, category: str) -> RecreationCandidate | None:
        for rc in self.recreation_candidates:
            if rc.category == category:
                return rc
        return None

    def knowledge_value(self, section: str, key: str):
        """Devuelve (value, confidence) de una clave del Generation Knowledge (KBG).

        UNKNOWN si no existe o si el corpus no la sintetiza (nunca inventa)."""
        for item in self.knowledge.get(section, []) or []:
            if item.get("key") == key:
                return item.get("value", UNKNOWN), float(item.get("confidence", 0.0) or 0.0)
        return UNKNOWN, 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "title": self.title,
            "genre": self.genre,
            "subject": self.subject,
            "people": list(self.people),
            "locations": list(self.locations),
            "events": list(self.events),
            "time_period": self.time_period,
            "coverage": {k: v.to_dict() for k, v in sorted(self.coverage.items())},
            "conflict_count": self.conflict_count,
            "recreation_candidates": [r.to_dict() for r in self.recreation_candidates],
            "timeline_events": list(self.timeline_events),
            "inputs_present": list(self.inputs_present),
            "inputs_missing": list(self.inputs_missing),
        }


# ===========================================================================
# SALIDA: piezas del blueprint
# ===========================================================================

@dataclass
class EvidencePlacement:
    """POR QUÉ una evidencia aparece aquí. Referencia la dimensión, nunca el contenido."""

    dimension: str                     # photographs | maps | news | documents | videos | chronology…
    use: str                           # EvidenceUse
    reason: str
    coverage_state: str = "MISSING"
    available: int = 0
    evidence_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RecreationPlacement:
    """Recreación justificada SOLO donde la evidencia real falta (prioridad: evidencia real)."""

    category: str
    reason: str
    justified_by: str = "missing_real_evidence"
    factual_basis: dict = field(default_factory=dict)
    allowed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ViewerQuestion:
    """Pregunta abierta ESTRUCTURADA (tipo + objetivo), no una frase escrita."""

    id: str
    type: str                          # QuestionType
    target: str                        # entidad/evento del caso
    origin: str                        # missing_coverage:* | conflict | open_event
    opened_in: int = -1                # índice de segmento donde se plantea
    resolved_in: int = -1              # -1 si queda abierta a propósito

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NarrationPurpose:
    """El MODO e INTENCIÓN de la narración del segmento (jamás el texto)."""

    mode: str                          # NarrationMode
    intent: str                        # NarrationIntent
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# --- mecanismos de suspense/estructura (cada uno una pieza nombrada) --------

@dataclass
class Hook:
    id: str
    segment_index: int
    target: str
    reason: str = ""
    kind: str = "HOOK"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Foreshadow:
    id: str
    segment_index: int
    target: str
    pays_off_in: int = -1
    reason: str = ""
    kind: str = "FORESHADOW"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Reveal:
    id: str
    segment_index: int
    target: str
    magnitude: str = "MEDIUM"          # LOW | MEDIUM | HIGH
    foreshadowed_by: str = ""
    reason: str = ""
    kind: str = "REVEAL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Cliffhanger:
    id: str
    segment_index: int
    target: str
    reason: str = ""
    kind: str = "CLIFFHANGER"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Payoff:
    id: str
    segment_index: int
    target: str
    resolves: str = ""
    reason: str = ""
    kind: str = "PAYOFF"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EmotionPoint:
    index: int
    segment_id: str
    emotion: str
    tension: str
    intensity: float = 0.0             # 0..1, derivado del rank de tensión

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EmotionCurve:
    arc_type: str
    points: list[EmotionPoint] = field(default_factory=list)
    peak_index: int = -1
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "arc_type": self.arc_type,
            "peak_index": self.peak_index,
            "summary": self.summary,
            "points": [p.to_dict() for p in self.points],
        }


@dataclass
class TimelineDecision:
    order: str                         # TimelineOrder
    reason: str
    reordered: bool = False
    event_order: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ActDefinition:
    id: str
    index: int
    key: str                           # clave de vocabulario (no prosa): act_setup, act_rising…
    beats: list[str] = field(default_factory=list)
    segment_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NarrativeArc:
    structure: str                     # StructureType
    acts: list[ActDefinition] = field(default_factory=list)
    beat_order: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "structure": self.structure,
            "beat_order": list(self.beat_order),
            "acts": [a.to_dict() for a in self.acts],
        }


@dataclass
class NarrativeState:
    """Lo que el ESPECTADOR sabe en cada punto: hace observable el 'qué ocultar / cuándo revelar'."""

    index: int
    segment_id: str
    revealed: int = 0                  # acumulado de revelaciones hasta aquí
    pending_reveals: int = 0           # revelaciones aún ocultas
    open_questions: int = 0            # preguntas abiertas vivas
    tension: str = "NONE"
    emotion: str = "NEUTRAL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NarrativeSegment:
    """Unidad del relato. NO contiene texto: define propósito, emoción y uso de material."""

    id: str
    index: int
    beat: str
    act_id: str
    purpose: str
    emotion: str
    tension: str
    narration: NarrationPurpose
    suggested_duration_seconds: float
    pacing_intent: str
    emphasis: str = "NORMAL"
    duration_basis: str = ""
    evidence: list[EvidencePlacement] = field(default_factory=list)
    recreations: list[RecreationPlacement] = field(default_factory=list)
    viewer_question_ids: list[str] = field(default_factory=list)
    mechanism_ids: list[str] = field(default_factory=list)
    directive: NarrativeDirective | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "index": self.index,
            "beat": self.beat,
            "act_id": self.act_id,
            "purpose": self.purpose,
            "emotion": self.emotion,
            "tension": self.tension,
            "narration": self.narration.to_dict(),
            "suggested_duration_seconds": self.suggested_duration_seconds,
            "pacing_intent": self.pacing_intent,
            "emphasis": self.emphasis,
            "duration_basis": self.duration_basis,
            "evidence": [e.to_dict() for e in self.evidence],
            "recreations": [r.to_dict() for r in self.recreations],
            "viewer_question_ids": list(self.viewer_question_ids),
            "mechanism_ids": list(self.mechanism_ids),
            "directive": self.directive.to_dict() if self.directive else None,
        }


@dataclass
class StructureCandidate:
    """Traza de la selección: cada estructura puntuada con sus razones objetivas."""

    structure: str
    score: float
    reasons: list[str] = field(default_factory=list)
    selected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KnowledgeProvenance:
    """De dónde salió cada decisión (qué entradas se usaron y cuáles faltaban)."""

    inputs_present: list[str] = field(default_factory=list)
    inputs_missing: list[str] = field(default_factory=list)
    knowledge_used: list[str] = field(default_factory=list)
    unknown_inputs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NarrativeBlueprint:
    """EL PLANO COMPLETO de la historia. No es un guion: es cómo debe contarse."""

    case_id: str
    title: str = ""
    genre: str = "generic"
    schema_version: str = NAR_SCHEMA_VERSION
    structure: str = ""
    structure_reason: str = ""
    candidates: list[StructureCandidate] = field(default_factory=list)
    timeline_decision: TimelineDecision | None = None
    arc: NarrativeArc | None = None
    segments: list[NarrativeSegment] = field(default_factory=list)
    emotion_curve: EmotionCurve | None = None
    devices_applied: list[dict] = field(default_factory=list)
    hooks: list[Hook] = field(default_factory=list)
    foreshadows: list[Foreshadow] = field(default_factory=list)
    reveals: list[Reveal] = field(default_factory=list)
    cliffhangers: list[Cliffhanger] = field(default_factory=list)
    payoffs: list[Payoff] = field(default_factory=list)
    viewer_questions: list[ViewerQuestion] = field(default_factory=list)
    narrative_states: list[NarrativeState] = field(default_factory=list)
    totals: dict = field(default_factory=dict)
    provenance: KnowledgeProvenance | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def directives(self) -> list[NarrativeDirective]:
        return [s.directive for s in self.segments if s.directive]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "case_id": self.case_id,
            "title": self.title,
            "genre": self.genre,
            "structure": self.structure,
            "structure_reason": self.structure_reason,
            "candidates": [c.to_dict() for c in self.candidates],
            "timeline_decision": self.timeline_decision.to_dict() if self.timeline_decision else None,
            "arc": self.arc.to_dict() if self.arc else None,
            "segments": [s.to_dict() for s in self.segments],
            "emotion_curve": self.emotion_curve.to_dict() if self.emotion_curve else None,
            "devices_applied": list(self.devices_applied),
            "mechanisms": {
                "hooks": [h.to_dict() for h in self.hooks],
                "foreshadows": [f.to_dict() for f in self.foreshadows],
                "reveals": [r.to_dict() for r in self.reveals],
                "cliffhangers": [c.to_dict() for c in self.cliffhangers],
                "payoffs": [p.to_dict() for p in self.payoffs],
            },
            "viewer_questions": [q.to_dict() for q in self.viewer_questions],
            "narrative_states": [s.to_dict() for s in self.narrative_states],
            "directives": [d.to_dict() for d in self.directives],
            "totals": self.totals,
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "boundaries": {"nar_decides": list(NAR_DECIDES), "nar_delegates": dict(NAR_DELEGATES)},
            "notes": list(self.notes),
        }
