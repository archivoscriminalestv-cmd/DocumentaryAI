"""PARALLEL_NARRATIVES — sostener varias líneas (personas/lugares) en paralelo.

Procede cuando hay varios hilos reales (varias personas o varios lugares) que pueden avanzar
de forma entrelazada.
"""

from app.nar.devices.base import BaseNarrativeDevice
from app.nar.models import NarrativeContext, NarrativeSegment
from app.nar.vocabulary import DeviceType


class ParallelNarrativesDevice(BaseNarrativeDevice):
    device_type = DeviceType.PARALLEL_NARRATIVES

    def applies(self, context, segments) -> tuple[bool, str]:
        if len(context.people) >= 2:
            return True, f"{len(context.people)} personas: hilos paralelos posibles"
        if len(context.locations) >= 2:
            return True, f"{len(context.locations)} lugares: hilos paralelos posibles"
        return False, "un solo hilo dominante: no hay narrativas paralelas"

    def targets(self, context, segments) -> list[int]:
        return []
