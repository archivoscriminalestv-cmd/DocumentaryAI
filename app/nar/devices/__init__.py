"""Registro de dispositivos narrativos (NAR-001).

Añadir un dispositivo nuevo = una clase más aquí; el orquestador no cambia.
"""

from app.nar.devices.base import BaseNarrativeDevice
from app.nar.devices.cold_open import ColdOpenDevice
from app.nar.devices.documentary_reveal import DocumentaryRevealDevice
from app.nar.devices.flashback import FlashbackDevice
from app.nar.devices.flashforward import FlashforwardDevice
from app.nar.devices.parallel_narratives import ParallelNarrativesDevice


def default_devices() -> list[BaseNarrativeDevice]:
    """Dispositivos disponibles, en orden estable de evaluación (determinista)."""
    return [
        ColdOpenDevice(),
        DocumentaryRevealDevice(),
        FlashbackDevice(),
        FlashforwardDevice(),
        ParallelNarrativesDevice(),
    ]


__all__ = [
    "default_devices",
    "BaseNarrativeDevice",
    "ColdOpenDevice",
    "DocumentaryRevealDevice",
    "FlashbackDevice",
    "FlashforwardDevice",
    "ParallelNarrativesDevice",
]
