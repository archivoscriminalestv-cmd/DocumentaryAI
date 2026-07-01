"""Métricas de engagement (YIE-002) — solo fórmulas matemáticas, sin inventar."""

from app.yie.intelligence.models import EngagementMetrics
from app.yie.models import VideoMetrics


def _n(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def build_engagement(metrics: VideoMetrics, age_days: int | None) -> EngagementMetrics:
    views, likes, comments = _n(metrics.views), _n(metrics.likes), _n(metrics.comments)
    positive_age = age_days if (age_days and age_days > 0) else None

    return EngagementMetrics(
        views=views, likes=likes, comments=comments, age_days=age_days,
        views_per_day=round(views / positive_age, 4) if views and positive_age else None,
        likes_per_view=round(likes / views, 6) if likes is not None and views else None,
        comments_per_view=round(comments / views, 6) if comments is not None and views else None,
        engagement_rate=round((likes + comments) / views, 6)
        if likes is not None and comments is not None and views else None,
        like_velocity=round(likes / positive_age, 4) if likes is not None and positive_age else None,
        comment_velocity=round(comments / positive_age, 4)
        if comments is not None and positive_age else None,
    )
