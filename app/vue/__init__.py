"""Visual Understanding Engine (VUE) — Sprint VUE-001 (foundation).

Motor permanente que comprenderá el CONTENIDO visual de cada plano. En el futuro lo
usarán DLE/DKS/Production Advisor/VAI/Composer, pero en este sprint es COMPLETAMENTE
independiente y NO se integra con ninguno.

Principios (ver ADR-0015):
- Arquitectura modular: cada capacidad visual es un **detector** independiente
  (una responsabilidad). El orquestador solo coordina; nunca implementa lógica.
- Solo **hechos observables**: nunca inferencias, opiniones, IA generativa ni
  puntuaciones inventadas. **UNKNOWN antes que inventar**.
- Provider-agnóstico, determinista, serializable y versionado.

Este sprint NO implementa OpenCV/YOLO/Florence/GroundingDINO/Gemini/GPT Vision: solo la
arquitectura. Los detectores incluidos devuelven UNKNOWN (esqueleto) de forma determinista.
"""

SCHEMA_VERSION = "0.1"
UNKNOWN = "UNKNOWN"
NOT_IMPLEMENTED = "not_implemented"

from app.vue.interfaces import FrameRef, VisualDetector
from app.vue.models import (
    Composition,
    DetectedText,
    EmptySpace,
    EvidenceType,
    FaceLayout,
    LayoutBalance,
    ObjectDetection,
    SceneType,
    ShotSize,
    SubjectRegion,
    VisualAnalysis,
    VisualObservation,
    VisualWeight,
)
from app.vue.orchestrator import VisualUnderstandingEngine, default_detectors

__all__ = [
    "SCHEMA_VERSION",
    "UNKNOWN",
    "NOT_IMPLEMENTED",
    "FrameRef",
    "VisualDetector",
    "VisualObservation",
    "VisualAnalysis",
    "ShotSize",
    "Composition",
    "FaceLayout",
    "DetectedText",
    "EvidenceType",
    "SceneType",
    "ObjectDetection",
    "SubjectRegion",
    "LayoutBalance",
    "VisualWeight",
    "EmptySpace",
    "VisualUnderstandingEngine",
    "default_detectors",
]
