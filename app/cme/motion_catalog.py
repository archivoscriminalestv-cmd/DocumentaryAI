"""Motion Grammar — catálogo estructurado de movimientos de cámara.

Cada movimiento define: familia (continuidad), estabilidad, ``primary`` físico +
dirección, duración base, easing, energía y amplitud. Es la única fuente de verdad
del vocabulario de cámara; añadir un movimiento = añadir una entrada aquí.

Las familias agrupan estilos COMPATIBLES para la continuidad de escena:
- ``static``  : cámara fija (compatible con cualquier escena)
- ``steady``  : movimientos suaves y estabilizados
- ``handheld``: cámara en mano (tensión); no se mezcla con ``steady``
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MotionDefinition:
    motion_type: str
    family: str            # static | steady | handheld
    primary: str           # zoom|pan|tilt|dolly|truck|crane|orbit|parallax|drone|macro|rack_focus|handheld|breathing|floating|none
    direction: str         # in|out|left|right|up|down|cw|ccw|none
    base_duration: float
    easing: str
    energy: float          # 0..1
    stability: float       # 0..1 (1 = bloqueada)
    amplitude: float = 0.0  # jitter (handheld/breathing)


def _d(*args, **kw) -> MotionDefinition:
    return MotionDefinition(*args, **kw)


CATALOG: dict[str, MotionDefinition] = {
    "STATIC":          _d("STATIC", "static", "none", "none", 3.0, "linear", 0.0, 1.0),
    "LOCKED":          _d("LOCKED", "static", "none", "none", 3.5, "linear", 0.05, 1.0),
    "MICRO_BREATHING": _d("MICRO_BREATHING", "static", "breathing", "none", 4.0, "ease_in_out", 0.10, 0.95, 0.1),
    "SLOW_PUSH_IN":    _d("SLOW_PUSH_IN", "steady", "zoom", "in", 6.0, "ease_in_out", 0.30, 0.92),
    "SLOW_PULL_OUT":   _d("SLOW_PULL_OUT", "steady", "zoom", "out", 6.0, "ease_in_out", 0.30, 0.92),
    "DOLLY_LEFT":      _d("DOLLY_LEFT", "steady", "dolly", "left", 5.0, "ease_in_out", 0.40, 0.90),
    "DOLLY_RIGHT":     _d("DOLLY_RIGHT", "steady", "dolly", "right", 5.0, "ease_in_out", 0.40, 0.90),
    "TRUCK_LEFT":      _d("TRUCK_LEFT", "steady", "truck", "left", 5.0, "ease_in_out", 0.40, 0.90),
    "TRUCK_RIGHT":     _d("TRUCK_RIGHT", "steady", "truck", "right", 5.0, "ease_in_out", 0.40, 0.90),
    "PAN_LEFT":        _d("PAN_LEFT", "steady", "pan", "left", 5.0, "ease_in_out", 0.45, 0.90),
    "PAN_RIGHT":       _d("PAN_RIGHT", "steady", "pan", "right", 5.0, "ease_in_out", 0.45, 0.90),
    "TILT_UP":         _d("TILT_UP", "steady", "tilt", "up", 4.5, "ease_in_out", 0.40, 0.90),
    "TILT_DOWN":       _d("TILT_DOWN", "steady", "tilt", "down", 4.5, "ease_in_out", 0.40, 0.90),
    "CRANE_UP":        _d("CRANE_UP", "steady", "crane", "up", 6.0, "ease_in_out", 0.60, 0.88),
    "CRANE_DOWN":      _d("CRANE_DOWN", "steady", "crane", "down", 6.0, "ease_in_out", 0.60, 0.88),
    "ORBIT_LEFT":      _d("ORBIT_LEFT", "steady", "orbit", "ccw", 7.0, "ease_in_out", 0.60, 0.86),
    "ORBIT_RIGHT":     _d("ORBIT_RIGHT", "steady", "orbit", "cw", 7.0, "ease_in_out", 0.60, 0.86),
    "PARALLAX":        _d("PARALLAX", "steady", "parallax", "none", 6.0, "ease_in_out", 0.40, 0.90),
    "DRONE_REVEAL":    _d("DRONE_REVEAL", "steady", "drone", "none", 8.0, "ease_out", 0.75, 0.82),
    "MACRO_SLIDE":     _d("MACRO_SLIDE", "steady", "macro", "right", 6.0, "ease_in_out", 0.30, 0.90),
    "RACK_FOCUS":      _d("RACK_FOCUS", "steady", "rack_focus", "none", 4.0, "ease_in_out", 0.20, 0.92),
    "FLOATING":        _d("FLOATING", "steady", "floating", "none", 5.0, "ease_in_out", 0.25, 0.85, 0.2),
    "REVEAL":          _d("REVEAL", "steady", "crane", "up", 6.0, "ease_out", 0.50, 0.88),
    "HANDHELD_SUBTLE": _d("HANDHELD_SUBTLE", "handheld", "handheld", "none", 5.0, "linear", 0.60, 0.60, 0.4),
    "HANDHELD_NERVOUS": _d("HANDHELD_NERVOUS", "handheld", "handheld", "none", 4.0, "linear", 0.95, 0.30, 1.2),
}

# Orden determinista del catálogo (para desempates del planner).
CATALOG_ORDER = tuple(CATALOG.keys())

# Compatibilidad de familias por clase de escena (continuidad).
SCENE_CLASS_FAMILIES = {
    "steady": ("static", "steady"),
    "handheld": ("static", "handheld"),
}


def compatible(scene_class: str, motion_type: str) -> bool:
    fam = CATALOG[motion_type].family
    return fam in SCENE_CLASS_FAMILIES.get(scene_class, ("static", "steady"))


def candidates_for(scene_class: str) -> list[str]:
    return [m for m in CATALOG_ORDER if compatible(scene_class, m)]
