"""Narrative Intelligence Engine (NAR) — el DIRECTOR NARRATIVO de DocumentaryAI.

Decide CÓMO contar una historia documental: estructura, orden, ritmo, tensión, revelaciones,
silencios y uso de evidencias. NUNCA escribe la historia (sin texto, sin guion, sin IA, sin
prompts). 100% determinista, basado en reglas objetivas, contratos y estructuras narrativas
reales. Produce un ``NarrativeBlueprint`` que consumen VIS → VAI → Composer.

Persistencia: ``output/narrative/`` (nunca ``knowledge/``).
"""

NAR_SCHEMA_VERSION = "0.1"

from app.nar.inputs import NarrativeInputs
from app.nar.models import NarrativeBlueprint, NarrativeContext

__all__ = [
    "NAR_SCHEMA_VERSION",
    "NarrativeInputs",
    "NarrativeContext",
    "NarrativeBlueprint",
    "NarrativeIntelligenceEngine",
    "StructureSelector",
    "write_blueprint",
    "render_markdown",
]


def __getattr__(name):
    """Exporta el motor de forma perezosa para evitar ciclos de importación al cargar el paquete."""
    if name == "NarrativeIntelligenceEngine":
        from app.nar.engine import NarrativeIntelligenceEngine
        return NarrativeIntelligenceEngine
    if name == "StructureSelector":
        from app.nar.selection import StructureSelector
        return StructureSelector
    if name == "write_blueprint":
        from app.nar.persistence import write_blueprint
        return write_blueprint
    if name == "render_markdown":
        from app.nar.report import render_markdown
        return render_markdown
    raise AttributeError(f"module 'app.nar' has no attribute {name!r}")
