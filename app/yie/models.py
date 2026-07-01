"""Modelos del YouTube Intelligence Engine (YIE).

Serializables, versionados y reproducibles. Lo que no se puede determinar vale
``UNKNOWN`` (campos de texto) o ``None`` (numéricos sin dato); nunca se inventa.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.yie import SCHEMA_VERSION, UNKNOWN


@dataclass
class VideoMetadata:
    video_id: str = UNKNOWN
    title: str = UNKNOWN
    description: str = UNKNOWN
    publish_date: str = UNKNOWN
    duration: float | None = None        # segundos
    category: str = UNKNOWN
    language: str = UNKNOWN
    tags: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    chapters: list[dict] = field(default_factory=list)
    subtitles: list[str] = field(default_factory=list)   # idiomas disponibles
    license: str = UNKNOWN
    fps: float | None = None
    resolution: str = UNKNOWN            # "WxH"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ChannelInfo:
    channel_id: str = UNKNOWN
    channel_name: str = UNKNOWN
    subscribers: int | None = None
    total_views: int | None = None
    total_videos: int | None = None
    country: str = UNKNOWN
    created_at: str = UNKNOWN
    average_views: float | None = None       # total_views / total_videos (si ambos)
    upload_frequency: str = UNKNOWN          # no inferido aquí; reservado

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VideoMetrics:
    views: int | None = None
    likes: int | None = None
    comments: int | None = None
    duration: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class YouTubeKnowledge:
    """Contenido de ``youtube.json`` (vídeo + canal + métricas brutas)."""
    schema_version: str = SCHEMA_VERSION
    video: VideoMetadata = field(default_factory=VideoMetadata)
    channel: ChannelInfo = field(default_factory=ChannelInfo)
    metrics: VideoMetrics = field(default_factory=VideoMetrics)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "video": self.video.to_dict(),
            "channel": self.channel.to_dict(),
            "metrics": self.metrics.to_dict(),
        }


@dataclass
class SeoAnalysis:
    schema_version: str = SCHEMA_VERSION
    title_length: int = 0
    title_word_count: int = 0
    description_word_count: int = 0
    uppercase_ratio: float = 0.0
    has_numbers: bool = False
    has_year: bool = False
    is_question: bool = False
    emoji_count: int = 0
    has_emoji: bool = False
    hashtag_count: int = 0
    tag_count: int = 0
    significant_words: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ThumbnailAnalysis:
    schema_version: str = SCHEMA_VERSION
    available: bool = False
    width: int | None = None
    height: int | None = None
    resolution: str = UNKNOWN
    brightness: float | None = None
    contrast: float | None = None
    saturation: float | None = None
    color_temperature: str = UNKNOWN     # warm | cool | neutral
    dominant_color: str = UNKNOWN        # "#rrggbb"
    text_percentage: float | None = None # estimación por densidad de bordes
    histogram: dict = field(default_factory=dict)  # {"r":[...], "g":[...], "b":[...]}

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PopularityMetrics:
    schema_version: str = SCHEMA_VERSION
    reference_date: str = UNKNOWN        # fecha usada para los cálculos temporales
    age_days: int | None = None
    views_per_day: float | None = None
    likes_per_view: float | None = None
    comments_per_view: float | None = None
    engagement_rate: float | None = None # (likes + comments) / views

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
