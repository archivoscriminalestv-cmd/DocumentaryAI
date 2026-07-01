"""Proveedor de prensa (contrato; noticias/artículos con fuente). Sin red, sin scraping."""

from app.eae.models import EvidenceKind
from app.eae.providers.base import BaseEvidenceProvider


class NewsProvider(BaseEvidenceProvider):
    name = "news"
    kinds = (EvidenceKind.NEWS, EvidenceKind.STATEMENT)
