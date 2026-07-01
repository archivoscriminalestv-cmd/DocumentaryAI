"""Estructura EVIDENCE_DRIVEN — el documental se organiza alrededor de la evidencia disponible.

Idónea cuando muchas dimensiones de cobertura están COMPLETAS: cada bloque de evidencia real
articula un tramo. Es temática más que cronológica (cada tramo agrupa material afín).
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType, TimelineOrder


class EvidenceDrivenStructure(BaseNarrativeStructure):
    structure_type = StructureType.EVIDENCE_DRIVEN

    def timeline_order(self) -> str:
        return TimelineOrder.THEMATIC

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.20, ["relato apoyado en evidencia real (base 0.20)"]
        complete = len(context.complete_dimensions)
        if complete >= 4:
            score += 0.30
            reasons.append(f"{complete} dimensiones con evidencia real COMPLETA")
        if context.total_discovered >= 40:
            score += 0.15
            reasons.append(f"material abundante ({context.total_discovered} evidencias)")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        # Un tramo de investigación por bloque de evidencia real (acotado 2..5), determinista.
        blocks = max(2, min(5, len(context.complete_dimensions) or 2))
        middle = []
        pattern = [B.INVESTIGATION, B.CLUE]
        for i in range(blocks):
            middle.append(pattern[i % len(pattern)])
        return self._skeleton([
            ("act_1_premise", [B.SETUP, B.INCITING_INCIDENT]),
            ("act_2_evidence", middle),
            ("act_3_synthesis", [B.MIDPOINT, B.REVELATION]),
            ("act_4_close", [B.RESOLUTION]),
        ])
