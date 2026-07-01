"""Programador de mecanismos narrativos (NAR-001).

Coloca los mecanismos de suspense a lo largo del relato: ganchos, presagios, revelaciones,
cliffhangers y pagos (payoffs), además de las preguntas abiertas que nacen de conflictos y de
los beats de incógnita. Todo determinista y trazable; cada pieza dice por qué está ahí.

Las preguntas por HUECOS de cobertura las genera el placement planner; aquí se generan las que
provienen de CONFLICTOS y de beats de pregunta. El motor las fusiona y deduplica.
"""

from app.nar.interfaces import ScheduleResult
from app.nar.models import (
    Cliffhanger,
    Foreshadow,
    Hook,
    NarrativeContext,
    NarrativeSegment,
    Payoff,
    Reveal,
    ViewerQuestion,
    slugify,
)
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import QuestionType, TensionLevel

_REVEAL_BEATS = {B.REVELATION, B.MIDPOINT, B.TURNING_POINT, B.CLIMAX, B.INCITING_INCIDENT}
_ANCHOR_BEATS = {B.HOOK, B.SETUP, B.BACKGROUND, B.INTRODUCE_SUBJECT}


class RevealScheduler:
    def schedule(self, context: NarrativeContext,
                 segments: list[NarrativeSegment]) -> ScheduleResult:
        result = ScheduleResult()
        primary = context.subject or context.title or context.case_id
        event_target = context.events[0] if context.events else primary

        # --- hooks ---
        for seg in segments:
            if seg.beat == B.HOOK:
                result.hooks.append(Hook(
                    id=f"hook_{seg.index}", segment_index=seg.index, target=primary,
                    reason="apertura diseñada para captar antes de asentar el contexto"))

        # --- reveals ---
        for seg in segments:
            if seg.beat in _REVEAL_BEATS:
                magnitude = self._magnitude(seg.tension)
                result.reveals.append(Reveal(
                    id=f"reveal_{seg.index}", segment_index=seg.index, target=event_target,
                    magnitude=magnitude,
                    reason=f"beat '{seg.beat}' con tensión {seg.tension}: punto de revelación"))

        # --- foreshadows + payoffs para reveals de alta magnitud ---
        for rev in result.reveals:
            if rev.magnitude != "HIGH":
                continue
            anchor = self._anchor_before(segments, rev.segment_index)
            if anchor >= 0:
                rev.foreshadowed_by = f"foreshadow_{anchor}_{rev.segment_index}"
                result.foreshadows.append(Foreshadow(
                    id=rev.foreshadowed_by, segment_index=anchor, target=rev.target,
                    pays_off_in=rev.segment_index,
                    reason=f"se siembra en el segmento {anchor} lo que se revela en {rev.segment_index}"))
            if rev.segment_index + 1 < len(segments):
                result.payoffs.append(Payoff(
                    id=f"payoff_{rev.segment_index}", segment_index=rev.segment_index + 1,
                    target=rev.target, resolves=rev.id,
                    reason="se asienta la consecuencia justo tras la revelación"))

        # --- cliffhangers en fronteras de acto (salvo el último) ---
        for idx in self._act_boundaries(segments)[:-1]:
            seg = segments[idx]
            if TensionLevel.RANK.get(seg.tension, 0) >= TensionLevel.RANK[TensionLevel.MEDIUM]:
                result.cliffhangers.append(Cliffhanger(
                    id=f"cliff_{idx}", segment_index=idx, target=event_target,
                    reason=f"fin de acto con tensión {seg.tension}: se deja en suspenso"))

        # --- preguntas: beats de incógnita + conflictos ---
        for seg in segments:
            if seg.beat == B.OPEN_QUESTION:
                result.viewer_questions.append(ViewerQuestion(
                    id=f"q_open_{seg.index}", type=QuestionType.WHY, target=primary,
                    origin="open_question_beat", opened_in=seg.index))
        for n, conflict in enumerate(context.conflicts[:3]):
            basis = str(conflict.get("basis", conflict.get("relation", "conflicto")))
            result.viewer_questions.append(ViewerQuestion(
                id=f"q_conflict_{n}", type=QuestionType.WHETHER, target=basis[:60],
                origin="conflict", opened_in=self._first_reveal_index(segments)))

        return result

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def _magnitude(tension: str) -> str:
        rank = TensionLevel.RANK.get(tension, 0)
        if rank >= TensionLevel.RANK[TensionLevel.PEAK]:
            return "HIGH"
        if rank >= TensionLevel.RANK[TensionLevel.HIGH]:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _anchor_before(segments: list[NarrativeSegment], before: int) -> int:
        anchor = -1
        for seg in segments:
            if seg.index < before and seg.beat in _ANCHOR_BEATS:
                anchor = seg.index
        return anchor

    @staticmethod
    def _act_boundaries(segments: list[NarrativeSegment]) -> list[int]:
        """Índice del último segmento de cada acto, en orden de aparición."""
        last_by_act: dict[str, int] = {}
        order: list[str] = []
        for seg in segments:
            if seg.act_id not in last_by_act:
                order.append(seg.act_id)
            last_by_act[seg.act_id] = seg.index
        return [last_by_act[a] for a in order]

    @staticmethod
    def _first_reveal_index(segments: list[NarrativeSegment]) -> int:
        for seg in segments:
            if seg.beat in _REVEAL_BEATS:
                return seg.index
        return 0
