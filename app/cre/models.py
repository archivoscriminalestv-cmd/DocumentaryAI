"""Modelos del Character Research Engine (CRE).

``CharacterBible`` es la fuente de verdad de un personaje. Es serializable a JSON,
versionada y reproducible (no contiene marcas de tiempo; la traza temporal vive en
el manifest). Todos los campos tienen defaults vacíos para permitir construcción
parcial y fusión determinista entre proveedores.
"""

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

from app.cre import SCHEMA_VERSION


def slugify(name: str) -> str:
    """Identificador estable y portable a partir de un nombre (sin acentos)."""
    normalized = unicodedata.normalize("NFKD", name or "")
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = "".join(ch if ch.isalnum() else "_" for ch in ascii_only)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "unknown"


@dataclass
class CharacterRequest:
    name: str
    aliases: list[str] = field(default_factory=list)
    hints: dict[str, str] = field(default_factory=dict)  # pistas opcionales (no inventadas)


@dataclass
class VisualReference:
    # Campos CRE-001 (retrocompatibles).
    source: str = ""
    description: str = ""
    url: str = ""
    copyright: str = ""
    provider: str = ""
    # Campos CRE-002 (referencia visual rica; aún NO se descargan imágenes).
    id: str = ""
    license: str = ""
    caption: str = ""
    resolution: str = ""          # "WxH" cuando se conoce
    author: str = ""
    quality_score: float = 0.0    # métrica derivada (p.ej. resolución), no un hecho
    relevance_score: float = 0.0  # reservado para puntuación futura
    hash: str = ""                # reservado: hash del binario cuando exista descarga


@dataclass
class Identity:
    id: str = ""
    canonical_name: str = ""
    aliases: list[str] = field(default_factory=list)
    nationality: str = ""
    birth_date: str = ""
    death_date: str = ""
    occupation: str = ""


@dataclass
class Biography:
    summary: str = ""  # extracto enciclopédico (texto), no interpretado por IA
    timeline: list[str] = field(default_factory=list)
    important_events: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    relationships: list[str] = field(default_factory=list)


@dataclass
class PhysicalAppearance:
    approximate_age: str = ""
    height: str = ""
    body_type: str = ""
    face_shape: str = ""
    skin_tone: str = ""
    eye_color: str = ""
    hair: str = ""
    beard: str = ""
    clothing_style: str = ""
    accessories: list[str] = field(default_factory=list)


@dataclass
class Behaviour:
    personality: list[str] = field(default_factory=list)
    gestures: list[str] = field(default_factory=list)
    posture: str = ""
    facial_expression: str = ""
    movement_style: str = ""


@dataclass
class Voice:
    accent: str = ""
    speaking_style: str = ""
    emotional_profile: str = ""


@dataclass
class Environment:
    recurring_locations: list[str] = field(default_factory=list)
    recurring_objects: list[str] = field(default_factory=list)
    historical_period: str = ""


@dataclass
class CharacterBible:
    schema_version: str = SCHEMA_VERSION
    identity: Identity = field(default_factory=Identity)
    biography: Biography = field(default_factory=Biography)
    physical_appearance: PhysicalAppearance = field(default_factory=PhysicalAppearance)
    behaviour: Behaviour = field(default_factory=Behaviour)
    voice: Voice = field(default_factory=Voice)
    environment: Environment = field(default_factory=Environment)
    visual_references: list[VisualReference] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    providers_used: list[str] = field(default_factory=list)
    # Trazabilidad CRE-002: origen de cada dato escogido y discrepancias entre fuentes.
    # provenance: [{"field", "value", "provider", "confidence"}]
    provenance: list[dict[str, Any]] = field(default_factory=list)
    # conflicts: [{"field", "candidates": [{"value", "provider", "confidence"}]}]
    conflicts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterBible":
        return cls(
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            identity=Identity(**data.get("identity", {})),
            biography=Biography(**data.get("biography", {})),
            physical_appearance=PhysicalAppearance(**data.get("physical_appearance", {})),
            behaviour=Behaviour(**data.get("behaviour", {})),
            voice=Voice(**data.get("voice", {})),
            environment=Environment(**data.get("environment", {})),
            visual_references=[VisualReference(**v) for v in data.get("visual_references", [])],
            sources=list(data.get("sources", [])),
            providers_used=list(data.get("providers_used", [])),
            provenance=[dict(p) for p in data.get("provenance", [])],
            conflicts=[dict(c) for c in data.get("conflicts", [])],
        )
