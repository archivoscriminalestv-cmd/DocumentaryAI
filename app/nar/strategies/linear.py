"""Estructura LINEAR — el relato sigue el orden cronológico de los hechos.

Es el suelo seguro: siempre viable. Gana fuerza cuando la cronología está completa y el
género favorece la exposición ordenada (historia, naturaleza, biografía).
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType


class LinearStructure(BaseNarrativeStructure):
    structure_type = StructureType.LINEAR

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.40, ["estructura universal y segura (base 0.40)"]
        if context.chronology_complete:
            score += 0.15
            reasons.append("cronología completa: el orden lineal es fiel a los hechos")
        if context.genre in ("history", "nature", "biography"):
            score += 0.15
            reasons.append(f"género '{context.genre}' favorece la exposición ordenada")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        return self._skeleton([
            ("act_setup", [B.SETUP, B.INTRODUCE_SUBJECT, B.BACKGROUND]),
            ("act_development", [B.INCITING_INCIDENT, B.RISING_ACTION, B.COMPLICATION]),
            ("act_outcome", [B.CLIMAX, B.FALLING_ACTION, B.RESOLUTION]),
        ])
