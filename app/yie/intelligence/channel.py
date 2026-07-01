"""Inteligencia de canal (YIE-002) — solo extracción + fórmulas, sin inventar.

Combina lo que aporta el dump por vídeo (yt-dlp: id/nombre/suscriptores/verificado) con
lo que aporten los proveedores de enriquecimiento (totales del canal, fecha de creación,
playlists, keywords…). Lo ausente queda ``UNKNOWN``/``None``; las derivadas solo se
calculan si existen los insumos.
"""

from datetime import date

from app.yie import UNKNOWN
from app.yie.intelligence.models import ChannelIntelligence


def _num(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _text(value) -> str:
    return value if isinstance(value, str) and value.strip() else UNKNOWN


def _bool(value):
    return value if isinstance(value, bool) else None


def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def build_channel_intelligence(raw: dict, enrichment: dict, reference_date: date) -> ChannelIntelligence:
    raw = raw or {}
    enr = enrichment or {}

    subscribers = _num(raw.get("channel_follower_count")) or _num(enr.get("subscribers"))
    total_videos = _num(enr.get("total_videos"))
    total_views = _num(enr.get("total_views"))
    creation = _text(enr.get("creation_date"))
    created = _parse_date(creation if creation != UNKNOWN else None)
    age_days = (reference_date - created).days if created else None

    custom_url = raw.get("uploader_id") or enr.get("custom_url")
    custom_url = custom_url if isinstance(custom_url, str) and custom_url.startswith("@") else _text(enr.get("custom_url"))

    avg_views = round(total_views / total_videos, 2) if total_views and total_videos else None
    years = (age_days / 365.25) if age_days and age_days > 0 else None
    months = (age_days / 30.4375) if age_days and age_days > 0 else None

    return ChannelIntelligence(
        channel_id=_text(raw.get("channel_id")),
        channel_name=_text(raw.get("channel") or raw.get("uploader")),
        subscribers=subscribers,
        total_videos=total_videos,
        total_views=total_views,
        country=_text(raw.get("channel_country") or enr.get("country")),
        creation_date=creation,
        channel_age_days=age_days,
        verified=_bool(raw.get("channel_is_verified")) if "channel_is_verified" in raw else _bool(enr.get("verified")),
        official_artist=_bool(enr.get("official_artist")),
        custom_url=custom_url,
        channel_keywords=list(enr.get("channel_keywords") or []),
        playlist_count=_num(enr.get("playlist_count")),
        average_views_per_video=avg_views,
        uploads_per_year=round(total_videos / years, 3) if total_videos and years else None,
        uploads_per_month=round(total_videos / months, 3) if total_videos and months else None,
    )
