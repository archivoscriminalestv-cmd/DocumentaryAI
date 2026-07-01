"""Popularidad: métricas DERIVADAS deterministas (YIE).

Calcula views_per_day, likes_per_view, comments_per_view, engagement_rate y age_days a
partir de las métricas brutas. NO crea un score con pesos arbitrarios: solo almacena las
métricas derivadas. Las métricas temporales usan una ``reference_date`` EXPLÍCITA para
ser reproducibles (misma URL + misma fecha → mismos valores).
"""

from datetime import date

from app.yie import UNKNOWN
from app.yie.models import PopularityMetrics, VideoMetrics


def _parse_date(value: str):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def compute_popularity(
    metrics: VideoMetrics, publish_date: str, reference_date: date
) -> PopularityMetrics:
    published = _parse_date(publish_date)
    age_days = (reference_date - published).days if published else None

    views = metrics.views if isinstance(metrics.views, (int, float)) else None
    likes = metrics.likes if isinstance(metrics.likes, (int, float)) else None
    comments = metrics.comments if isinstance(metrics.comments, (int, float)) else None

    views_per_day = (
        round(views / age_days, 4) if views and age_days and age_days > 0 else None
    )
    likes_per_view = round(likes / views, 6) if likes is not None and views else None
    comments_per_view = (
        round(comments / views, 6) if comments is not None and views else None
    )
    engagement_rate = (
        round((likes + comments) / views, 6)
        if likes is not None and comments is not None and views else None
    )

    return PopularityMetrics(
        reference_date=reference_date.isoformat() if reference_date else UNKNOWN,
        age_days=age_days,
        views_per_day=views_per_day,
        likes_per_view=likes_per_view,
        comments_per_view=comments_per_view,
        engagement_rate=engagement_rate,
    )
