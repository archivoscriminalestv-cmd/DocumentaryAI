"""Modelos de inteligencia competitiva (YIE-002).

Serializables, versionados, reproducibles. ``UNKNOWN`` (texto) o ``None`` (numérico)
cuando no hay dato; nunca se inventa ni se estima.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.yie import UNKNOWN
from app.yie.intelligence import SCHEMA_VERSION


@dataclass
class ChannelIntelligence:
    schema_version: str = SCHEMA_VERSION
    channel_id: str = UNKNOWN
    channel_name: str = UNKNOWN
    subscribers: int | None = None
    total_videos: int | None = None
    total_views: int | None = None
    country: str = UNKNOWN
    creation_date: str = UNKNOWN
    channel_age_days: int | None = None
    verified: bool | None = None
    official_artist: bool | None = None
    custom_url: str = UNKNOWN
    channel_keywords: list[str] = field(default_factory=list)
    playlist_count: int | None = None
    # derivadas (solo fórmulas; None si faltan insumos)
    average_views_per_video: float | None = None
    uploads_per_year: float | None = None
    uploads_per_month: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AudienceMetrics:
    schema_version: str = SCHEMA_VERSION
    subscribers: int | None = None
    total_channel_views: int | None = None
    total_videos: int | None = None
    views_per_subscriber: float | None = None       # vistas del VÍDEO / subs
    subscribers_per_view: float | None = None
    channel_views_per_subscriber: float | None = None  # vistas del CANAL / subs
    average_views_per_video: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EngagementMetrics:
    schema_version: str = SCHEMA_VERSION
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    age_days: int | None = None
    views_per_day: float | None = None
    likes_per_view: float | None = None
    comments_per_view: float | None = None
    engagement_rate: float | None = None             # (likes + comments) / views
    like_velocity: float | None = None               # likes / día
    comment_velocity: float | None = None            # comentarios / día

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExtendedSeo:
    schema_version: str = SCHEMA_VERSION
    title_length: int = 0
    description_length: int = 0
    word_count: int = 0
    first_line_length: int = 0
    link_count: int = 0
    hashtag_count: int = 0
    tag_count: int = 0
    chapter_count: int = 0
    stopword_ratio: float = 0.0
    keyword_repetition: int = 0                       # máx. repeticiones de una palabra
    keyword_density: dict = field(default_factory=dict)  # palabra -> frecuencia relativa
    pinned_comment: str = UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExtendedThumbnail:
    schema_version: str = SCHEMA_VERSION
    available: bool = False
    width: int | None = None
    height: int | None = None
    aspect_ratio: float | None = None
    brightness: float | None = None
    contrast: float | None = None
    average_saturation: float | None = None
    color_temperature: str = UNKNOWN
    dominant_colors: list[str] = field(default_factory=list)
    color_palette: list[dict] = field(default_factory=list)  # [{color, fraction}]
    edge_density: float | None = None
    text_area_percentage: float | None = None
    safe_margin_edge_ratio: float | None = None       # bordes en el margen exterior / total
    histogram: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProviderCoverage:
    """Auditoría: de qué proveedor vino cada grupo de campos (o UNKNOWN)."""
    schema_version: str = SCHEMA_VERSION
    providers_available: list[str] = field(default_factory=list)
    providers_unavailable: list[str] = field(default_factory=list)
    by_field: dict = field(default_factory=dict)      # campo -> proveedor | "UNKNOWN"
    known_fields: int = 0
    unknown_fields: int = 0
    coverage_ratio: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
