"""IdentityLockEngine — convierte una ``CharacterBible`` en un ``CharacterProfile``.

La identidad visual resultante es PERMANENTE: el mismo input produce siempre el mismo
perfil (determinista). Solo se vuelcan atributos visuales realmente presentes en la
bible (y, opcionalmente, referencias visuales del EvidenceGraph). NUNCA se inventan
rasgos: si un dato no existe, el campo queda vacío y el perfil es PARCIAL.

No genera imágenes, no genera prompts de plano, no conoce al proveedor.
"""

import re

from app.cce.continuity import derive_continuity_rules
from app.cce.models import (
    VISUAL_ATTRIBUTES,
    CharacterProfile,
    ContinuityRule,
    ReferenceImage,
    visual_identity_id,
)

_LABELS = dict(VISUAL_ATTRIBUTES)

# Colores de pelo reconocibles dentro del texto libre del campo ``hair`` (extracción,
# no invención: solo se usa si la palabra aparece literalmente).
_HAIR_COLORS = ("white", "grey", "gray", "silver", "black", "brown", "blonde",
                "blond", "red", "ginger", "auburn", "bald")

# Negativos de identidad SIEMPRE seguros (no inventan rasgos; prohíben rediseñar).
_BASE_NEGATIVES = (
    "different person", "another person", "multiple different people",
    "inconsistent face", "face morphing between shots", "changing identity",
    "altered facial proportions", "random appearance",
)


def _extract_hair_color(hair: str) -> str:
    text = (hair or "").lower()
    for color in _HAIR_COLORS:
        if re.search(rf"\b{color}\b", text):
            return "gray" if color == "grey" else color
    return ""


def _age_range_from(text: str) -> str:
    """Bucket de década a partir de una edad numérica explícita (restatement, no
    invención). 'around 72' -> '70s'. Sin número -> ''."""
    match = re.search(r"\b(\d{1,3})\b", text or "")
    if not match:
        return ""
    age = int(match.group(1))
    if age <= 0 or age > 130:
        return ""
    return f"{(age // 10) * 10}s"


class IdentityLockEngine:
    """Bible (+ EvidenceGraph opcional) -> CharacterProfile determinista."""

    def lock(self, bible, evidence=None) -> CharacterProfile:
        identity = getattr(bible, "identity", None)
        pa = getattr(bible, "physical_appearance", None)
        behaviour = getattr(bible, "behaviour", None)

        canonical_name = getattr(identity, "canonical_name", "") or ""

        profile = CharacterProfile(
            canonical_name=canonical_name,
            visual_identity_id=visual_identity_id(canonical_name) if canonical_name else "",
            source_bible_version=getattr(bible, "schema_version", ""),
        )

        # --- apariencia física (solo lo que existe) ---
        if pa is not None:
            profile.age = getattr(pa, "approximate_age", "") or ""
            profile.age_range = _age_range_from(profile.age)
            profile.skin_tone = getattr(pa, "skin_tone", "") or ""
            profile.eye_color = getattr(pa, "eye_color", "") or ""
            profile.face_shape = getattr(pa, "face_shape", "") or ""
            profile.height = getattr(pa, "height", "") or ""
            profile.body_type = getattr(pa, "body_type", "") or ""
            hair = getattr(pa, "hair", "") or ""
            profile.hair_style = hair
            profile.hair_color = _extract_hair_color(hair)
            profile.facial_hair = getattr(pa, "beard", "") or ""
            profile.clothing_style = getattr(pa, "clothing_style", "") or ""
            profile.accessories = list(getattr(pa, "accessories", []) or [])

        # --- comportamiento visible ---
        if behaviour is not None:
            profile.posture = getattr(behaviour, "posture", "") or ""
            profile.expression = getattr(behaviour, "facial_expression", "") or ""
            profile.walking_style = getattr(behaviour, "movement_style", "") or ""
            # 'personality' es la lista de afecto disponible; se reutiliza tal cual.
            profile.typical_emotions = list(getattr(behaviour, "personality", []) or [])

        # --- referencias visuales (bible + evidence) — solo se registran ---
        profile.reference_images = self._collect_references(bible, evidence)

        # --- derivadas (constraints + reglas + cobertura) ---
        self._derive(profile)
        return profile

    # ---------------------------------------------------------------- internals

    def _collect_references(self, bible, evidence) -> list[ReferenceImage]:
        refs: list[ReferenceImage] = []
        for vr in getattr(bible, "visual_references", []) or []:
            refs.append(ReferenceImage(
                reference_id=getattr(vr, "id", "") or getattr(vr, "hash", "") or getattr(vr, "url", ""),
                provider=getattr(vr, "provider", ""),
                license=getattr(vr, "license", "") or getattr(vr, "copyright", ""),
                url=getattr(vr, "url", ""),
                hash=getattr(vr, "hash", ""),
                quality=float(getattr(vr, "quality_score", 0.0) or 0.0),
            ))
        # Enriquecimiento opcional desde el EvidenceGraph (imágenes), si está presente.
        for img in getattr(evidence, "images", []) or []:
            refs.append(ReferenceImage(
                reference_id=getattr(img, "id", "") or getattr(img, "url", ""),
                provider=getattr(img, "provider", "") or "evidence",
                license=getattr(img, "license", ""),
                url=getattr(img, "url", ""),
                hash=getattr(img, "hash", ""),
                quality=float(getattr(img, "quality_score", 0.0) or 0.0),
            ))
        return refs

    def _derive(self, profile: CharacterProfile) -> None:
        values = profile.attribute_values()

        # Constraints positivos: "etiqueta: valor" por atributo conocido.
        profile.visual_constraints = [f"{_LABELS[name]}: {values[name]}"
                                      for name, _ in VISUAL_ATTRIBUTES if name in values]

        # Negativos: base de identidad + "different <atributo>" por atributo conocido.
        negatives = list(_BASE_NEGATIVES)
        negatives += [f"different {_LABELS[name]}" for name, _ in VISUAL_ATTRIBUTES if name in values]
        profile.negative_constraints = negatives

        # Reglas de continuidad derivadas.
        profile.continuity_rules = derive_continuity_rules(profile)

        # Cobertura: atributos escalares conocidos / total.
        profile.known_attributes = (
            list(values.keys())
            + [n for n in ("typical_emotions", "accessories", "dominant_colors")
               if getattr(profile, n)]
        )
        profile.completeness = round(len(values) / len(VISUAL_ATTRIBUTES), 3)
