"""Narrative Intelligence Engine — el orquestador (NAR-001).

Coordina: elige estructura → expande beats a segmentos → asigna emoción, ritmo, evidencias,
mecanismos y narración → aplica dispositivos → construye los contratos para VIS. NO contiene
reglas narrativas propias: delega en estrategias y diseñadores. Determinista, sin red, sin IA.
"""

from app.nar import NAR_SCHEMA_VERSION
from app.nar.contracts import NarrativeDirective
from app.nar.devices import default_devices
from app.nar.emotion import EmotionCurveDesigner
from app.nar.interfaces import BeatPlan
from app.nar.models import (
    ActDefinition,
    KnowledgeProvenance,
    NarrationPurpose,
    NarrativeArc,
    NarrativeBlueprint,
    NarrativeContext,
    NarrativeSegment,
    NarrativeState,
    TimelineDecision,
    slugify,
)
from app.nar.pacing import PacingDesigner
from app.nar.placement import EvidencePlacementPlanner
from app.nar.beats import beat_profile
from app.nar.reveals import RevealScheduler
from app.nar.selection import StructureSelector
from app.nar.vocabulary import UNKNOWN, TensionLevel, TimelineOrder


class NarrativeIntelligenceEngine:
    """Construye un ``NarrativeBlueprint`` a partir de un ``NarrativeContext``."""

    def __init__(self, selector=None, emotion=None, pacing=None, placer=None,
                 scheduler=None, devices=None) -> None:
        self._selector = selector or StructureSelector()
        self._emotion = emotion or EmotionCurveDesigner()
        self._pacing = pacing or PacingDesigner()
        self._placer = placer or EvidencePlacementPlanner()
        self._scheduler = scheduler or RevealScheduler()
        self._devices = devices if devices is not None else default_devices()

    # ------------------------------------------------------------------
    def design(self, context: NarrativeContext) -> NarrativeBlueprint:
        structure, ranking = self._selector.select(context)
        skeleton = structure.build_skeleton(context)
        segments = self._build_segments(skeleton)

        # Diseñadores transversales.
        curve = self._emotion.design(context, segments)
        for seg in segments:
            dur, basis, pacing_intent = self._pacing.plan(context, seg)
            seg.suggested_duration_seconds = dur
            seg.duration_basis = basis
            seg.pacing_intent = pacing_intent

        questions = self._place_evidence(context, segments)
        schedule = self._scheduler.schedule(context, segments)
        questions = self._merge_questions(questions, schedule.viewer_questions)
        self._attach_questions(segments, questions)
        self._attach_mechanisms(segments, schedule)

        devices_applied = self._apply_devices(context, segments)
        self._build_directives(segments)
        states = self._narrative_states(segments, schedule.reveals, questions)
        timeline = self._timeline_decision(context, structure)
        arc = self._build_arc(structure.structure_type, segments)

        blueprint = NarrativeBlueprint(
            case_id=context.case_id, title=context.title, genre=context.genre,
            schema_version=NAR_SCHEMA_VERSION,
            structure=structure.structure_type,
            structure_reason=self._structure_reason(ranking),
            candidates=ranking, timeline_decision=timeline, arc=arc, segments=segments,
            emotion_curve=curve, devices_applied=devices_applied,
            hooks=schedule.hooks, foreshadows=schedule.foreshadows, reveals=schedule.reveals,
            cliffhangers=schedule.cliffhangers, payoffs=schedule.payoffs,
            viewer_questions=questions, narrative_states=states,
            provenance=self._provenance(context),
            totals=self._totals(segments, schedule, questions, curve),
            notes=self._notes(context),
        )
        return blueprint

    # ------------------------------------------------------------------
    def _build_segments(self, skeleton: list[BeatPlan]) -> list[NarrativeSegment]:
        segments: list[NarrativeSegment] = []
        for index, plan in enumerate(skeleton):
            profile = beat_profile(plan.beat)
            seg = NarrativeSegment(
                id=f"seg_{index:02d}_{slugify(plan.beat)}", index=index, beat=plan.beat,
                act_id=plan.act_key, purpose=plan.purpose or profile.purpose,
                emotion=profile.emotion, tension=profile.tension,
                narration=NarrationPurpose(mode=profile.narration_mode,
                                           intent=profile.narration_intent,
                                           reason=f"modo por defecto del beat '{plan.beat}'"),
                suggested_duration_seconds=profile.base_duration_seconds,
                pacing_intent=profile.pacing,
                emphasis=plan.emphasis or profile.emphasis)
            segments.append(seg)
        return segments

    def _place_evidence(self, context, segments) -> list:
        all_questions = []
        for seg in segments:
            placements, recreations, questions = self._placer.place(context, seg)
            seg.evidence = placements
            seg.recreations = recreations
            all_questions.extend(questions)
        return all_questions

    @staticmethod
    def _merge_questions(placer_questions, scheduler_questions) -> list:
        merged: dict[str, object] = {}
        for q in list(placer_questions) + list(scheduler_questions):
            existing = merged.get(q.id)
            if existing is None or q.opened_in < existing.opened_in:
                merged[q.id] = q
        return sorted(merged.values(), key=lambda q: (q.opened_in, q.id))

    @staticmethod
    def _attach_questions(segments, questions) -> None:
        by_index: dict[int, list[str]] = {}
        for q in questions:
            by_index.setdefault(q.opened_in, []).append(q.id)
        for seg in segments:
            seg.viewer_question_ids = sorted(by_index.get(seg.index, []))

    @staticmethod
    def _attach_mechanisms(segments, schedule) -> None:
        by_index: dict[int, list[str]] = {}
        for group in (schedule.hooks, schedule.foreshadows, schedule.reveals,
                      schedule.cliffhangers, schedule.payoffs):
            for m in group:
                by_index.setdefault(m.segment_index, []).append(m.id)
        for seg in segments:
            seg.mechanism_ids = sorted(by_index.get(seg.index, []))

    def _apply_devices(self, context, segments) -> list[dict]:
        applied: list[dict] = []
        for device in self._devices:
            ok, reason = device.applies(context, segments)
            if not ok:
                continue
            targets = device.targets(context, segments)
            device.apply(context, segments)
            applied.append({"type": device.device_type, "reason": reason,
                            "target_segments": sorted(targets)})
        return applied

    @staticmethod
    def _build_directives(segments) -> None:
        for seg in segments:
            seg.directive = NarrativeDirective(
                segment_id=seg.id, purpose=seg.purpose, emotion=seg.emotion,
                tension=seg.tension, pacing_intent=seg.pacing_intent,
                narration_mode=seg.narration.mode,
                suggested_duration_seconds=seg.suggested_duration_seconds,
                emphasis=seg.emphasis,
                evidence_dimensions=[e.dimension for e in seg.evidence],
                viewer_question_ids=list(seg.viewer_question_ids),
                mechanism_ids=list(seg.mechanism_ids),
                duration_basis=seg.duration_basis)

    @staticmethod
    def _narrative_states(segments, reveals, questions) -> list[NarrativeState]:
        total_reveals = len(reveals)
        states: list[NarrativeState] = []
        for seg in segments:
            revealed = sum(1 for r in reveals if r.segment_index <= seg.index)
            open_q = sum(1 for q in questions
                         if q.opened_in <= seg.index and (q.resolved_in < 0 or q.resolved_in > seg.index))
            states.append(NarrativeState(
                index=seg.index, segment_id=seg.id, revealed=revealed,
                pending_reveals=total_reveals - revealed, open_questions=open_q,
                tension=seg.tension, emotion=seg.emotion))
        return states

    @staticmethod
    def _timeline_decision(context, structure) -> TimelineDecision:
        order = structure.timeline_order()
        events = list(context.events)
        if order == TimelineOrder.REVERSE:
            events = list(reversed(events))
        reason = {
            TimelineOrder.CHRONOLOGICAL: "se respeta el orden de los hechos",
            TimelineOrder.REVERSE: "se cuenta desde el desenlace hacia el origen",
            TimelineOrder.NON_LINEAR: "se entrelazan hilos fuera del orden temporal",
            TimelineOrder.THEMATIC: "se agrupa por bloques de evidencia, no por tiempo",
        }.get(order, "orden por defecto")
        return TimelineDecision(order=order, reason=reason,
                                reordered=order != TimelineOrder.CHRONOLOGICAL,
                                event_order=events)

    @staticmethod
    def _build_arc(structure_type, segments) -> NarrativeArc:
        acts: list[ActDefinition] = []
        index_by_act: dict[str, int] = {}
        for seg in segments:
            if seg.act_id not in index_by_act:
                index_by_act[seg.act_id] = len(acts)
                acts.append(ActDefinition(id=seg.act_id, index=len(acts), key=seg.act_id))
            act = acts[index_by_act[seg.act_id]]
            act.beats.append(seg.beat)
            act.segment_ids.append(seg.id)
        return NarrativeArc(structure=structure_type, acts=acts,
                            beat_order=[s.beat for s in segments])

    @staticmethod
    def _structure_reason(ranking) -> str:
        if not ranking:
            return ""
        top = ranking[0]
        return f"{top.structure} (score {top.score}): " + "; ".join(top.reasons)

    @staticmethod
    def _provenance(context) -> KnowledgeProvenance:
        used, unknown = [], []
        pacing_value, _ = context.knowledge_value("storytelling", "pacing")
        if pacing_value != UNKNOWN:
            used.append("kbg:storytelling.pacing")
        for section, items in sorted(context.knowledge.items()):
            if items and all(str(i.get("value")) == UNKNOWN for i in items):
                unknown.append(f"kbg:{section}")
        return KnowledgeProvenance(
            inputs_present=list(context.inputs_present),
            inputs_missing=list(context.inputs_missing),
            knowledge_used=sorted(used), unknown_inputs=sorted(unknown))

    @staticmethod
    def _totals(segments, schedule, questions, curve) -> dict:
        peak = max((TensionLevel.RANK.get(s.tension, 0) for s in segments), default=0)
        return {
            "segments": len(segments),
            "total_suggested_seconds": round(sum(s.suggested_duration_seconds for s in segments), 1),
            "acts": len({s.act_id for s in segments}),
            "reveals": len(schedule.reveals),
            "hooks": len(schedule.hooks),
            "foreshadows": len(schedule.foreshadows),
            "cliffhangers": len(schedule.cliffhangers),
            "payoffs": len(schedule.payoffs),
            "viewer_questions": len(questions),
            "recreations": sum(len(s.recreations) for s in segments),
            "evidence_placements": sum(len(s.evidence) for s in segments),
            "tension_peak": TensionLevel.from_rank(peak),
            "arc_type": curve.arc_type if curve else UNKNOWN,
        }

    @staticmethod
    def _notes(context) -> list[str]:
        notes = ["NAR no escribe texto: produce el plano de CÓMO contar la historia."]
        if context.inputs_missing:
            notes.append("entradas ausentes: " + ", ".join(context.inputs_missing))
        if context.missing_dimensions:
            notes.append("huecos de cobertura → preguntas abiertas: "
                         + ", ".join(context.missing_dimensions))
        return notes
