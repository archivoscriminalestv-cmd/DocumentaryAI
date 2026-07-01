"""ColorGradingEngine — grade: teal-orange, warm doc, cold investigative, Kodak, IMAX…

Determinista a partir de temperatura/saturación del contexto + estilo. Provider-
agnóstico (describe el look, no usa sintaxis de ningún proveedor).
"""

from app.vai.models import VisualContext

_TEMPERATURE = {
    "warm": "warm documentary grade with golden tones",
    "cool": "cold investigative grade with teal shadows",
    "neutral": "natural filmic color grade",
}
_SATURATION = {
    "vivid": "rich saturated colors",
    "moderate": "balanced color saturation",
    "muted": "desaturated muted palette",
}
_STYLE_LOOK = {
    "cinematic": "teal-and-orange cinematic grade, IMAX look",
    "investigative": "high-contrast cold grade",
    "nature": "vibrant natural Kodak film look",
    "documentary": "Kodak film stock look",
}


class ColorGradingEngine:
    category = "color_grade"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        out = [_TEMPERATURE.get(context.color_temperature, _TEMPERATURE["neutral"])]
        out.append(_SATURATION.get(context.saturation, _SATURATION["moderate"]))
        look = _STYLE_LOOK.get(context.style)
        if look:
            out.append(look)
        return out
