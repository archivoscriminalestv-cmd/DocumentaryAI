"""Modelos del Character Consistency Engine (CCE).

``CharacterProfile`` es la IDENTIDAD VISUAL permanente de un personaje: solo atributos
visuales, serializable, versionada y reproducible (sin marcas de tiempo). Todos los
campos tienen defaults vacíos para permitir perfiles PARCIALES (cuando hay pocos
datos) sin inventar nada.

Independiente del proveedor: aquí no hay sintaxis de Imagen/Flux/SDXL. Los adapters
del VPL traducirán más tarde; el CCE solo describe restricciones en lenguaje neutro.
"""

import hashlib
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

from app.cce import SCHEMA_VERSION


def slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name or "")
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = "".join(ch if ch.isalnum() else "_" for ch in ascii_only)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "unknown"


def visual_identity_id(canonical_name: str) -> str:
    """Identidad visual estable y permanente derivada del nombre (determinista).

    El mismo personaje produce SIEMPRE el mismo id, independientemente del proveedor.
    """
    digest = hashlib.sha256(slugify(canonical_name).encode("utf-8")).hexdigest()[:12]
    return f"vid_{digest}"


# Atributos visuales escalares (field, etiqueta legible). Orden = orden del bloque de
# identidad. Las listas (typical_emotions/accessories/dominant_colors/reference_images)
# se tratan aparte.
VISUAL_ATTRIBUTES: tuple[tuple[str, str], ...] = (
    ("age", "age"),
    ("age_range", "age range"),
    ("gender", "gender"),
    ("ethnicity", "ethnicity"),
    ("skin_tone", "skin tone"),
    ("eye_color", "eye colour"),
    ("hair_color", "hair colour"),
    ("hair_style", "hairstyle"),
    ("facial_hair", "facial hair"),
    ("face_shape", "face shape"),
    ("nose", "nose"),
    ("mouth", "mouth"),
    ("ears", "ears"),
    ("eyebrows", "eyebrows"),
    ("wrinkles", "wrinkles"),
    ("scars", "scars"),
    ("tattoos", "tattoos"),
    ("height", "height"),
    ("body_type", "body type"),
    ("posture", "posture"),
    ("walking_style", "walking style"),
    ("expression", "expression"),
    ("clothing_style", "clothing style"),
)

# Atributos que la historia PUEDE cambiar (la ropa evoluciona si el guion lo pide);
# el resto son inmutables (la identidad de la persona no cambia).
MUTABLE_ATTRIBUTES: frozenset[str] = frozenset({"clothing_style", "accessories"})


@dataclass
class ReferenceImage:
    """Referencia visual futura. Por ahora solo se registra (no se descarga)."""

    reference_id: str = ""
    provider: str = ""
    license: str = ""
    url: str = ""
    hash: str = ""
    quality: float = 0.0


@dataclass
class ContinuityRule:
    """Regla de continuidad DERIVADA del perfil (no escrita a mano).

    ``severity``: ``locked`` (no puede cambiar) | ``soft`` (puede evolucionar si la
    historia lo exige). ``directive`` es el fragmento neutro que usará el prompt.
    """

    attribute: str
    severity: str          # locked | soft
    directive: str
    value: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CharacterProfile:
    """Identidad visual permanente (fuente de verdad de consistencia)."""

    schema_version: str = SCHEMA_VERSION
    # --- identidad ---
    canonical_name: str = ""
    visual_identity_id: str = ""
    source_bible_version: str = ""
    # --- atributos visuales escalares ---
    age: str = ""
    age_range: str = ""
    gender: str = ""
    ethnicity: str = ""
    skin_tone: str = ""
    eye_color: str = ""
    hair_color: str = ""
    hair_style: str = ""
    facial_hair: str = ""
    face_shape: str = ""
    nose: str = ""
    mouth: str = ""
    ears: str = ""
    eyebrows: str = ""
    wrinkles: str = ""
    scars: str = ""
    tattoos: str = ""
    height: str = ""
    body_type: str = ""
    posture: str = ""
    walking_style: str = ""
    expression: str = ""
    clothing_style: str = ""
    # --- atributos de lista ---
    typical_emotions: list[str] = field(default_factory=list)
    accessories: list[str] = field(default_factory=list)
    dominant_colors: list[str] = field(default_factory=list)
    # --- referencias y restricciones (derivadas) ---
    reference_images: list[ReferenceImage] = field(default_factory=list)
    visual_constraints: list[str] = field(default_factory=list)
    negative_constraints: list[str] = field(default_factory=list)
    continuity_rules: list[ContinuityRule] = field(default_factory=list)
    # --- metadatos ---
    provider_metadata: dict[str, Any] = field(default_factory=dict)
    completeness: float = 0.0           # 0..1 atributos visuales conocidos
    known_attributes: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------ helpers

    def attribute_values(self) -> dict[str, str]:
        """Atributos escalares conocidos (no vacíos), en orden canónico."""
        out: dict[str, str] = {}
        for name, _label in VISUAL_ATTRIBUTES:
            value = str(getattr(self, name, "") or "").strip()
            if value:
                out[name] = value
        return out

    def is_partial(self) -> bool:
        return self.completeness < 1.0

    # ------------------------------------------------------------------ (de)serialización

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterProfile":
        known = {f for f in cls.__dataclass_fields__}
        kwargs = {k: v for k, v in data.items() if k in known}
        kwargs["reference_images"] = [
            ReferenceImage(**r) for r in data.get("reference_images", [])
        ]
        kwargs["continuity_rules"] = [
            ContinuityRule(**r) for r in data.get("continuity_rules", [])
        ]
        return cls(**kwargs)
