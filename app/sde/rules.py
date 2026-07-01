"""Reglas deterministas del SDE: narrativa, parseo y renderizado.

- ``classify_narrative``: decide cuánta diversidad permite la narrativa (entrevista →
  continuidad; reconstrucción/recurso → máxima libertad; etc.).
- ``parse_base_fingerprint``: mapea el ShotExecutionRequest del VAI a categorías.
- ``render_to_spec``: convierte un fingerprint en los campos estructurados que el VSC
  ya consume (camera_language + composition). NO escribe prompts completos.
"""

import re

from app.sde.models import LENSES, ShotFingerprint

# Modo narrativo -> dimensiones LIBRES + umbral de diversidad objetivo + ventana.
# Las dimensiones NO listadas se mantienen (continuidad). Identidad nunca está aquí.
NARRATIVE_MODES = {
    "interview":      {"free": ("composition", "subject_position", "gaze"),
                       "threshold": 0.20, "window": 4},
    "intimate":       {"free": ("shot_size", "camera_angle", "composition", "subject_position"),
                       "threshold": 0.45, "window": 5},
    "observational":  {"free": ("shot_size", "camera_angle", "camera_height", "lens",
                                "composition", "subject_position", "gaze"),
                       "threshold": 0.60, "window": 6},
    "reflective":     {"free": ("shot_size", "camera_angle", "camera_height", "lens",
                                "composition", "subject_position"),
                       "threshold": 0.60, "window": 6},
    "dynamic":        {"free": ("shot_size", "camera_angle", "lens", "composition",
                                "subject_position", "movement"),
                       "threshold": 0.65, "window": 6},
    "reconstruction": {"free": ("shot_size", "camera_angle", "camera_height", "lens",
                                "composition", "subject_position", "gaze", "movement"),
                       "threshold": 0.70, "window": 8},
    "broll":          {"free": ("shot_size", "camera_angle", "camera_height", "lens",
                                "composition", "subject_position", "gaze", "movement"),
                       "threshold": 0.70, "window": 8},
}
DEFAULT_MODE = "observational"


def classify_narrative(documentary_style: str, shot_role: str = "") -> str:
    style = (documentary_style or "").lower()
    role = (shot_role or "").lower()
    # Planos recurso / insertos: máxima libertad.
    if role in ("cutaway", "insert", "detail", "establishing", "broll"):
        return "broll"
    for key in ("interview", "reconstruction", "intimate", "observational", "reflective"):
        if key in style:
            return key
    if "chase" in style or "action" in style or "persecu" in style:
        return "dynamic"
    return DEFAULT_MODE


def mode_config(mode: str) -> dict:
    return NARRATIVE_MODES.get(mode, NARRATIVE_MODES[DEFAULT_MODE])


# --- parseo VAI -> fingerprint ----------------------------------------------

def _nearest_lens(text: str) -> int:
    match = re.search(r"(\d{2,3})\s*mm", text or "")
    if match:
        target = int(match.group(1))
        return min(LENSES, key=lambda l: abs(l - target))
    low = (text or "").lower()
    if "macro" in low or "extreme detail" in low:
        return 135
    if "ultra-wide" in low or "ultra wide" in low:
        return 18
    if "wide" in low:
        return 24
    if "portrait" in low or "tele" in low:
        return 85
    return 35


def _shot_size_from(lead: str) -> str:
    t = (lead or "").lower()
    table = (
        ("extreme detail", "extreme close"), ("insert", "extreme close"), ("macro", "extreme close"),
        ("extreme close", "extreme close"), ("close-up", "close"), ("close up", "close"),
        ("intimate", "close"), ("medium close", "medium close"), ("hero", "medium"),
        ("medium", "medium"), ("american", "american"), ("full", "full"),
        ("establishing", "wide"), ("sweeping", "wide"), ("wide", "wide"), ("extreme wide", "extreme wide"),
    )
    for needle, size in table:
        if needle in t:
            return size
    return "medium"


def _angle_from(angle: str) -> str:
    a = (angle or "").lower()
    if "low" in a:
        return "low"
    if "high" in a:
        return "high"
    if "bird" in a or "aerial" in a or "drone" in a:
        return "bird"
    if "worm" in a:
        return "worm"
    if "dutch" in a or "dynamic" in a or "tilt" in a:
        return "dutch"
    return "eye level"


