"""Estructura THREE_ACT — planteamiento, confrontación, desenlace.

La estructura dramática más universal. Idónea cuando existe un incidente desencadenante claro
y el material no exige una arquitectura más específica.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType


class ThreeActStructure(BaseNarrativeStructure):
    structure_type = StructureType.THREE_ACT

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.50, ["estructura dramática universal (base 0.50)"]
        if context.events:
            score += 0.15
            reasons.append("hay un incidente desencadenante identificable")
        if context.genre in ("generic", "history", "biography"):
            score += 0.10
            reasons.append(f"género '{context.genre}' encaja con tres actos")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        return self._skeleton([
            ("act_1_setup", [B.HOOK, B.SETUP, B.INCITING_INCIDENT]),
            ("act_2_confrontation", [B.RISING_ACTION, B.MIDPOINT, B.COMPLICATION]),
            ("act_3_resolution", [B.CLIMAX, B.FALLING_ACTION, B.RESOLUTION]),
        ])
