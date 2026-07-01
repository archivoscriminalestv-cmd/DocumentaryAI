"""Estructura MYSTERY_INVESTIGATION — el misterio como motor.

Plantea un enigma, investiga, siembra pistas y falsas pistas, revela y deja preguntas. Idónea
para true crime, especialmente con versiones en conflicto y huecos de cobertura que sostienen
la incógnita.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import StructureType


class MysteryInvestigationStructure(BaseNarrativeStructure):
    structure_type = StructureType.MYSTERY_INVESTIGATION

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        score, reasons = 0.25, ["arquitectura de enigma (base 0.25)"]
        if context.genre == "true_crime":
            score += 0.40
            reasons.append("género 'true_crime': el misterio es su forma natural")
        if context.conflict_count > 0:
            score += 0.15
            reasons.append(f"{context.conflict_count} conflicto(s): hay versiones que confrontar")
        if context.missing_dimensions:
            score += 0.10
            reasons.append(f"{len(context.missing_dimensions)} huecos abiertos sostienen la incógnita")
        return self._clamp(score), reasons

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        return self._skeleton([
            ("act_1_enigma", [B.HOOK, B.SETUP, B.INTRODUCE_SUBJECT]),
            ("act_2_investigation", [B.INCITING_INCIDENT, B.INVESTIGATION, B.CLUE,
                                     B.COMPLICATION, B.RED_HERRING]),
            ("act_3_revelation", [B.TURNING_POINT, B.REVELATION]),
            ("act_4_aftermath", [B.AFTERMATH, B.OPEN_QUESTION]),
        ])
