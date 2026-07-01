"""Parámetros FÍSICOS del movimiento de cámara (provider-agnósticos, configurables).

No se usan valores arbitrarios: cada movimiento deriva de una velocidad/tasa física.
Todo se expresa en magnitudes neutras (m/s, °/s, %/s) y se convierte a parámetros
normalizados por plano. Determinista: misma definición + duración → mismos parámetros.
"""

from dataclasses import dataclass

# --- constantes físicas base (configurables) ---------------------------------
PUSH_IN_SPEED_MS = 0.30      # m/s
PULL_OUT_SPEED_MS = 0.30
DOLLY_SPEED_MS = 0.25
TRUCK_SPEED_MS = 0.25
CRANE_SPEED_MS = 0.20
DRONE_SPEED_MS = 0.50
MACRO_SLIDE_SPEED_MS = 0.05

PAN_RATE_DEG_S = 8.0         # °/s
TILT_RATE_DEG_S = 6.0
ORBIT_RATE_DEG_S = 6.0
ZOOM_RATE_PCT_S = 4.0        # %/s

HANDHELD_SUBTLE_AMP_DEG = 0.4
HANDHELD_NERVOUS_AMP_DEG = 1.2
MICRO_BREATHING_AMP_DEG = 0.1
FLOATING_AMP_DEG = 0.2

# Límites de seguridad de IDENTIDAD: el movimiento jamás debe deformar al personaje.
MAX_ZOOM_PCT = 30.0          # zoom total por plano
MAX_PAN_DEG = 25.0
MAX_TILT_DEG = 20.0
MAX_TRANSLATE = 0.20         # fracción de cuadro
MAX_ROLL_DEG = 3.0           # balanceo (dutch/handheld)


def _clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


@dataclass
class MotionParameters:
    """Parámetros normalizados del movimiento (lo que ejecutará cualquier motor)."""

    duration: float = 4.0
    easing: str = "ease_in_out"
    speed: float = 0.0            # magnitud principal (m/s o °/s según el tipo)
    zoom_pct: float = 0.0         # + acerca, - aleja
    pan_deg: float = 0.0          # + derecha
    tilt_deg: float = 0.0         # + arriba
    translate_x: float = 0.0      # fracción de cuadro (+ derecha)
    translate_y: float = 0.0      # fracción de cuadro (+ arriba)
    roll_deg: float = 0.0         # balanceo
    amplitude_deg: float = 0.0    # jitter (handheld / breathing)
    focus_shift: float = 0.0      # rack focus (0..1), no espacial
    stability: float = 1.0        # 1.0 bloqueada .. 0.0 muy inestable

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)


def compute_parameters(primary: str, direction: str, duration: float, easing: str,
                       stability: float, *, amplitude: float = 0.0) -> MotionParameters:
    """Convierte (primary, direction, duración) en parámetros físicos normalizados."""
    p = MotionParameters(duration=round(duration, 3), easing=easing, stability=stability,
                         amplitude_deg=round(amplitude, 3))
    sign = -1.0 if direction in ("out", "left", "down", "ccw") else 1.0

    if primary == "zoom":
        p.speed = PUSH_IN_SPEED_MS
        p.zoom_pct = _clamp(sign * ZOOM_RATE_PCT_S * duration, MAX_ZOOM_PCT)
    elif primary == "pan":
        p.speed = PAN_RATE_DEG_S
        p.pan_deg = _clamp(sign * PAN_RATE_DEG_S * duration, MAX_PAN_DEG)
    elif primary == "tilt":
        p.speed = TILT_RATE_DEG_S
        p.tilt_deg = _clamp(sign * TILT_RATE_DEG_S * duration, MAX_TILT_DEG)
    elif primary == "dolly":
        p.speed = DOLLY_SPEED_MS
        p.translate_x = _clamp(sign * DOLLY_SPEED_MS * duration * 0.1, MAX_TRANSLATE)
        p.zoom_pct = _clamp(2.0, MAX_ZOOM_PCT)  # leve paralaje de profundidad
    elif primary == "truck":
        p.speed = TRUCK_SPEED_MS
        p.translate_x = _clamp(sign * TRUCK_SPEED_MS * duration * 0.1, MAX_TRANSLATE)
    elif primary == "crane":
        p.speed = CRANE_SPEED_MS
        p.translate_y = _clamp(sign * CRANE_SPEED_MS * duration * 0.1, MAX_TRANSLATE)
        p.tilt_deg = _clamp(sign * TILT_RATE_DEG_S * duration * 0.3, MAX_TILT_DEG)
    elif primary == "orbit":
        p.speed = ORBIT_RATE_DEG_S
        p.pan_deg = _clamp(sign * ORBIT_RATE_DEG_S * duration * 0.5, MAX_PAN_DEG)
        p.translate_x = _clamp(sign * 0.03 * duration, MAX_TRANSLATE)
    elif primary == "parallax":
        p.translate_x = _clamp(0.02 * duration, MAX_TRANSLATE)
        p.zoom_pct = _clamp(1.5, MAX_ZOOM_PCT)
    elif primary == "drone":
        p.speed = DRONE_SPEED_MS
        p.translate_y = _clamp(-0.03 * duration, MAX_TRANSLATE)  # descenso
        p.zoom_pct = _clamp(ZOOM_RATE_PCT_S * duration * 0.5, MAX_ZOOM_PCT)
    elif primary == "macro":
        p.speed = MACRO_SLIDE_SPEED_MS
        p.translate_x = _clamp(sign * MACRO_SLIDE_SPEED_MS * duration, MAX_TRANSLATE)
    elif primary == "rack_focus":
        p.focus_shift = 1.0
    elif primary == "handheld":
        p.roll_deg = _clamp(amplitude * 0.5, MAX_ROLL_DEG)
        p.amplitude_deg = round(amplitude, 3)
    elif primary == "breathing":
        p.zoom_pct = _clamp(0.5, MAX_ZOOM_PCT)
        p.amplitude_deg = round(amplitude, 3)
    elif primary == "floating":
        p.translate_y = _clamp(0.01 * duration, MAX_TRANSLATE)
        p.amplitude_deg = round(amplitude, 3)
    # "none" (static/locked) -> todo a cero
    return p