def _composition_from(comp: str) -> str:
    c = (comp or "").lower()
    table = (
        ("symmetr", "symmetry"), ("rule of thirds", "rule of thirds"), ("off-center", "rule of thirds"),
        ("off center", "rule of thirds"), ("centered", "centered"), ("center", "centered"),
        ("negative space", "negative space"), ("leading", "leading lines"),
        ("diagonal", "diagonal"), ("foreground", "foreground framing"),
        ("silhouette", "silhouette"), ("reflection", "reflection"),
    )
    for needle, value in table:
        if needle in c:
            return value
    return "rule of thirds"


def _movement_from(motion: dict) -> str:
    move = str((motion or {}).get("move", "")).lower()
    known = ("static", "push_in", "pull_out", "parallax", "tracking", "pan", "ken_burns", "orbit")
    return move if move in known else "static"


def parse_base_fingerprint(request, ctx) -> ShotFingerprint:
    spec = getattr(request, "specification", None)
    camera_language = list(getattr(spec, "camera_language", []) or [])
    composition = list(getattr(spec, "composition", []) or [])
    lead = camera_language[0] if camera_language else ""

    return ShotFingerprint(
        shot_size=_shot_size_from(lead),
        camera_angle=_angle_from(getattr(request, "angle", "")),
        camera_height="eye",
        lens=_nearest_lens(getattr(request, "lens", "")),
        composition=_composition_from(composition[0] if composition else ""),
        subject_position="center",
        gaze="off camera left",
        movement=_movement_from(getattr(request, "motion", {})),
        scene=ctx.scene_id, character=ctx.character_name, identity=ctx.identity,
        location=ctx.location, color_palette=ctx.color_palette,
        time_of_day=ctx.time_of_day, weather=ctx.weather, lighting_language=ctx.lighting,
    )


# --- renderizado fingerprint -> campos estructurados (VSC) -------------------

_SHOT_SIZE_PHRASE = {
    "extreme wide": "extreme wide shot", "wide": "wide shot", "full": "full shot",
    "american": "american shot", "medium": "medium shot", "medium close": "medium close-up",
    "close": "close-up", "extreme close": "extreme close-up",
}
_ANGLE_PHRASE = {
    "eye level": "eye-level angle", "low": "low angle", "high": "high angle",
    "bird": "bird's-eye view", "worm": "worm's-eye view", "dutch": "dutch angle",
}
_HEIGHT_PHRASE = {
    "floor": "floor-level camera", "knee": "knee-height camera", "waist": "waist-height camera",
    "chest": "chest-height camera", "eye": "eye-height camera",
    "above head": "raised camera above head height", "drone": "aerial drone height",
}
_COMPOSITION_PHRASE = {
    "centered": "centered composition", "rule of thirds": "rule of thirds composition",
    "negative space": "negative space composition", "leading lines": "leading lines composition",
    "symmetry": "symmetrical composition", "diagonal": "diagonal composition",
    "foreground framing": "foreground framing", "silhouette": "silhouette composition",
    "reflection": "reflection composition",
}
_POSITION_PHRASE = {
    "left": "subject framed left", "center": "subject centered", "right": "subject framed right",
    "foreground": "subject in the foreground", "background": "subject in the background",
}
_GAZE_PHRASE = {
    "camera": "looking into the camera", "off camera left": "looking off-camera left",
    "off camera right": "looking off-camera right", "down": "looking downward",
    "up": "looking upward", "hidden": "face turned away from camera",
}
_MOVEMENT_PHRASE = {
    "static": "static locked frame", "push_in": "slow push-in", "pull_out": "slow pull-out",
    "parallax": "parallax depth move", "tracking": "tracking move", "pan": "slow pan",
    "ken_burns": "ken burns drift", "orbit": "orbital move",
}


def render_to_spec(fp: ShotFingerprint) -> tuple[list[str], list[str]]:
    """Devuelve (camera_language, composition) que el VSC ya sabe compilar."""
    camera_language = [
        _SHOT_SIZE_PHRASE.get(fp.shot_size, "medium shot"),
        _ANGLE_PHRASE.get(fp.camera_angle, "eye-level angle"),
        _HEIGHT_PHRASE.get(fp.camera_height, "eye-height camera"),
        f"{fp.lens}mm lens",
        _GAZE_PHRASE.get(fp.gaze, "looking off-camera left"),
        _MOVEMENT_PHRASE.get(fp.movement, "static locked frame"),
    ]
    composition = [
        _COMPOSITION_PHRASE.get(fp.composition, "rule of thirds composition"),
        _POSITION_PHRASE.get(fp.subject_position, "subject centered"),
    ]
    return camera_language, composition
