"""Documentary Learning Engine (DLE) — Sprint DLE-001.

Motor de ADQUISICIÓN DE CONOCIMIENTO: observa documentales reales (YouTube o vídeo
local), extrae conocimiento cinematográfico ESTRUCTURADO y lo almacena de forma
permanente y versionada en ``knowledge/``. El DLE NO genera documentales y NO modifica
el pipeline de generación (VIS/VAI/CRE/CCE/ERE/VSC/VPL/ALR/SDE/CME/Composer/FFmpeg):
solo observa, analiza y almacena.

Provider-agnóstico (el origen del vídeo no afecta al análisis), determinista (mismas
entradas → mismo conocimiento), serializable y versionado. Nunca inventa: lo que no se
puede determinar con confianza se marca ``UNKNOWN``. Si un análisis falla, se registra
el error y se continúa.
"""

SCHEMA_VERSION = "1.0"
UNKNOWN = "UNKNOWN"

from app.dle.models import (
    AnalysisError,
    DocumentaryKnowledge,
    Metadata,
    NarrativeBlock,
    SceneSegment,
    ShotAnalysis,
    Statistics,
    Transcript,
    TranscriptSegment,
)
from app.dle.orchestrator import DocumentaryLearningEngine, VideoSource

__all__ = [
    "SCHEMA_VERSION",
    "UNKNOWN",
    "DocumentaryLearningEngine",
    "VideoSource",
    "DocumentaryKnowledge",
    "Metadata",
    "ShotAnalysis",
    "SceneSegment",
    "NarrativeBlock",
    "Statistics",
    "Transcript",
    "TranscriptSegment",
    "AnalysisError",
]
