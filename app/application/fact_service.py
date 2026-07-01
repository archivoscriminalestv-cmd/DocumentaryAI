"""FactService — consolida ExtractedEvidence[] -> ConsolidatedFact[] (Sprint C-05).

Capa de consolidación DETERMINISTA, sin IA y sin inventar nada:

- Agrupa evidencias léxicamente equivalentes (solapamiento de tokens
  significativos) en un único hecho — no un hecho por evidencia.
- ``statement`` = la afirmación MÁS SIMPLE del grupo, TAL CUAL aparece en la
  evidencia (verbatim) -> imposible introducir conocimiento externo.
- ``confidence`` = mínimo de las confianzas del grupo.
- Procedencia completa: ``evidence_ids`` (todas las del grupo) y ``source_ids``
  (derivados de ellas), deduplicados y en orden de entrada.
- Vacío/ inválido -> se omite con seguridad; sin evidencia válida -> ``[]``.

LÍMITE CONOCIDO: la equivalencia *sinónima* (p.ej. "accident" == "disaster")
requiere un LLM y queda fuera de esta capa determinista; aquí se fusiona lo
léxicamente cercano. La fusión semántica profunda llegará con la capa de IA.
"""

import re

from app.domain.fact.consolidated_fact import ConsolidatedFact

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "of", "in", "on", "at", "to", "and", "or", "is", "was",
    "were", "are", "be", "been", "it", "its", "that", "this", "these", "those",
    "for", "with", "as", "by", "from", "into", "near", "over", "after", "before",
}
_JACCARD_MIN = 0.5
_CONTAINMENT_MIN = 0.8


def _tokens(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS and len(w) > 1}


def _similar(a: set[str], b: set[str]) -> bool:
    if not a or not b:
        return False
    inter = len(a & b)
    if inter == 0:
        return False
    jaccard = inter / len(a | b)
    containment = inter / min(len(a), len(b))
    return jaccard >= _JACCARD_MIN or containment >= _CONTAINMENT_MIN


class _Item:
    __slots__ = ("claim", "tokens", "evidence_id", "source_id", "confidence")

    def __init__(self, claim, tokens, evidence_id, source_id, confidence):
        self.claim = claim
        self.tokens = tokens
        self.evidence_id = evidence_id
        self.source_id = source_id
        self.confidence = confidence


class FactService:
    def consolidate(self, evidence: list) -> list[ConsolidatedFact]:
        items = self._normalize_inputs(evidence)
        if not items:
            return []

        clusters = self._cluster(items)

        facts: list[ConsolidatedFact] = []
        for index, cluster in enumerate(clusters, start=1):
            facts.append(self._to_fact(f"fact-{index:02d}", cluster))
        return facts

    @staticmethod
    def _normalize_inputs(evidence: list) -> list[_Item]:
        items: list[_Item] = []
        for ev in evidence or []:
            try:
                claim = str(getattr(ev, "claim", "") or "").strip()
                if not claim:
                    continue  # evidencia inválida/ vacía -> se omite
                items.append(
                    _Item(
                        claim=claim,
                        tokens=_tokens(claim),
                        evidence_id=str(getattr(ev, "id", "") or ""),
                        source_id=str(getattr(ev, "source_id", "") or ""),
                        confidence=float(getattr(ev, "confidence", 0.0) or 0.0),
                    )
                )
            except Exception:
                continue
        return items

    @staticmethod
    def _cluster(items: list[_Item]) -> list[list[_Item]]:
        # Single-link greedy en orden de entrada -> determinista. Una afirmación
        # se une al primer grupo que contenga un miembro suficientemente similar.
        clusters: list[list[_Item]] = []
        for item in items:
            placed = False
            for cluster in clusters:
                if any(_similar(item.tokens, member.tokens) for member in cluster):
                    cluster.append(item)
                    placed = True
                    break
            if not placed:
                clusters.append([item])
        return clusters

    @staticmethod
    def _representative(cluster: list[_Item]) -> str:
        # "Prefiere la afirmación factual más simple": menos tokens, luego más
        # corta, luego la primera en orden de entrada. Verbatim (sin inventar).
        best_index, best = 0, cluster[0]
        for i, item in enumerate(cluster):
            key = (len(item.tokens), len(item.claim), i)
            best_key = (len(best.tokens), len(best.claim), best_index)
            if key < best_key:
                best_index, best = i, item
        return best.claim

    def _to_fact(self, fact_id: str, cluster: list[_Item]) -> ConsolidatedFact:
        evidence_ids: list[str] = []
        source_ids: list[str] = []
        for item in cluster:
            if item.evidence_id and item.evidence_id not in evidence_ids:
                evidence_ids.append(item.evidence_id)
            if item.source_id and item.source_id not in source_ids:
                source_ids.append(item.source_id)
        confidence = min(item.confidence for item in cluster)
        return ConsolidatedFact(
            id=fact_id,
            statement=self._representative(cluster),
            confidence=confidence,
            evidence_ids=evidence_ids,
            source_ids=source_ids,
        )
