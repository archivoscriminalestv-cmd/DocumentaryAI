"""SEO extendido (YIE-002) — reglas deterministas, sin IA.

Reutiliza el tokenizador y las stopwords del SEO base (YIE-001, no se modifica) y añade
métricas: longitudes, enlaces, primera línea, densidad/repetición de palabras clave,
ratio de stopwords, capítulos y pinned comment (si un proveedor lo aporta).
"""

import re

from app.yie import UNKNOWN
from app.yie.intelligence.models import ExtendedSeo
from app.yie.models import VideoMetadata
from app.yie.seo import _STOPWORDS, _WORD_RE   # reutilizado del YIE-001 (sin modificarlo)

_LINK_RE = re.compile(r"https?://\S+")


def analyze_seo_extended(video: VideoMetadata, enrichment: dict | None = None) -> ExtendedSeo:
    enr = enrichment or {}
    title = "" if video.title == UNKNOWN else video.title
    description = "" if video.description == UNKNOWN else video.description

    words = _WORD_RE.findall((title + " " + description).lower())
    total = len(words)
    stopwords = sum(1 for w in words if w in _STOPWORDS)

    counts: dict[str, int] = {}
    for word in words:
        if len(word) >= 3 and word not in _STOPWORDS:
            counts[word] = counts.get(word, 0) + 1
    keyword_repetition = max(counts.values(), default=0)
    density = {
        w: round(counts[w] / total, 4)
        for w in sorted(counts, key=lambda x: (-counts[x], x))[:15]
    } if total else {}

    first_line = description.split("\n", 1)[0] if description else ""

    return ExtendedSeo(
        title_length=len(title),
        description_length=len(description),
        word_count=total,
        first_line_length=len(first_line),
        link_count=len(_LINK_RE.findall(description)),
        hashtag_count=len(video.hashtags),
        tag_count=len(video.tags),
        chapter_count=len(video.chapters),
        stopword_ratio=round(stopwords / total, 4) if total else 0.0,
        keyword_repetition=keyword_repetition,
        keyword_density=density,
        pinned_comment=enr.get("pinned_comment") if isinstance(enr.get("pinned_comment"), str) else UNKNOWN,
    )
