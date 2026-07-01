"""Parsing determinista de la información del canal (YIE).

De un dump por vídeo (yt-dlp) solo suelen venir id/nombre/suscriptores. Los totales del
canal (vistas/vídeos/fecha de creación) quedan ``UNKNOWN``/``None`` salvo que el
proveedor los aporte; ``average_views`` solo se calcula si hay totales reales.
"""

from app.yie import UNKNOWN
from app.yie.models import ChannelInfo


def _text(value) -> str:
    return value if isinstance(value, str) and value.strip() else UNKNOWN


def _num(value):
    return value if isinstance(value, (int, float)) else None


def parse_channel(raw: dict) -> ChannelInfo:
    raw = raw or {}
    total_views = _num(raw.get("channel_total_views"))
    total_videos = _num(raw.get("channel_total_videos"))
    average = (
        round(total_views / total_videos, 2)
        if total_views and total_videos else None
    )
    return ChannelInfo(
        channel_id=_text(raw.get("channel_id")),
        channel_name=_text(raw.get("channel") or raw.get("uploader")),
        subscribers=_num(raw.get("channel_follower_count")),
        total_views=total_views,
        total_videos=total_videos,
        country=_text(raw.get("channel_country") or raw.get("country")),
        created_at=_text(raw.get("channel_created_at")),
        average_views=average,
        upload_frequency=UNKNOWN,        # no se infiere aquí (reservado)
    )
