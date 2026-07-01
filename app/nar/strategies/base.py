"""Base de las estrategias narrativas (NAR-001).

Una estrategia SOLO sabe dos cosas: (1) cuán idónea es para un caso (``fitness``, objetiva y
trazable) y (2) qué orden de beats propone (``build_skeleton``). NO asigna emoción, evidencias
ni duración: de eso se encargan los diseñadores. Así cada estructura es pequeña, aislada y
sustituible — sin ``if`` gigantes en el motor.
"""

from app.nar.interfaces import BeatPlan
from app.nar.models import NarrativeContext
from app.nar.vocabulary import TimelineOrder


class BaseNarrativeStructure:
    """Clase base concreta. Las subclases definen ``structure_type``, ``fitness`` y beats."""

    structure_type: str = ""

    # --- API que el motor usa --------------------------------------------
    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        raise NotImplementedError

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        raise NotImplementedError

    def timeline_order(self) -> str:
        """Orden temporal por defecto. Las estructuras no lineales lo redefinen."""
        return TimelineOrder.CHRONOLOGICAL

    # --- helpers compartidos ---------------------------------------------
    @staticmethod
    def _skeleton(acts: list[tuple[str, list[str]]]) -> list[BeatPlan]:
        """Convierte [(act_key, [beats])] en una lista plana de BeatPlan con índice de acto."""
        plans: list[BeatPlan] = []
        for act_index, (act_key, beats) in enumerate(acts):
            for beat in beats:
                plans.append(BeatPlan(beat=beat, act_key=act_key, act_index=act_index))
        return plans

    @staticmethod
    def _clamp(score: float) -> float:
        return round(max(0.0, min(1.0, score)), 4)
