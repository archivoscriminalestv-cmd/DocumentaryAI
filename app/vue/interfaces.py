"""Interfaces públicas del VUE.

Un fotograma se referencia de forma PROVIDER-AGNÓSTICA (``FrameRef``: ruta + índice +
timestamp), sin abrir píxeles aquí ni depender de OpenCV/PIL. Cada capacidad visual es un
``VisualDetector`` (Protocol). El orquestador solo conoce esta interfaz.
"""

from dataclasses import dataclass
from typing import Protocol

from app.vue.models import VisualObservation


@dataclass
class FrameRef:
    """Referencia a un fotograma. El cómo se obtuvo no afecta a la interfaz."""

    path: str = ""
    index: int = 0
    timestamp: float = 0.0
    frame_id: str = ""


class VisualDetector(Protocol):
    capability: str

    def detect(self, frame: FrameRef, context: dict | None = None) -> VisualObservation:
        """Devuelve un HECHO objetivo sobre ``frame`` (o UNKNOWN). Nunca interpreta."""
        ...
