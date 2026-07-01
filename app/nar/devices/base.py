"""Base de los dispositivos narrativos (NAR-001).

Un dispositivo es una técnica que se aplica SOBRE una estructura ya construida (cold open,
flashback, parallel narratives…). Decide objetivamente si procede y, en su caso, anota los
segmentos afectados. En esta fundación los dispositivos ANOTAN (énfasis + segmentos objetivo)
y registran su decisión; la reescritura estructural profunda se reserva a sprints posteriores.
"""

from app.nar.models import NarrativeContext, NarrativeSegment


class BaseNarrativeDevice:
    device_type: str = ""

    def applies(self, context: NarrativeContext,
                segments: list[NarrativeSegment]) -> tuple[bool, str]:
        raise NotImplementedError

    def targets(self, context: NarrativeContext,
                segments: list[NarrativeSegment]) -> list[int]:
        """Índices de segmentos afectados (para trazabilidad). Por defecto, ninguno."""
        return []

    def apply(self, context: NarrativeContext,
              segments: list[NarrativeSegment]) -> list[NarrativeSegment]:
        """Anota los segmentos objetivo (énfasis alto) y devuelve la lista. Determinista."""
        for i in self.targets(context, segments):
            if 0 <= i < len(segments):
                segments[i].emphasis = "HIGH"
        return segments

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def _indices_with_beats(segments: list[NarrativeSegment], beats: set) -> list[int]:
        return [s.index for s in segments if s.beat in beats]
