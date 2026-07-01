"""LensEngine — óptica: focal, profundidad de campo, bokeh, apertura, compresión."""

from app.vai.models import VisualContext

_BY_TYPE = {
    "establishing": ["ultra-wide 18mm lens", "deep focus", "f/8 aperture"],
    "wide": ["wide 35mm lens", "deep focus", "f/5.6 aperture"],
    "detail": ["macro lens", "shallow depth of field", "creamy bokeh", "f/2.8 aperture"],
    "closeup": ["85mm portrait lens", "shallow depth of field", "soft bokeh", "f/1.8 aperture"],
    "action": ["35mm lens", "moderate depth of field", "f/4 aperture"],
    "impact": ["50mm lens", "shallow depth of field", "optical compression", "f/2 aperture"],
    "aftermath": ["wide 35mm lens", "deep focus", "f/5.6 aperture"],
}
_DEFAULT = ["35mm lens", "moderate depth of field"]


class LensEngine:
    category = "lens"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        return list(_BY_TYPE.get(str(getattr(shot, "shot_type", "")), _DEFAULT))
