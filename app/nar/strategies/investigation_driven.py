"""Estructura INVESTIGATION_DRIVEN — el procedimiento de investigación guía el relato.

Se avanza paso a paso siguiendo pistas y documentos. A diferencia de MYSTERY_INVESTIGATION
(centrada en el enigma y el impacto), aquí el método —seguir la evidencia— es el protagonista.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType


class InvestigationDrivenStructure(BaseNarrativeStructure):
    structure_type = StructureType.INVESTIGATION_DRIVEN

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.25, ["relato procedimental (base 0.25)"]
        if context.genre == "true_crime":
            score += 0.25
            reasons.append("género 'true_crime' admite estructura de investigación")
        if context.is_complete("news") or context.count("documents") > 0:
            score += 0.15
            reasons.append("hay prensa/documentos sobre los que articular el procedimiento")
        if context.recreation_candidates:
            score += 0.10
            reasons.append(f"{len(context.recreation_candidates)} candidatos de recreación apoyan los pasos")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        return self._skeleton([
            ("act_1_case_opens", [B.SETUP, B.INCITING_INCIDENT]),
            ("act_2_leads", [B.INVESTIGATION, B.CLUE, B.COMPLICATION, B.CLUE]),
            ("act_3_breakthrough", [B.TURNING_POINT, B.REVELATION]),
            ("act_4_status", [B.RESOLUTION, B.OPEN_QUESTION]),
        ])
