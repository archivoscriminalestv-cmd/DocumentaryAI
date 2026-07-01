"""Modelos y vocabulario cinematográfico del SDE.

Las categorías son LISTAS ORDENADAS (no aleatorias): el orden define la prioridad
determinista de selección cuando hay que desempatar. El ``ShotFingerprint`` resume
la composición de un plano; sus dimensiones VARIABLES son las que el SDE diversifica.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.sde import SCHEMA_VERSION

# --- vocabulario cinematográfico (orden = prioridad determinista) ------------

SHOT_SIZES = ("extreme wide", "wide", "full", "american", "medium", "medium close",
              "close", "extreme close")
CAMERA_ANGLES = ("eye level", "low", "high", "bird", "worm", "dutch")
CAMERA_HEIGHTS = ("floor", "knee", "waist", "chest", "eye", "above head", "drone")
LENSES = (18, 24, 28, 35, 50, 85, 135)
COMPOSITIONS = ("centered", "rule of thirds", "negative space", "leading lines",
                "symmetry", "diagonal", "foreground framing", "silhouette", "reflection")
SUBJECT_POSITIONS = ("left", "center", "right", "foreground", "background")
GAZES = ("camera", "off camera left", "off camera right", "down", "up", "hidden")
LIGHTINGS = ("soft", "hard", "window", "overcast", "backlight", "rim", "volumetric",
             "golden hour", "blue hour")
MOVEMENTS = ("static", "push_in", "pull_out", "parallax", "tracking", "pan",
             "ken_burns", "orbit")

# Catálogo por dimensión variable (para el planner LRU).
CATEGORY = {
    "shot_size": SHOT_SIZES,
    "camera_angle": CAMERA_ANGLES,
    "camera_height": CAMERA_HEIGHTS,
    "lens": LENSES,
    "composition": COMPOSITIONS,
    "subject_position": SUBJECT_POSITIONS,
    "gaze": GAZES,
    "movement": MOVEMENTS,
}

# Dimensiones que el SDE puede diversificar (NUNCA toca identidad/escena/personaje).
VARIABLE_DIMENSIONS = ("shot_size", "camera_angle", "camera_height", "lens",
                       "composition", "subject_position", "gaze", "movement")


@dataclass
class ShotFingerprint:
    # --- dimensiones VARIABLES (las que se diversifican) ---
    shot_size: str = "medium"
    camera_angle: str = "eye level"
    camera_height: str = "eye"
    lens: int = 35
    composition: str = "rule of thirds"
    subject_position: str = "center"
    gaze: str = "off camera left"
    movement: str = "static"
    # --- contexto (NO se diversifica; awareness narrativa/identidad) ---
    scene: str = ""
    character: str = ""
    identity: str = ""
    location: str = ""
    color_palette: str = ""
    time_of_day: str = ""
    weather: str = ""
    lighting_language: str = ""

    def variable_tuple(self) -> tuple:
        return tuple(getattr(self, d) for d in VARIABLE_DIMENSIONS)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ShotRecord:
    index: int
    shot_id: str
    scene: str
    narrative_mode: str
    fingerprint: ShotFingerprint
    base_fingerprint: ShotFingerprint
    diversity_score: float = 0.0
    changes: list[dict] = field(default_factory=list)   # [{dim, from, to, reason}]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["schema_version"] = SCHEMA_VERSION
        return data
