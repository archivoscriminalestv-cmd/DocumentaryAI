"""AtmosphereEngine — atmósfera: niebla, bruma, polvo, partículas, humedad…

Sutil por defecto (no satura cada plano). Varía por índice para dar riqueza sin
repetición. La intensidad/tipo se inclina según el estilo/mood del contexto.
"""

from app.vai.models import VisualContext
from app.vai.selection import rotate

_BY_STYLE = {
    "investigative": ["faint haze", "floating dust particles", "low atmospheric smoke"],
    "cinematic": ["volumetric atmosphere", "subtle haze", "fine airborne particles"],
    "nature": ["morning mist", "soft atmospheric haze", "light humidity in the air"],
    "documentary": ["subtle atmospheric depth", "faint haze", "natural air diffusion"],
}
_DEFAULT = ["subtle atmospheric depth", "faint haze"]


class AtmosphereEngine:
    category = "atmosphere"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        options = _BY_STYLE.get(context.style, _DEFAULT)
        primary = rotate(options, int(getattr(shot, "index", 0)), offset=1) or options[0]
        return [primary]
