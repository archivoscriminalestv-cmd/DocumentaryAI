"""Proveedor YouTube (contrato; vídeos/ruedas de prensa/entrevistas públicas). Sin red."""

from app.eae.models import EvidenceKind
from app.eae.providers.base import BaseEvidenceProvider


class YouTubeEvidenceProvider(BaseEvidenceProvider):
    name = "youtube"
    kinds = (EvidenceKind.VIDEO, EvidenceKind.PRESS_CONFERENCE, EvidenceKind.INTERVIEW)
