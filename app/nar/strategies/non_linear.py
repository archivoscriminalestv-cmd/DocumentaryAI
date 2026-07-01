"""Estructura NON_LINEAR — hilos entrelazados fuera del orden cronológico.

Para casos con varios hilos fuertes y giros (varias dimensiones completas + hitos + conflicto).
Técnica avanzada; se apoya bien en dispositivos como flashback/parallel narratives.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType, TimelineOrder


class NonLinearStructure(BaseNarrativeStructure):
    structure_type = StructureType.NON_LINEAR

    def timeline_order(self) -> str:
        return TimelineOrder.NON_LINEAR

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.15, ["arquitectura entrelazada (base 0.15)"]
        if len(context.complete_dimensions) >= 5 and len(context.events) >= 3:
            score += 0.30
            reasons.append("múltiples hilos fuertes (≥5 dimensiones, ≥3 hitos)")
        if context.conflict_count >= 1:
            score += 0.10
            reasons.append("el conflicto justifica el salto entre hilos")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        return self._skeleton([
            ("act_1_threads_open", [B.HOOK, B.SETUP]),
            ("act_2_interleave", [B.INVESTIGATION, B.MIDPOINT, B.CLUE, B.COMPLICATION]),
            ("act_3_converge", [B.REVELATION, B.AFTERMATH, B.OPEN_QUESTION]),
        ])
