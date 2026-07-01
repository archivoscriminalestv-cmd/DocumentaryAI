"""Construcción de VisualContext (desacoplada: duck-typing de scene/profile).

VAI no depende de RDA ni de VIS: este helper traduce una escena + un perfil de
estilo (p.ej. CinematicProfile del RDA, o cualquier objeto con esos atributos) a
los hints planos que VAI consume. Si no hay perfil, usa defaults neutros.
"""

from app.vai.models import VisualContext


def _lighting_key(tendency: str) -> str:
    t = (tendency or "").lower()
    if t.startswith("low-key"):
        return "low-key"
    if t.startswith("high-key"):
        return "high-key"
    return "balanced"


def build_context(scene, profile=None, *, style: str = "documentary", realism_level: str = "high") -> VisualContext:
    subject = str(getattr(scene, "title", "")).strip() or str(getattr(scene, "narration", "")).strip()[:80] or "the subject"
    if profile is None:
        return VisualContext(subject=subject, style=style, realism_level=realism_level)
    return VisualContext(
        subject=subject,
        style=style,
        color_temperature=str(getattr(profile, "color_temperature", "neutral")),
        saturation=str(getattr(profile, "saturation_tendency", "moderate")),
        lighting_key=_lighting_key(str(getattr(profile, "lighting_tendency", "balanced"))),
        realism_level=realism_level,
    )
