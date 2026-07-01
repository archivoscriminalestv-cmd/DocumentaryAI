"""Proveedor Internet Archive (contrato; vídeo/audio/documentos archivados). Sin red."""

from app.eae.models import EvidenceKind
from app.eae.providers.base import BaseEvidenceProvider


class InternetArchiveProvider(BaseEvidenceProvider):
    name = "internet_archive"
    kinds = (EvidenceKind.VIDEO, EvidenceKind.AUDIO, EvidenceKind.DOCUMENT, EvidenceKind.PDF)
