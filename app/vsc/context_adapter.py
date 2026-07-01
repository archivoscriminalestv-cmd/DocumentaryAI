"""Adaptador SceneVisualContext -> VisualContext (VAI), para coherencia escena↔plano.

Deriva el contexto que consume VAI a partir de la identidad de escena del VSC, de
modo que las decisiones de plano (VAI) sean coherentes con la continuidad de la
escena. Duck-typed; no acopla VSC a VAI más allá de construir su contexto.
"""

from app.vai import VisualContext
from app.vsc.models import SceneVisualContext


def _temperature(palette: str) -> str:
    p = (palette or "").lower()
    if any(w in p for w in ("warm", "golden", "amber")):
        return "warm"
    if any(w in p for w in ("cold", "cool", "blue", "teal")):
        return "cool"
    return "neutral"


def _saturation(palette: str) -> str:
    p = (palette or "").lower()
    if any(w in p for w in ("muted", "desaturated", "pale")):
        return "muted"
    if any(w in p for w in ("vivid", "saturated", "vibrant")):
        return "vivid"
    return "moderate"


def _lighting_key(lighting: str) -> str:
    light = (lighting or "").lower()
    if "low-key" in light or "chiaroscuro" in light:
        return "low-key"
    if "high-key" in light or "bright" in light:
        return "high-key"
    return "balanced"


def to_vai_context(scene: SceneVisualContext, subject: str) -> VisualContext:
    return VisualContext(
        subject=subject,
        style=scene.documentary_style.split()[0].lower() if scene.documentary_style else "documentary",
        color_temperature=_temperature(scene.color_palette),
        saturation=_saturation(scene.color_palette),
        lighting_key=_lighting_key(scene.lighting_language),
        realism_level=scene.realism_level,
    )
