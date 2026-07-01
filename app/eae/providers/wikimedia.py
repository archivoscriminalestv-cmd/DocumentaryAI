"""Proveedor Wikimedia/Commons (contrato; fotos/mapas con licencia). Sin red."""

from app.eae.models import EvidenceKind
from app.eae.providers.base import BaseEvidenceProvider


class WikimediaProvider(BaseEvidenceProvider):
    name = "wikimedia"
    kinds = (EvidenceKind.PHOTO, EvidenceKind.MAP, EvidenceKind.DOCUMENT)
