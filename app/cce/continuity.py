"""Derivación AUTOMÁTICA de reglas de continuidad desde un ``CharacterProfile``.

Las reglas no se escriben a mano: se derivan de los atributos conocidos del perfil.
- Atributos identitarios -> ``locked`` (no pueden cambiar nunca).
- Atributos mutables (ropa/accesorios) -> ``soft`` (evolucionan solo si el guion lo
  exige).
Si el perfil es parcial, se emiten igualmente las reglas de ESTABILIDAD de identidad
(misma persona, proporciones faciales fijas), que no inventan ningún rasgo concreto.
"""

from app.cce.models import (
    MUTABLE_ATTRIBUTES,
    VISUAL_ATTRIBUTES,
    CharacterProfile,
    ContinuityRule,
)

_LABELS = dict(VISUAL_ATTRIBUTES)


def _locked(label: str) -> str:
    return f"{label} must remain identical across every shot and scene"


def _soft(label: str) -> str:
    return f"{label} may evolve only if the story requires it"


def derive_continuity_rules(profile: CharacterProfile) -> list[ContinuityRule]:
    rules: list[ContinuityRule] = []

    # 1) Estabilidad de identidad: SIEMPRE (no inventa rasgos, solo prohíbe rediseñar).
    rules.append(ContinuityRule(
        attribute="identity", severity="locked",
        directive="the same person across every shot; do not redesign the character",
        value=profile.canonical_name,
    ))
    rules.append(ContinuityRule(
        attribute="face_proportions", severity="locked",
        directive="facial proportions must remain fixed",
    ))

    # 2) Una regla por atributo escalar CONOCIDO (en orden canónico).
    values = profile.attribute_values()
    for name, label in VISUAL_ATTRIBUTES:
        if name not in values:
            continue
        if name in MUTABLE_ATTRIBUTES:
            rules.append(ContinuityRule(attribute=name, severity="soft",
                                        directive=_soft(label), value=values[name]))
        else:
            rules.append(ContinuityRule(attribute=name, severity="locked",
                                        directive=_locked(label), value=values[name]))

    # 3) Listas mutables: accesorios y paleta dominante (soft).
    if profile.accessories:
        rules.append(ContinuityRule(attribute="accessories", severity="soft",
                                    directive=_soft("accessories"),
                                    value=", ".join(profile.accessories)))
    if profile.dominant_colors:
        rules.append(ContinuityRule(attribute="dominant_colors", severity="soft",
                                    directive=_soft("dominant colour palette"),
                                    value=", ".join(profile.dominant_colors)))
    return rules
