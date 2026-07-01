"""Modelos del DocumentaryDossier (ERE-003).

Serializable, versionado y reproducible. Las evidencias (noticias, imágenes, vídeos,
documentos) se mantienen INDIVIDUALMENTE (no se fusionan). Cada afirmación lleva
procedencia (ver ``DossierClaim``). Sin inferencias ni narrativa.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.dossier import SCHEMA_VERSION
from app.dossier.claims import DossierClaim


@dataclass
class Person:
    id: str
    name: str = ""
    aliases: list[str] = field(default_factory=list)
    # hechos atribuidos (birth_date, death_date, nationality, occupation, age, appearance…)
    attributes: dict[str, list[DossierClaim]] = field(default_factory=dict)
    family: list[DossierClaim] = field(default_factory=list)
    friends: list[DossierClaim] = field(default_factory=list)
    bands: list[DossierClaim] = field(default_factory=list)
    organizations: list[DossierClaim] = field(default_factory=list)
    usual_locations: list[str] = field(default_factory=list)  # ids de Location
    photos: list[str] = field(default_factory=list)           # ids de MediaImage
    videos: list[str] = field(default_factory=list)           # ids de MediaVideo


@dataclass
class TimelineEvent:
    id: str
    date: str = ""
    time: str = ""
    description: str = ""
    location_id: str = ""
    entity_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0
    provider: str = ""
    source_url: str = ""
    license: str = ""


@dataclass
class Location:
    id: str
    name: str = ""
    type: str = ""
    coordinates: str = ""  # reservado (sin geocodificación inventada)
    photos: list[str] = field(default_factory=list)
    confidence: float = 0.0
    provider: str = ""
    source_url: str = ""


@dataclass
class MediaImage:
    id: str
    url: str = ""
    thumbnail_url: str = ""
    license: str = ""
    author: str = ""
    caption: str = ""
    resolution: str = ""
    hash: str = ""          # pendiente (sin descarga)
    provider: str = ""
    confidence: float = 0.0
    relevance: float = 0.0


@dataclass
class MediaVideo:
    id: str
    url: str = ""
    title: str = ""
    channel: str = ""
    duration: str = ""
    published: str = ""
    thumbnail_url: str = ""
    license: str = ""
    hash: str = ""          # pendiente (sin descarga)
    provider: str = ""
    confidence: float = 0.0


@dataclass
class NewsItem:
    id: str
    headline: str = ""
    medium: str = ""
    date: str = ""
    url: str = ""
    snippet: str = ""
    entities_detected: list[str] = field(default_factory=list)
    provider: str = ""
    confidence: float = 0.0
    license: str = ""


@dataclass
class CourtItem:
    id: str
    title: str = ""
    reference: str = ""
    court: str = ""
    date: str = ""
    url: str = ""
    provider: str = ""
    confidence: float = 0.0


@dataclass
class Conflict:
    type: str          # date | place | name | generic
    subject: str       # id de la entidad/evento afectado
    field: str
    candidates: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DossierSource:
    provider: str = ""
    url: str = ""
    source: str = ""
    confidence: float = 0.0
    license: str = ""


@dataclass
class DocumentaryDossier:
    schema_version: str = SCHEMA_VERSION
    project: dict[str, Any] = field(default_factory=dict)
    people: list[Person] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)
    locations: list[Location] = field(default_factory=list)
    media_images: list[MediaImage] = field(default_factory=list)
    media_videos: list[MediaVideo] = field(default_factory=list)
    news: list[NewsItem] = field(default_factory=list)
    court_documents: list[CourtItem] = field(default_factory=list)
    publications: list[dict[str, Any]] = field(default_factory=list)  # reservado
    relationships: list[dict[str, Any]] = field(default_factory=list)  # grafo (aristas)
    conflicts: list[Conflict] = field(default_factory=list)
    sources: list[DossierSource] = field(default_factory=list)
    providers_used: list[str] = field(default_factory=list)
    coverage: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentaryDossier":
        def _claim(d: dict) -> DossierClaim:
            return DossierClaim(**d)

        def _person(d: dict) -> Person:
            return Person(
                id=d["id"], name=d.get("name", ""), aliases=list(d.get("aliases", [])),
                attributes={
                    k: [_claim(c) for c in v]
                    for k, v in (d.get("attributes", {}) or {}).items()
                },
                family=[_claim(c) for c in d.get("family", [])],
                friends=[_claim(c) for c in d.get("friends", [])],
                bands=[_claim(c) for c in d.get("bands", [])],
                organizations=[_claim(c) for c in d.get("organizations", [])],
                usual_locations=list(d.get("usual_locations", [])),
                photos=list(d.get("photos", [])),
                videos=list(d.get("videos", [])),
            )

        return cls(
            schema_version=data.get("schema_version", SCHEMA_VERSION),
            project=dict(data.get("project", {})),
            people=[_person(p) for p in data.get("people", [])],
            timeline=[TimelineEvent(**e) for e in data.get("timeline", [])],
            locations=[Location(**loc) for loc in data.get("locations", [])],
            media_images=[MediaImage(**i) for i in data.get("media_images", [])],
            media_videos=[MediaVideo(**v) for v in data.get("media_videos", [])],
            news=[NewsItem(**n) for n in data.get("news", [])],
            court_documents=[CourtItem(**c) for c in data.get("court_documents", [])],
            publications=[dict(p) for p in data.get("publications", [])],
            relationships=[dict(r) for r in data.get("relationships", [])],
            conflicts=[Conflict(**c) for c in data.get("conflicts", [])],
            sources=[DossierSource(**s) for s in data.get("sources", [])],
            providers_used=list(data.get("providers_used", [])),
            coverage=dict(data.get("coverage", {})),
        )
