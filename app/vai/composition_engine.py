"""CompositionEngine — composición fotográfica (rule of thirds, simetría, líneas…)."""

from app.vai.models import VisualContext
from app.vai.selection import rotate

_BY_TYPE = {
    "establishing": ["wide symmetrical composition", "strong leading lines"],
    "wide": ["rule of thirds", "layered foreground and background"],
    "detail": ["centered macro framing", "tight rule-of-thirds detail"],
    "closeup": ["balanced close-up framing", "frame within a frame"],
    "action": ["dynamic diagonal composition", "off-center action framing"],
    "impact": ["dramatic centered composition", "negative space for tension"],
    "aftermath": ["wide negative space", "balanced symmetry"],
}
_DEFAULT = ["rule of thirds", "balanced composition"]


class CompositionEngine:
    category = "composition"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        options = _BY_TYPE.get(str(getattr(shot, "shot_type", "")), _DEFAULT)
        primary = rotate(options, int(getattr(shot, "index", 0)), offset=0) or options[0]
        return [primary, "clear foreground-background separation"]
