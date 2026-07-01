"""Interfaz permanente de ejecución de movimiento.

``MotionExecutor`` es la frontera entre el plan (CME) y el motor que lo ejecuta. Hoy
solo existe ``FFmpegMotionExecutor``; mañana podrán enchufarse Runway/Veo/Kling/Luma/
Pika implementando esta misma interfaz, SIN tocar el Composer.
"""

from typing import Protocol


class MotionExecutor(Protocol):
    name: str

    def execute(self, *, asset_path: str, motion_type: str, parameters: dict,
                duration: float, out_clip: str,
                fade_in: float = 0.0, fade_out: float = 0.0) -> str:
        """Renderiza UN plano (imagen + movimiento) a un clip de vídeo. Devuelve la ruta."""
        ...
