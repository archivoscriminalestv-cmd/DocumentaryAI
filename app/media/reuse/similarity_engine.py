"""SimilarityEngine — reutilización por similitud de prompt (Fase 1 MGL).

Versión inicial SIN ML: compara prompts normalizados con una ratio determinista
(``difflib``). Está preparado para evolucionar a recuperación por embeddings sin
refactor: cuando los Assets tengan ``embedding``, este motor podrá usar la
similitud vectorial en lugar de (o además de) la textual, manteniendo la misma
firma pública ``find_similar_assets(prompt, threshold)``.
"""

import difflib

from app.media.store.asset_store import AssetStore
from app.media.store.models import Asset


class SimilarityEngine:
    def __init__(self, store: AssetStore) -> None:
        self._store = store

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join((text or "").lower().split())

    def similarity(self, a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, self._normalize(a), self._normalize(b)).ratio()

    def find_similar_assets(self, prompt: str, threshold: float = 0.85) -> list[Asset]:
        """Assets cuyo prompt supera el umbral de similitud, de mayor a menor.

        Placeholder para embeddings: si en el futuro ``asset.embedding`` existe, la
        puntuación podrá calcularse en el espacio vectorial sin cambiar esta firma.
        """
        scored: list[tuple[Asset, float]] = []
        for asset in self._store.all():
            score = self.similarity(prompt, asset.prompt)
            if score >= threshold:
                scored.append((asset, score))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [asset for asset, _ in scored]
