"""VAI — Visual AI Director (Director de Fotografía de DocumentaryAI).

Transforma un ``Shot`` (VIS) en una ``VisualSpecification`` y un
``ShotExecutionRequest`` listo para el MGL, mediante motores especialistas
deterministas y desacoplados. No genera imágenes, no llama a proveedores, no toca
VIS/RDA/MGL/FFmpeg. Independiente de proveedor. Ver README.md.
"""

from app.vai.context import build_context
from app.vai.models import ShotExecutionRequest, VisualContext, VisualSpecification
from app.vai.visual_director import VisualDirector

__all__ = [
    "VisualDirector",
    "VisualContext",
    "VisualSpecification",
    "ShotExecutionRequest",
    "build_context",
]
