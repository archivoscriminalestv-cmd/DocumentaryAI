"""ReuseEngine — reutilización semántica básica de assets (Fase 3, FASE 1 simple).

Decide si un prompt puede satisfacerse con un asset ya existente en lugar de
generar uno nuevo. SIN embeddings, SIN ML, SIN APIs: scoring determinista basado
en:

1. Similitud de prompt: solapamiento de tokens / keywords (score 0–1).
2. Coincidencia de metadatos: ``style_tags`` y ``scene_type`` (si existen).

``find_best_match`` devuelve el mejor asset cuyo score supere el umbral
(por defecto 0.75) o ``None``. Preparado para evolucionar a embeddings sin
cambiar la firma pública.
"""

import re
from typing import Optional

from app.media.store.models import Asset

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "at", "to", "and", "or", "is", "was",
    "were", "are", "be", "it", "its", "that", "this", "for", "with", "as", "by",
    "from", "into", "near", "over", "very", "image", "picture", "photo", "shot",
}
_DEFAULT_THRESHOLD = 0.75
_PROMPT_WEIGHT = 0.75
_STYLE_WEIGHT = 0.25
_SCENE_TYPE_BONUS = 0.1


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall((text or "").lower()) if len(w) >= 3 and w not in _STOPWORDS}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class ReuseEngine:
    def __init__(self, threshold: float = _DEFAULT_THRESHOLD) -> None:
        self._threshold = threshold

    def score(
        self,
        prompt: str,
        asset: Asset,
        *,
        scene_type: str | None = None,
        style_tags: list[str] | None = None,
    ) -> float:
        """Score de reutilización 0–1 entre ``prompt``/metadatos y un asset."""
        prompt_score = _jaccard(_tokens(prompt), _tokens(getattr(asset, "prompt", "")))

        asset_styles = [str(t).lower() for t in (getattr(asset, "style_tags", []) or [])]
        if style_tags and asset_styles:
            style_score = _jaccard(
                {str(t).lower() for t in style_tags}, set(asset_styles)
            )
            score = _PROMPT_WEIGHT * prompt_score + _STYLE_WEIGHT * style_score
        else:
            score = prompt_score

        asset_scene_type = getattr(asset, "scene_type", None)
        if scene_type and asset_scene_type and str(scene_type).lower() == str(asset_scene_type).lower():
            score = min(1.0, score + _SCENE_TYPE_BONUS)

        return score

    def find_best_match(
        self,
        prompt: str,
        asset_store,
        *,
        media_type: str | None = None,
        threshold: float | None = None,
        scene_type: str | None = None,
        style_tags: list[str] | None = None,
    ) -> Optional[Asset]:
        """Mejor asset reutilizable cuyo score >= umbral; ``None`` si no hay match."""
        cutoff = self._threshold if threshold is None else threshold
        best: Asset | None = None
        best_score = 0.0
        for asset in asset_store.all():
            if media_type is not None and getattr(asset, "type", None) != media_type:
                continue
            value = self.score(prompt, asset, scene_type=scene_type, style_tags=style_tags)
            if value >= cutoff and value > best_score:
                best, best_score = asset, value
        return best


# Función de conveniencia con la firma del sprint: find_best_match(prompt, store).
_DEFAULT_ENGINE = ReuseEngine()


def find_best_match(
    prompt: str,
    asset_store,
    *,
    media_type: str | None = None,
    threshold: float = _DEFAULT_THRESHOLD,
    scene_type: str | None = None,
    style_tags: list[str] | None = None,
) -> Optional[Asset]:
    return _DEFAULT_ENGINE.find_best_match(
        prompt,
        asset_store,
        media_type=media_type,
        threshold=threshold,
        scene_type=scene_type,
        style_tags=style_tags,
    )
