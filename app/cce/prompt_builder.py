"""IdentityPromptBuilder — bloque de identidad en lenguaje NEUTRO (provider-agnostic).

El bloque se construye AUTOMÁTICAMENTE a partir del ``CharacterProfile`` (atributos +
reglas de continuidad derivadas). No hay frases de identidad hardcodeadas: cada
cláusula procede de un dato real del perfil o de una regla derivada. El VSC/CLI lo
antepone al prompt del plano; los adapters del VPL lo traducen luego si lo necesitan.

Para un perfil PARCIAL (p.ej. Coquito), el bloque contiene solo las directivas de
estabilidad de identidad (misma persona, no rediseñar, proporciones fijas), sin
inventar rasgos concretos.
"""

from app.cce.models import VISUAL_ATTRIBUTES, CharacterProfile

_LABELS = dict(VISUAL_ATTRIBUTES)


def _label(attribute: str) -> str:
    return _LABELS.get(attribute, attribute.replace("_", " "))


class IdentityPromptBuilder:
    """Construye el bloque de identidad y el bloque de negativos desde el perfil."""

    def build_identity_block(self, profile: CharacterProfile) -> str:
        locked: list[str] = []
        soft: list[str] = []
        name = ""
        keep_proportions = False
        no_redesign = False

        for rule in profile.continuity_rules:
            if rule.attribute == "identity":
                name = rule.value
                no_redesign = True
            elif rule.attribute == "face_proportions":
                keep_proportions = True
            elif rule.severity == "locked":
                label = _label(rule.attribute)
                locked.append(f"the same {label} ({rule.value})" if rule.value else f"the same {label}")
            else:  # soft
                label = _label(rule.attribute)
                tail = f" ({rule.value})" if rule.value else ""
                soft.append(f"{label} may change only if the story requires it{tail}")

        vid = f" {profile.visual_identity_id}" if profile.visual_identity_id else ""
        who = f"the same person, {name}," if name else "the same person"
        sentences = [f"Consistent identity{vid}: {who} across every shot of the documentary."]

        if locked:
            sentences.append("Maintain " + ", ".join(locked) + ".")
        if soft:
            sentences.append("; ".join(s.capitalize() for s in soft) + ".")

        directives = []
        if keep_proportions:
            directives.append("keep facial proportions fixed")
        if no_redesign:
            directives.append("do not redesign the character")
        directives.append("maintain identity consistency")
        sentences.append(_sentence(directives))
        return " ".join(sentences)

    def build_negative_block(self, profile: CharacterProfile) -> str:
        return ", ".join(profile.negative_constraints)


def _sentence(parts: list[str]) -> str:
    if not parts:
        return ""
    text = "; ".join(parts)
    return text[0].upper() + text[1:] + "."
