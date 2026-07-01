"""Cinematic Motion Engine (CME) — Sprint CME-001.

Director de Cámara virtual y DETERMINISTA. Transforma una secuencia de imágenes
estáticas en un plan de movimiento cinematográfico reproducible. NO genera vídeo, NO
renderiza, NO llama a FFmpeg ni a proveedores de IA: solo construye un ``MotionPlan``
(intención + parámetros), provider-agnóstico (ejecutable luego por FFmpeg, Runway,
Veo, Pika, Kling, OpenAI Video o cualquier motor futuro).

Único punto de integración:  VIS → VAI → SDE → VSC → **CME** → Composer.
Recibe un plano (request enriquecido + contexto) y devuelve un ``MotionShot``.

100% determinista: sin ``random`` y sin sintaxis de proveedor. Cada movimiento tiene
una razón narrativa explícita; nada es Ken Burns por defecto.
"""

SCHEMA_VERSION = "1.0"

from app.cme.models import MotionFingerprint, MotionParameters, MotionShot
from app.cme.orchestrator import CinematicMotionEngine, CMEContext
from app.cme.timeline import MotionTimeline

__all__ = [
    "SCHEMA_VERSION",
    "CinematicMotionEngine",
    "CMEContext",
    "MotionShot",
    "MotionParameters",
    "MotionFingerprint",
    "MotionTimeline",
]
