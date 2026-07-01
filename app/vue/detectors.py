"""Detectores del VUE — esqueleto (VUE-001).

Un detector = una responsabilidad. En este sprint NINGUNO implementa visión por
computador: todos devuelven ``UNKNOWN`` de forma determinista (``method=not_implemented``),
demostrando la arquitectura. Cada uno se sustituirá en el futuro por una implementación
real (OpenCV/YOLO/Florence/…) SIN cambiar la interfaz ni el orquestador.
"""

from app.vue import NOT_IMPLEMENTED, UNKNOWN
from app.vue.interfaces import FrameRef
from app.vue.models import (
    DetectedText,
    FaceLayout,
    ObjectDetection,
    VisualObservation,
)


class _BaseUnknownDetector:
    """Base: devuelve una observación UNKNOWN objetiva (sin inventar nada)."""

    capability = "base"

    def _facts(self) -> dict:
        return {}

    def detect(self, frame: FrameRef, context: dict | None = None) -> VisualObservation:
        return VisualObservation(
            detector=type(self).__name__, capability=self.capability,
            value=UNKNOWN, confidence=None, facts=self._facts(), method=NOT_IMPLEMENTED)


class ShotSizeDetector(_BaseUnknownDetector):
    capability = "shot_size"


class CompositionDetector(_BaseUnknownDetector):
    capability = "composition"


class SceneTypeDetector(_BaseUnknownDetector):
    capability = "scene_type"


class EvidenceDetector(_BaseUnknownDetector):
    capability = "evidence"


class MapDetector(_BaseUnknownDetector):
    capability = "map"


class DocumentDetector(_BaseUnknownDetector):
    capability = "document"


class FaceLayoutDetector(_BaseUnknownDetector):
    capability = "face_layout"

    def _facts(self) -> dict:
        return FaceLayout(face_count=None, note=NOT_IMPLEMENTED).to_dict()


class TextDetector(_BaseUnknownDetector):
    capability = "text"

    def _facts(self) -> dict:
        return DetectedText(present=UNKNOWN, note=NOT_IMPLEMENTED).to_dict()


class ObjectDetector(_BaseUnknownDetector):
    capability = "object"

    def _facts(self) -> dict:
        return ObjectDetection(objects=[], note=NOT_IMPLEMENTED).to_dict()
