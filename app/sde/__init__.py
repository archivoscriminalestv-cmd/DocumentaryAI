"""Shot Diversity Engine (SDE) — Sprint SDE-001.

Director de Fotografía determinista. Recibe un ``ShotExecutionRequest`` (VAI) y
devuelve otro ENRIQUECIDO con una composición cinematográfica diferente cuando la
narrativa lo permite, recordando todos los planos del documental.

NO genera imágenes, NO genera prompts completos, NO llama al VPL, NO toca Motion ni
Composer. Único punto de integración:  VIS → VAI → **SDE** → VSC.

100% determinista: sin ``random`` y sin dependencia del proveedor de imágenes. El
mismo documental produce siempre el mismo plan visual. Las decisiones se basan en
reglas, historial y contexto narrativo, y SIEMPRE se justifican.
"""

SCHEMA_VERSION = "1.0"

from app.sde.history import ShotHistory
from app.sde.models import ShotFingerprint, ShotRecord
from app.sde.orchestrator import SDEContext, ShotDiversityEngine

__all__ = [
    "SCHEMA_VERSION",
    "ShotDiversityEngine",
    "SDEContext",
    "ShotHistory",
    "ShotFingerprint",
    "ShotRecord",
]
