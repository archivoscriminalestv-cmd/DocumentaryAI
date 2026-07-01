"""LightingEngine — iluminación: volumétrica, rim, soft/hard, god rays, chiaroscuro.

Respeta la INTENCIÓN de VIS (``shot.lighting`` como semilla) y la refina según la
clave de luz del contexto y el tipo de plano.
"""

from app.vai.models import VisualContext

_KEY = {
    "low-key": ["low-key lighting", "chiaroscuro", "hard rim light", "deep shadows"],
    "balanced": ["soft natural light", "ambient bounce", "gentle key light"],
    "high-key": ["high-key lighting", "soft fill", "bright airy light"],
}
_TYPE_ACCENT = {
    "establishing": "volumetric light with god rays",
    "impact": "dramatic rim light",
    "detail": "soft directional light",
    "closeup": "soft window light",
}


class LightingEngine:
    category = "lighting"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        base = list(_KEY.get(context.lighting_key, _KEY["balanced"]))
        accent = _TYPE_ACCENT.get(str(getattr(shot, "shot_type", "")))
        if accent:
            base.append(accent)
        # Semilla de VIS (si trae un descriptor de luz, se conserva).
        seed = str(getattr(shot, "lighting", "")).strip()
        if seed and seed not in base:
            base.append(seed)
        return base
