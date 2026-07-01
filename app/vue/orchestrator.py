"""VisualUnderstandingEngine — coordina detectores (VUE-001).

SOLO coordina: ejecuta cada ``VisualDetector`` sobre un ``FrameRef`` y reúne sus
``VisualObservation`` en un ``VisualAnalysis``. Nunca implementa lógica de detección. Si
un detector falla, registra el error y continúa (devuelve UNKNOWN para esa capacidad);
nunca rompe el análisis. Determinista: el orden de los detectores se conserva.
"""

import logging

from app.vue import NOT_IMPLEMENTED, UNKNOWN
from app.vue.cv_detectors import classical_detectors
from app.vue.layout_detectors import layout_detectors
from app.vue.detectors import (
    DocumentDetector,
    EvidenceDetector,
    FaceLayoutDetector,
    MapDetector,
    ObjectDetector,
    SceneTypeDetector,
    ShotSizeDetector,
    TextDetector,
)
from app.vue.interfaces import FrameRef, VisualDetector
from app.vue.models import VisualAnalysis, VisualObservation


def default_detectors() -> list[VisualDetector]:
    """Conjunto estándar de detectores (orden estable y determinista).

    VUE-002: visión clásica real (composición/color/bordes/movimiento/geometría) +
    los detectores aún-esqueleto de capacidades futuras (devuelven UNKNOWN).
    """
    return [
        *classical_detectors(),     # composition (real), color, edge_density, motion_energy, frame_geometry
        *layout_detectors(),        # subject_localization, layout_balance, visual_weight, empty_space
        ShotSizeDetector(), FaceLayoutDetector(), TextDetector(), EvidenceDetector(),
        SceneTypeDetector(), ObjectDetector(), MapDetector(), DocumentDetector(),
    ]


class VisualUnderstandingEngine:
    def __init__(self, detectors: list[VisualDetector] | None = None, *, logger=None) -> None:
        self._detectors = list(detectors) if detectors is not None else default_detectors()
        self._log = logger or logging.getLogger("vue")

    @property
    def detectors(self) -> list[VisualDetector]:
        return list(self._detectors)

    def register(self, detector: VisualDetector) -> None:
        self._detectors.append(detector)

    def analyze(self, frame: FrameRef, context: dict | None = None) -> VisualAnalysis:
        analysis = VisualAnalysis(
            frame_id=frame.frame_id or frame.path, frame_index=frame.index,
            timestamp=frame.timestamp)
        for detector in self._detectors:
            capability = getattr(detector, "capability", type(detector).__name__)
            try:
                observation = detector.detect(frame, context)
            except Exception as exc:  # noqa: BLE001 — un detector no rompe el análisis
                self._log.warning("VUE detector '%s' falló: %s", capability, exc)
                analysis.errors.append({"detector": capability, "error": str(exc)})
                observation = VisualObservation(
                    detector=type(detector).__name__, capability=capability,
                    value=UNKNOWN, confidence=None, method=NOT_IMPLEMENTED,
                    facts={"error": str(exc)})
            analysis.observations.append(observation)
        return analysis

    def analyze_many(self, frames: list[FrameRef], context: dict | None = None) -> list[VisualAnalysis]:
        return [self.analyze(f, context) for f in frames]
