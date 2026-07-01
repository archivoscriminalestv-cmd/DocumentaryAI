"""CameraLanguageEngine — TRADUCE las decisiones de VIS a lenguaje de cine.

NO cambia la cámara (shot_type/camera_move los decide VIS): solo los describe en
lenguaje cinematográfico para el prompt.
"""

from app.vai.models import VisualContext

_TYPE = {
    "establishing": "sweeping establishing shot",
    "wide": "wide cinematic shot",
    "detail": "extreme detail insert shot",
    "closeup": "intimate close-up shot",
    "action": "kinetic action shot",
    "impact": "dramatic hero shot",
    "aftermath": "reflective wide shot",
}
_MOVE = {
    "push_in": "slow cinematic push-in",
    "pull_out": "slow reveal pull-out",
    "tracking": "smooth tracking movement",
    "drone": "aerial drone perspective",
    "orbital": "orbital camera move",
    "parallax": "parallax depth motion",
    "ken_burns": "subtle Ken Burns drift",
    "pan": "steady pan",
    "zoom_in": "slow zoom-in",
    "static": "locked-off framing",
}


class CameraLanguageEngine:
    category = "camera_language"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        out = [_TYPE.get(str(getattr(shot, "shot_type", "")), "cinematic shot")]
        move = _MOVE.get(str(getattr(shot, "camera_move", "")), "")
        if move:
            out.append(move)
        return out
