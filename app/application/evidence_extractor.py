"""EvidenceExtractor — heurística determinista RetrievedSource -> Evidence (C-04).

Sin IA, sin red. Trocea el texto de la fuente en frases, conserva las
significativas (longitud > 40) como ``claim`` y asigna una confianza según el
tipo de fuente. Nunca lanza: ante cualquier problema devuelve ``[]``.
"""

import re

from app.domain.evidence.extracted_evidence import ExtractedEvidence
from app.domain.search import SearchType

# Confianza por tipo de fuente (heurística fija del sprint).
_CONFIDENCE: dict[SearchType, float] = {
    SearchType.WIKIPEDIA: 0.9,
    SearchType.YOUTUBE: 0.7,
    SearchType.NEWS: 0.85,
    SearchType.ACADEMIC: 0.95,
    SearchType.ARCHIVES: 0.8,
}
_OTHER_CONFIDENCE = 0.6

_MIN_CLAIM_LEN = 40
_CONTEXT_MAX = 300
_SPLIT = re.compile(r"[.\n;]")


class EvidenceExtractor:
    def extract(self, source) -> list[ExtractedEvidence]:
        try:
            text = self._source_text(source)
            if not text:
                return []

            confidence = _CONFIDENCE.get(getattr(source, "type", None), _OTHER_CONFIDENCE)
            source_id = str(getattr(source, "id", "") or "")
            context = self._context(text)

            evidence: list[ExtractedEvidence] = []
            seq = 0
            for fragment in _SPLIT.split(text):
                claim = fragment.strip()
                if len(claim) <= _MIN_CLAIM_LEN:
                    continue
                seq += 1
                evidence.append(
                    ExtractedEvidence(
                        id=f"ev-{seq:02d}",
                        source_id=source_id,
                        claim=claim,
                        context=context,
                        confidence=confidence,
                    )
                )
            return evidence
        except Exception:
            return []  # fuente inválida -> se omite con seguridad

    @staticmethod
    def _source_text(source) -> str:
        # ``RetrievedSource`` expone ``snippet``; admitimos ``content`` por si
        # una fuente futura lo trae.
        text = getattr(source, "content", None) or getattr(source, "snippet", "")
        return str(text or "").strip()

    @staticmethod
    def _context(text: str) -> str:
        normalized = " ".join(text.split())
        if len(normalized) <= _CONTEXT_MAX:
            return normalized
        return normalized[:_CONTEXT_MAX].rstrip() + "…"
