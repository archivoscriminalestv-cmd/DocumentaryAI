"""Análisis SEO determinista (YIE) — solo reglas, sin IA.

Mide propiedades objetivas del título/descripción/tags: longitud, mayúsculas, números,
años, preguntas, emojis, y extrae palabras significativas (frecuencia, sin stopwords).
"""

import re

from app.yie import UNKNOWN
from app.yie.models import SeoAnalysis, VideoMetadata

_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)    # secuencias de letras (cualquier idioma)
_YEAR_RE = re.compile(r"\b(?:18|19|20)\d{2}\b")

# Stopwords genéricas multi-idioma (no específicas de ningún nicho).
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are",
    "this", "that", "it", "as", "at", "by", "from", "be", "was", "were",
    "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "de", "del", "a",
    "en", "con", "es", "son", "que", "se", "su", "sus", "por", "para", "al", "lo",
}


def _is_emoji(ch: str) -> bool:
    code = ord(ch)
    return (
        0x1F300 <= code <= 0x1FAFF      # símbolos & pictogramas, emoticonos, etc.
        or 0x2600 <= code <= 0x27BF     # misceláneos & dingbats
        or 0x1F1E6 <= code <= 0x1F1FF   # banderas regionales
    )


def analyze_seo(video: VideoMetadata) -> SeoAnalysis:
    title = "" if video.title == UNKNOWN else video.title
    description = "" if video.description == UNKNOWN else video.description

    letters = [c for c in title if c.isalpha()]
    uppercase = [c for c in letters if c.isupper()]
    uppercase_ratio = round(len(uppercase) / len(letters), 4) if letters else 0.0

    emoji_count = sum(1 for c in title + description if _is_emoji(c))

    counts: dict[str, int] = {}
    for word in _WORD_RE.findall((title + " " + description).lower()):
        if len(word) >= 3 and word not in _STOPWORDS:
            counts[word] = counts.get(word, 0) + 1
    significant = sorted(counts, key=lambda w: (-counts[w], w))[:25]

    return SeoAnalysis(
        title_length=len(title),
        title_word_count=len(title.split()),
        description_word_count=len(description.split()),
        uppercase_ratio=uppercase_ratio,
        has_numbers=any(c.isdigit() for c in title),
        has_year=bool(_YEAR_RE.search(title)),
        is_question="?" in title,
        emoji_count=emoji_count,
        has_emoji=emoji_count > 0,
        hashtag_count=len(video.hashtags),
        tag_count=len(video.tags),
        significant_words=significant,
    )
