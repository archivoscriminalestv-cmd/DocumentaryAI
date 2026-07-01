"""Métricas de audiencia (YIE-002) — solo fórmulas matemáticas, sin inventar."""

from app.yie.intelligence.models import AudienceMetrics, ChannelIntelligence
from app.yie.models import VideoMetrics


def build_audience(channel: ChannelIntelligence, metrics: VideoMetrics) -> AudienceMetrics:
    subs = channel.subscribers
    views = metrics.views if isinstance(metrics.views, (int, float)) else None
    total_views = channel.total_views

    return AudienceMetrics(
        subscribers=subs,
        total_channel_views=total_views,
        total_videos=channel.total_videos,
        views_per_subscriber=round(views / subs, 4) if views and subs else None,
        subscribers_per_view=round(subs / views, 4) if subs and views else None,
        channel_views_per_subscriber=round(total_views / subs, 4) if total_views and subs else None,
        average_views_per_video=channel.average_views_per_video,
    )
