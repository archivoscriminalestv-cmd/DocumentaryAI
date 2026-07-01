"""EvidenceService — orquesta la extracción sobre muchas fuentes (Sprint C-04).

Aplicación pura: entra ``list[RetrievedSource]``, sale ``list[ExtractedEvidence]``.
Reasigna ids globales deterministas (``ev-01``, ``ev-02``, …) sobre el resultado
agregado. Nunca rompe: una fuente inválida se omite y el resto continúa.
Sin IA, sin red.
"""

from app.application.evidence_extractor import EvidenceExtractor
from app.domain.evidence.extracted_evidence import ExtractedEvidence


class EvidenceService:
    def __init__(self, extractor: EvidenceExtractor | None = None) -> None:
        self._extractor = extractor or EvidenceExtractor()

    def extract_all(self, sources: list) -> list[ExtractedEvidence]:
        collected: list[ExtractedEvidence] = []
        for source in sources or []:
            try:
                collected.extend(self._extractor.extract(source))
            except Exception:
                continue  # fuente inválida -> se omite con seguridad

        for index, evidence in enumerate(collected, start=1):
            evidence.id = f"ev-{index:02d}"
        return collected
