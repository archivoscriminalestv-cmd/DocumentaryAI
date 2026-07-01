"""FLASHFORWARD — adelantar un atisbo del desenlace para crear expectación."""

from app.nar.devices.base import BaseNarrativeDevice
from app.nar.models import NarrativeContext, NarrativeSegment
from app.nar.vocabulary import DeviceType
from app.nar.vocabulary import NarrativeBeat as B


class FlashforwardDevice(BaseNarrativeDevice):
    device_type = DeviceType.FLASHFORWARD

    def _revelation_index(self, segments: list[NarrativeSegment]) -> int:
        idxs = self._indices_with_beats(segments, {B.REVELATION, B.CLIMAX, B.TURNING_POINT})
        return idxs[-1] if idxs else -1

    def applies(self, context, segments) -> tuple[bool, str]:
        rev = self._revelation_index(segments)
        if rev <= 1:
            return False, "no hay desenlace alejado del inicio que adelantar"
        if context.genre in ("true_crime",):
            return True, f"se atisba el desenlace (segmento {rev}) al comienzo"
        return False, "género sin tradición de flashforward documental"

    def targets(self, context, segments) -> list[int]:
        rev = self._revelation_index(segments)
        return sorted({0, rev}) if rev > 1 else []
