"""RealismEngine — realismo físico: PBR, fotorealismo, grano, GI, sombras naturales."""

from app.vai.models import VisualContext

_BASE = ["photorealistic", "ultra detailed", "realistic textures", "natural shadows", "subtle film grain"]
_HIGH = ["physically based rendering", "global illumination", "cinematic photography"]
_ULTRA = ["high dynamic range", "ray-traced lighting", "subsurface scattering"]


class RealismEngine:
    category = "realism"

    def contribute(self, shot, context: VisualContext) -> list[str]:
        out = list(_BASE)
        if context.realism_level in ("high", "ultra"):
            out += _HIGH
        if context.realism_level == "ultra":
            out += _ULTRA
        return out
