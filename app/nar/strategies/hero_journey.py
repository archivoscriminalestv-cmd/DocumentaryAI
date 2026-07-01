"""Estructura HERO_JOURNEY — el viaje del protagonista (mundo ordinario → llamada → prueba →
retorno). Idónea para biografías con un sujeto central claro.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType


class HeroJourneyStructure(BaseNarrativeStructure):
    structure_type = StructureType.HERO_JOURNEY

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.20, ["arco de transformación personal (base 0.20)"]
        if context.genre == "biography":
            score += 0.45
            reasons.append("género 'biography': el viaje del héroe es su forma natural")
        if context.subject or context.people:
            score += 0.15
            reasons.append("hay un sujeto central sobre el que articular el viaje")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        return self._skeleton([
            ("act_ordinary_world", [B.INTRODUCE_SUBJECT, B.CALL_TO_ADVENTURE]),
            ("act_trials", [B.THRESHOLD, B.RISING_ACTION, B.ORDEAL]),
            ("act_return", [B.REWARD, B.RETURN, B.REFLECTION]),
        ])
