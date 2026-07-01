"""FLASHBACK — insertar pasado (contexto/origen) después de presentar el presente."""

from app.nar.devices.base import BaseNarrativeDevice
from app.nar.models import NarrativeContext, NarrativeSegment
from app.nar.vocabulary import DeviceType
from app.nar.vocabulary import NarrativeBeat as B


class FlashbackDevice(BaseNarrativeDevice):
    device_type = DeviceType.FLASHBACK

    def applies(self, context, segments) -> tuple[bool, str]:
        incident_idx = next((s.index for s in segments
                             if s.beat in (B.INCITING_INCIDENT, B.HOOK)), -1)
        back = self._indices_with_beats(segments, {B.BACKGROUND, B.SETUP})
        later_back = [i for i in back if i > incident_idx] if incident_idx >= 0 else []
        if later_back:
            return True, "hay contexto posterior al incidente: se cuenta como flashback"
        return False, "el contexto ya precede al incidente: no se requiere flashback"

    def targets(self, context, segments) -> list[int]:
        incident_idx = next((s.index for s in segments
                             if s.beat in (B.INCITING_INCIDENT, B.HOOK)), -1)
        back = self._indices_with_beats(segments, {B.BACKGROUND, B.SETUP})
        return [i for i in back if i > incident_idx] if incident_idx >= 0 else []
