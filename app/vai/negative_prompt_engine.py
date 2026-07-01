"""NegativePromptEngine — negativos automáticos (universales para cualquier proveedor)."""

from app.vai.models import VisualContext

_STANDARD = [
    "cartoon", "anime", "illustration", "painting", "drawing", "cgi", "3d render",
    "video game", "low quality", "lowres", "blurry", "out of focus", "bad anatomy",
    "deformed", "disfigured", "text", "caption", "watermark", "logo", "signature",
    "oversaturated", "duplicate", "flat image", "plastic look", "jpeg artifacts",
]


class NegativePromptEngine:
    category = "negatives"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        negatives = list(_STANDARD)
        # Refuerzo por nivel de realismo (documental fotográfico): fuera estética sintética.
        if context.realism_level in ("high", "ultra"):
            negatives += ["render look", "artificial", "overprocessed"]
        return negatives
