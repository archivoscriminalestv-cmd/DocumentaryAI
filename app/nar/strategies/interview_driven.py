"""Estructura INTERVIEW_DRIVEN — el testimonio sostiene el relato.

Requiere material de entrevista real. Si no consta cobertura de entrevistas, su idoneidad
permanece baja: el NAR NO inventa testimonios (UNKNOWN sobre inventar). Se usa un proxy
honesto (vídeo abundante + personas) declarado como tal.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType


class InterviewDrivenStructure(BaseNarrativeStructure):
    structure_type = StructureType.INTERVIEW_DRIVEN

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.10, ["relato testimonial (base 0.10)"]
        if context.is_complete("interviews"):
            score += 0.50
            reasons.append("cobertura de entrevistas COMPLETA: hay testimonios reales")
        elif context.count("videos") >= 10 and context.people:
            score += 0.15
            reasons.append("proxy: vídeo abundante + personas (entrevistas no confirmadas)")
        else:
            reasons.append("sin cobertura de entrevistas: idoneidad baja (no se inventan testimonios)")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        return self._skeleton([
            ("act_1_voices", [B.SETUP, B.INTRODUCE_SUBJECT]),
            ("act_2_testimony", [B.BACKGROUND, B.RISING_ACTION, B.COMPLICATION]),
            ("act_3_meaning", [B.REVELATION, B.REFLECTION, B.RESOLUTION]),
        ])
