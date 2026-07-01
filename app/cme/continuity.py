"""Continuidad de escena + seguridad de identidad del CME.

- Todos los planos de una misma escena comparten la CLASE de cámara (steady|handheld):
  no se mezclan estilos incompatibles.
- El movimiento jamás puede deformar al personaje: los parámetros se mantienen dentro
  de límites de identidad (ya garantizados por ``physics.compute_parameters``); aquí se
  verifican como red de seguridad.
"""

from app.cme.motion_catalog import compatible
from app.cme.physics import (
    MAX_PAN_DEG,
    MAX_ROLL_DEG,
    MAX_TILT_DEG,
    MAX_TRANSLATE,
    MAX_ZOOM_PCT,
    MotionParameters,
)


def enforce_scene_class(scene_class: str, motion_type: str) -> bool:
    """¿Es ``motion_type`` compatible con la clase de la escena?"""
    return compatible(scene_class, motion_type)


def remap_to_scene_class(scene_class: str, motion_type: str) -> str:
    """Si el movimiento no es compatible con la escena, lo lleva a un equivalente."""
    if compatible(scene_class, motion_type):
        return motion_type
    return "HANDHELD_SUBTLE" if scene_class == "handheld" else "SLOW_PUSH_IN"


def assert_identity_safe(params: MotionParameters) -> None:
    """El movimiento no puede deformar rostro/proporciones/identidad."""
    checks = (
        (abs(params.zoom_pct), MAX_ZOOM_PCT, "zoom"),
        (abs(params.pan_deg), MAX_PAN_DEG, "pan"),
        (abs(params.tilt_deg), MAX_TILT_DEG, "tilt"),
        (abs(params.translate_x), MAX_TRANSLATE, "translate_x"),
        (abs(params.translate_y), MAX_TRANSLATE, "translate_y"),
        (abs(params.roll_deg), MAX_ROLL_DEG, "roll"),
    )
    for value, limit, name in checks:
        if value > limit + 1e-6:
            raise ValueError(f"CME excede el límite de identidad en '{name}': {value} > {limit}")
