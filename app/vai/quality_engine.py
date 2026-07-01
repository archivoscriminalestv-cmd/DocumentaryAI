"""QualityEngine — calidad técnica y densidad visual (provider-agnóstico).

Evita jerga de proveedores concretos (nada de "masterpiece/--ar/trending"): solo
términos universales de calidad e riqueza visual.
"""

from app.vai.models import VisualContext

_BASE = ["8k", "high detail", "sharp focus"]
_DENSITY = {
    "establishing": "rich environmental detail",
    "wide": "dense scene detail",
    "detail": "fine micro-detail",
    "closeup": "intricate surface detail",
    "action": "motion-rich detail",
    "impact": "high visual impact detail",
    "aftermath": "atmospheric environmental detail",
}


class QualityEngine:
    category = "quality"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        out = list(_BASE)
        density = _DENSITY.get(str(getattr(shot, "shot_type", "")))
        if density:
            out.append(density)
        return out
