"""Parsing determinista de metadatos de vídeo (YIE).

Convierte el dict bruto del proveedor (estilo yt-dlp) en ``VideoMetadata`` y
``VideoMetrics``. Nunca inventa: lo ausente queda ``UNKNOWN`` (texto) o ``None``
(numérico). Provider-agnóstico (no asume de dónde vienen los datos).
"""

import re

from app.yie import UNKNOWN
from app.yie.models import VideoMetadata, VideoMetrics

_ID_RE = re.compile(r"(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{6,})")
_HASHTAG_RE = re.compile(r"#(\w+)")


def extract_video_id(url: str) -> str:
    match = _ID_RE.search(url or "")
    return match.group(1) if match else ""


def extract_hashtags(text: str) -> list[str]:
    seen: list[str] = []
    for tag in _HASHTAG_RE.findall(text or ""):
        low = tag.lower()
        if low not in seen:
            seen.append(low)
    return seen


def _text(value) -> str:
    return value if isinstance(value, str) and value.strip() else UNKNOWN


def _num(value):
    return value if isinstance(value, (int, float)) else None


def _publish_date(raw: dict) -> str:
    # yt-dlp: 'upload_date' = "YYYYMMDD"; o 'release_date'. Si no, UNKNOWN.
    date = raw.get("upload_date") or raw.get("release_date") or ""
    if isinstance(date, str) and len(date) == 8 and date.isdigit():
        return f"{date[:4]}-{date[4:6]}-{date[6:]}"
    return _text(date or None)


def parse_video(raw: dict) -> VideoMetadata:
    raw = raw or {}
    title = _text(raw.get("title"))
    description = _text(raw.get("description"))
    width, height = raw.get("width"), raw.get("height")
    categories = raw.get("categories") or []
    chapters_raw = raw.get("chapters") or []
    subtitles = raw.get("subtitles") or {}
    text_for_tags = " ".join(s for s in (raw.get("title"), raw.get("description")) if s)
    return VideoMetadata(
        video_id=_text(raw.get("id")),
        title=title,
        description=description,
        publish_date=_publish_date(raw),
        duration=_num(raw.get("duration")),
        category=_text(categories[0]) if categories else UNKNOWN,
        language=_text(raw.get("language")),
        tags=[str(t) for t in (raw.get("tags") or [])],
        hashtags=extract_hashtags(text_for_tags),
        chapters=[
            {"title": str(c.get("title", "")),
             "start_time": c.get("start_time"), "end_time": c.get("end_time")}
            for c in chapters_raw if isinstance(c, dict)
        ],
        subtitles=sorted(subtitles.keys()) if isinstance(subtitles, dict) else [],
        license=_text(raw.get("license")),
        fps=_num(raw.get("fps")),
        resolution=f"{width}x{height}" if width and height else UNKNOWN,
    )


def parse_metrics(raw: dict) -> VideoMetrics:
    raw = raw or {}
    return VideoMetrics(
        views=_num(raw.get("view_count")),
        likes=_num(raw.get("like_count")),
        comments=_num(raw.get("comment_count")),
        duration=_num(raw.get("duration")),
    )
