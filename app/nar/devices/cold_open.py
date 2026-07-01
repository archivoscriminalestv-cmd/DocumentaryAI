"""COLD_OPEN — abrir con un fragmento de alto impacto antes de asentar el contexto."""

from app.nar.devices.base import BaseNarrativeDevice
from app.nar.models import NarrativeContext, NarrativeSegment
from app.nar.vocabulary import DeviceType, TensionLevel


class ColdOpenDevice(BaseNarrativeDevice):
    device_type = DeviceType.COLD_OPEN

    def _peak_index(self, segments: list[NarrativeSegment]) -> int:
        best, best_rank = -1, -1
        for s in segments:
            rank = TensionLevel.RANK.get(s.tension, 0)
            if rank > best_rank:
                best, best_rank = s.index, rank
        return best

    def applies(self, context, segments) -> tuple[bool, str]:
        if len(segments) < 3:
            return False, "documental demasiado corto para un cold open"
        peak = self._peak_index(segments)
        if peak <= 1:
            return False, "el pico ya está al inicio: no aporta cold open"
        if context.genre == "true_crime" or peak >= 0:
            return True, f"existe un pico de tensión en el segmento {peak}: se teasea al inicio"
        return False, "sin pico que adelantar"

    def targets(self, context, segments) -> list[int]:
        peak = self._peak_index(segments)
        return sorted({0, peak}) if peak > 1 else [0]
