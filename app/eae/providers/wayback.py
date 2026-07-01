"""Proveedor Wayback Machine (contrato; instantáneas históricas de páginas). Sin red."""

from app.eae.models import EvidenceKind
from app.eae.providers.base import BaseEvidenceProvider


class WaybackProvider(BaseEvidenceProvider):
    name = "wayback"
    kinds = (EvidenceKind.NEWS, EvidenceKind.DOCUMENT, EvidenceKind.SOCIAL_POST)
