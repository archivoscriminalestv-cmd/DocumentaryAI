"""Proveedor de fuentes oficiales/gubernamentales (contrato; archivos judiciales,
publicaciones oficiales, comunicados). Sin red."""

from app.eae.models import EvidenceKind
from app.eae.providers.base import BaseEvidenceProvider


class GovernmentProvider(BaseEvidenceProvider):
    name = "government"
    kinds = (EvidenceKind.COURT_RECORD, EvidenceKind.OFFICIAL_PUBLICATION,
             EvidenceKind.STATEMENT, EvidenceKind.PDF)
