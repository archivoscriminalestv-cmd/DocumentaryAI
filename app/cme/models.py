"""Modelos del Cinematic Motion Engine (CME).

``MotionFingerprint`` resume el movimiento de un plano (para medir diversidad);
``MotionShot`` es el plan completo de cámara de un plano (intención + parámetros +
posición en la línea temporal). Serializable, versionado, provider-agnóstico.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.cme import SCHEMA_VERSION
from app.cme.physics import MotionParameters

# Dimensiones del fingerprint que cuentan para la diversidad de movimiento.
MOTION_DIMENSIONS = ("motion_type", "direction", "family")


@dataclass
class MotionFingerprint:
    motion_type: str = "STATIC"
    family: str = "static"
    direction: str = "none"
    speed: float = 0.0
    duration: float = 0.0
    ease: str = "linear"
    camera_energy: float = 0.0
    camera_stability: float = 1.0
    narrative_purpose: str = ""

    def variable_tuple(self) -> tuple:
        return (self.motion_type, self.direction, self.family)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MotionShot:
    shot_id: str
    scene_id: str
    asset_id: str = ""
    motion_type: str = "STATIC"
    family: str = "static"
    direction: str = "none"
    purpose: str = ""
    narrative_mode: str = ""
    parameters: MotionParameters = field(default_factory=MotionParameters)
    fingerprint: MotionFingerprint = field(default_factory=MotionFingerprint)
    # posición en la línea temporal
    start: float = 0.0
    end: float = 0.0
    duration: float = 0.0
    transition_in: float = 0.0
    transition_out: float = 0.0
    justification: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["schema_version"] = SCHEMA_VERSION
        return data
