"""DOCUMENTARY_REVEAL — divulgación escalonada de evidencia decisiva (el "gran revelado").

Procede cuando hay revelaciones y materia que confrontar (conflictos o huecos): el documental
dosifica la evidencia hasta el momento de máximo impacto.
"""

from app.nar.devices.base import BaseNarrativeDevice
from app.nar.models import NarrativeContext, NarrativeSegment
from app.nar.vocabulary import DeviceType
from app.nar.vocabulary import NarrativeBeat as B


class DocumentaryRevealDevice(BaseNarrativeDevice):
    device_type = DeviceType.DOCUMENTARY_REVEAL

    def _reveal_indices(self, segments: list[NarrativeSegment]) -> list[int]:
        return self._indices_with_beats(segments, {B.REVELATION, B.TURNING_POINT, B.MIDPOINT})

    def applies(self, context, segments) -> tuple[bool, str]:
        reveals = self._reveal_indices(segments)
        if not reveals:
            return False, "no hay beats de revelación que dosificar"
        if context.conflict_count > 0 or context.missing_dimensions:
            return True, "hay materia que confrontar: la evidencia se dosifica hasta el revelado"
        return True, "hay revelaciones: se planifica una divulgación escalonada"

    def targets(self, context, segments) -> list[int]:
        return self._reveal_indices(segments)
