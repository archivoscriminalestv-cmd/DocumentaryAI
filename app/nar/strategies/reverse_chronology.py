"""Estructura REVERSE_CHRONOLOGY — se parte del desenlace y se retrocede.

Técnica avanzada: solo cobra sentido cuando el resultado es conocido (cronología completa) y
hay tensión que justifique recorrer el camino hacia atrás (conflictos). Nicho.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType, TimelineOrder


class ReverseChronologyStructure(BaseNarrativeStructure):
    structure_type = StructureType.REVERSE_CHRONOLOGY

    def timeline_order(self) -> str:
        return TimelineOrder.REVERSE

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.15, ["técnica avanzada de retroceso (base 0.15)"]
        if context.chronology_complete and context.conflict_count > 0 and context.genre == "true_crime":
            score += 0.35
            reasons.append("desenlace conocido + cronología completa + conflicto: el retroceso revela")
        else:
            reasons.append("faltan condiciones (cronología completa + conflicto + true_crime)")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        # Presentación en orden inverso al tiempo real.
        return self._skeleton([
            ("act_1_outcome", [B.HOOK, B.AFTERMATH]),
            ("act_2_unwinding", [B.REVELATION, B.TURNING_POINT, B.COMPLICATION]),
            ("act_3_origin", [B.INVESTIGATION, B.INCITING_INCIDENT, B.SETUP]),
        ])
