"""Proveedores de evidencia del EAE — SOLO contratos (EAE-001).

Cada proveedor implementa ``EvidenceProvider`` pero NO realiza peticiones reales todavía:
``search`` devuelve [] y ``fetch`` lanza NotImplementedError. Sin red, sin scraping.
"""

from app.eae.providers.future import FutureProvider
from app.eae.providers.government import GovernmentProvider
from app.eae.providers.internet_archive import InternetArchiveProvider
from app.eae.providers.news import NewsProvider
from app.eae.providers.wayback import WaybackProvider
from app.eae.providers.wikimedia import WikimediaProvider
from app.eae.providers.youtube import YouTubeEvidenceProvider

__all__ = [
    "YouTubeEvidenceProvider", "WikimediaProvider", "InternetArchiveProvider",
    "NewsProvider", "GovernmentProvider", "WaybackProvider", "FutureProvider",
]


def default_providers() -> list:
    """Conjunto estándar de proveedores (contratos), en orden estable."""
    return [
        YouTubeEvidenceProvider(), WikimediaProvider(), InternetArchiveProvider(),
        NewsProvider(), GovernmentProvider(), WaybackProvider(), FutureProvider(),
    ]
