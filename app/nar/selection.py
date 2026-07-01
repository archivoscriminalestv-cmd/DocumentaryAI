"""Selector de estructura narrativa (NAR-001).

NO contiene reglas de negocio narrativas: cada estructura se auto-puntúa (``fitness``). El
selector solo ordena las puntuaciones y elige la mejor, con un desempate determinista (orden
estable del registro). Así, añadir una estructura no toca este archivo. Sin ``if`` gigantes.
"""

from app.nar.models import NarrativeContext, StructureCandidate
from app.nar.strategies import default_structures


class StructureSelector:
    """Puntúa todas las estructuras y devuelve un ranking trazable."""

    def __init__(self, structures=None) -> None:
        self._structures = structures if structures is not None else default_structures()
        # Orden estable para desempates deterministas.
        self._order = {s.structure_type: i for i, s in enumerate(self._structures)}

    def rank(self, context: NarrativeContext) -> list[StructureCandidate]:
        candidates: list[StructureCandidate] = []
        for strat in self._structures:
            score, reasons = strat.fitness(context)
            candidates.append(StructureCandidate(
                structure=strat.structure_type, score=float(score), reasons=list(reasons)))
        # Mayor score primero; empate → orden estable del registro.
        candidates.sort(key=lambda c: (-c.score, self._order.get(c.structure, 999)))
        if candidates:
            candidates[0].selected = True
        return candidates

    def select(self, context: NarrativeContext):
        """Devuelve (estructura_elegida, ranking). La estructura es la instancia, no el string."""
        ranking = self.rank(context)
        chosen_type = ranking[0].structure if ranking else None
        strat = next((s for s in self._structures if s.structure_type == chosen_type), None)
        return strat, ranking
