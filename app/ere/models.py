"""Modelos del Evidence Research Engine (ERE).

``EvidenceGraph`` es un grafo de evidencia serializable, reproducible y versionado:
entidades (personajes, lugares, organizaciones), eventos/fechas, artículos de
prensa, imágenes, vídeos, documentos judiciales y **relaciones** entre nodos. Cada
dato lleva su procedencia (``SourceRef``) y su confianza; los desacuerdos se
conservan (no se decide). La marca temporal vive en el manifest, no en el grafo.
"""

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

from app.ere import SCHEMA_VERSION


def slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name or "")
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = "".join(ch if ch.isalnum() else "_" for ch in ascii_only)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "unknown"


@dataclass
class ProjectQuery:
    """Entrada de investigación: el caso a documentar."""
    name: str
    location: str = ""
    date: str = ""
    aliases: list[str] = field(default_factory=list)
    hints: dict[str, str] = field(default_factory=dict)

    def subject_id(self) -> str:
        return f"character:{slugify(self.name)}"


@dataclass
class SourceRef:
    """Procedencia de un dato. Nada se guarda sin SourceRef."""
    provider: str = ""
    url: str = ""
    source: str = ""        # etiqueta legible / medio
    confidence: float = 0.0
    license: str = ""
    hash: str = ""          # reservado (sin descarga)
    retrieved_at: str = ""  # reservado: vacío en el grafo para preservar reproducibilidad


@dataclass
class Claim:
    """Valor atribuido a un campo, con procedencia. Permite conservar conflictos."""
    field: str
    value: Any
    provider: str
    confidence: float
    source: str = ""  # url o id de fuente


@dataclass
class Entity:
    id: str
    type: str = "character"  # character | location | organization | ...
    canonical_name: str = ""
    aliases: list[str] = field(default_factory=list)
    attributes: dict[str, list[Claim]] = field(default_factory=dict)  # campo -> claims
    references: list[str] = field(default_factory=list)  # ids de assets relacionados
    sources: list[SourceRef] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Event:
    id: str
    description: str = ""
    date: str = ""
    location_id: str = ""
    entity_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0
    sources: list[SourceRef] = field(default_factory=list)


@dataclass
class Article:
    id: str
    headline: str = ""
    medium: str = ""
    date: str = ""
    url: str = ""
    snippet: str = ""
    entities_detected: list[str] = field(default_factory=list)
    source: SourceRef = field(default_factory=SourceRef)


@dataclass
class ImageAsset:
    id: str
    provider: str = ""
    thumbnail_url: str = ""
    original_url: str = ""
    license: str = ""
    author: str = ""
    caption: str = ""
    resolution: str = ""
    hash: str = ""          # reservado: sin descarga
    quality: float = 0.0
    relevance: float = 0.0


@dataclass
class VideoAsset:
    id: str
    provider: str = ""
    title: str = ""
    url: str = ""
    channel: str = ""
    duration: str = ""
    published: str = ""
    thumbnail_url: str = ""
    license: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CourtDocument:
    """Referencia PÚBLICA a documentación judicial. Nunca se interpreta su contenido."""
    id: str
    provider: str = ""
    title: str = ""
    reference: str = ""  # número/identificador público
    court: str = ""
    date: str = ""
    url: str = ""


@dataclass
class Relationship:
    source_id: str
    relation: str  # appeared_in | mentions | located_in | alias_of | has_reference | ...
    target_id: str
    provider: str = ""
    confidence: float = 0.0


@dataclass
class EvidenceGraph:
    schema_version: str = SCHEMA_VERSION
    project: ProjectQuery = field(default_factory=lambda: ProjectQuery(name=""))
    entities: list[Entity] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    articles: list[Article] = field(default_factory=list)
    images: list[ImageAsset] = field(default_factory=list)
    videos: list[VideoAsset] = field(default_factory=list)
    court_documents: list[CourtDocument] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    providers_used: list[str] = field(default_factory=list)
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceGraph":
        def _src(d: dict) -> SourceRef:
            return SourceRef(**d)

        def _entity(d: dict) -> Entity:
            attrs = {
                fname: [Claim(**c) for c in claims]
                for fname, claims in (d.get("attributes", {}) or {}).items()
            }
            return Entity(
                id=d["id"],
                type=d.get("type", "character"),
                canonical_name=d.get("canonical_name", ""),
                aliases=list(d.get("aliases", [])),
                attributes=attrs,
                references=list(d.get("references", [])),
                sources=[_src(s) for s in d.get("sources", [])],
                metadata=dict(d.get("metadata", {})),
            )

        return cls(
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            project=ProjectQuery(**data.get("project", {"name": ""})),
            entities=[_entity(e) for e in data.get("entities", [])],
            events=[
                Event(
                    **{**e, "sources": [_src(s) for s in e.get("sources", [])]}
                )
                for e in data.get("events", [])
            ],
            articles=[
                Article(**{**a, "source": _src(a.get("source", {}))})
                for a in data.get("articles", [])
            ],
            images=[ImageAsset(**i) for i in data.get("images", [])],
            videos=[VideoAsset(**v) for v in data.get("videos", [])],
            court_documents=[CourtDocument(**c) for c in data.get("court_documents", [])],
            relationships=[Relationship(**r) for r in data.get("relationships", [])],
            conflicts=[dict(c) for c in data.get("conflicts", [])],
            providers_used=list(data.get("providers_used", [])),
            sources=[_src(s) for s in data.get("sources", [])],
        )
