"""Estructura FIVE_ACT — exposición, ascenso, clímax, caída, desenlace.

Para casos con suficientes hitos y material como para sostener una arquitectura más amplia.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType


class FiveActStructure(BaseNarrativeStructure):
    structure_type = StructureType.FIVE_ACT

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.35, ["arquitectura amplia (base 0.35)"]
        if len(context.events) >= 4:
            score += 0.20
            reasons.append(f"{len(context.events)} hitos: suficientes para cinco actos")
        if context.total_discovered >= 40:
            score += 0.10
            reasons.append(f"material abundante ({context.total_discovered} evidencias)")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        return self._skeleton([
            ("act_1_exposition", [B.SETUP, B.INTRODUCE_SUBJECT]),
            ("act_2_rising", [B.INCITING_INCIDENT, B.RISING_ACTION]),
            ("act_3_climax", [B.MIDPOINT, B.CLIMAX]),
            ("act_4_falling", [B.COMPLICATION, B.FALLING_ACTION]),
            ("act_5_denouement", [B.RESOLUTION, B.REFLECTION]),
        ])
