"""Documentary Runtime & Composer (COMP-001).

Primer runtime end-to-end: EJECUTA el pipeline completo y produce un MP4 real. El
Composer NO toma decisiones cinematográficas (ya las tomaron CRE/CCE/ERE/VIS/VAI/SDE/
VSC/VPL/ALR/CME): solo consume sus contratos públicos y ejecuta.

Para cada plano: asset (ALR) + plan de movimiento (CME) + duración (timeline) +
narración → clip MP4. Luego ensambla: transiciones (timeline), audio sincronizado
(narración + música) → ``documentary.mp4``.

La ejecución del movimiento vive tras una interfaz ``MotionExecutor`` con una
implementación ``FFmpegMotionExecutor``; en el futuro se podrá enchufar Runway/Veo/
Kling/Luma/Pika sin tocar el Composer.
"""

SCHEMA_VERSION = "1.0"

from app.composer.interfaces import MotionExecutor
from app.composer.models import ClipResult, ComposerResult
from app.composer.runtime import DocumentaryComposer

__all__ = [
    "SCHEMA_VERSION",
    "DocumentaryComposer",
    "MotionExecutor",
    "ClipResult",
    "ComposerResult",
]
