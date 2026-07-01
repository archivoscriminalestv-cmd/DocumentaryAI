"""Catálogo de proveedores de descubrimiento (EAE-003/004).

Los proveedores REALES (Wikimedia Commons, Internet Archive, OpenStreetMap, Wikidata,
Wikipedia) viven en ``real.py``. Aquí quedan los CONTRATOS declarativos del resto de
fuentes (interfaz lista; ``available()`` False, ``discover()`` -> [] hasta integrarlas).
``default_providers(http, cache)`` ensambla reales + contratos. Solo APIs oficiales o
fuentes públicas definidas; nunca scraping/HTML.
"""

from app.eae.discovery.providers.base import BaseDiscoveryProvider
from app.eae.discovery.providers.real import real_providers
from app.eae.planner.models import EvidenceCategory as C

_OPEN = ("PUBLIC_DOMAIN", "CC0", "CC-BY", "CC-BY-SA")
_PD = ("PUBLIC_DOMAIN",)
_RIGHTS = ("RIGHTS_RESERVED",)


class EuropeanaProvider(BaseDiscoveryProvider):
    name = "europeana"
    _media = (C.PHOTO, C.NEWSPAPER, C.MAP, C.BOOK, C.PUBLIC_RECORD)
    _licenses = _OPEN
    _priority = 20
    _cost = "free"
    _rate_limits = {"requires_api_key": True}
    _capabilities = ("search", "metadata")
    _reliability = "HIGH"


class FlickrCommonsProvider(BaseDiscoveryProvider):
    name = "flickr_commons"
    _media = (C.PHOTO, C.SCENE_PHOTO)
    _licenses = _PD + ("CC-BY", "CC-BY-SA")
    _priority = 25
    _cost = "free"
    _rate_limits = {"requires_api_key": True}
    _capabilities = ("search", "metadata")
    _reliability = "MEDIUM"


class LibraryOfCongressProvider(BaseDiscoveryProvider):
    name = "library_of_congress"
    _media = (C.PHOTO, C.NEWSPAPER, C.MAP, C.AUDIO, C.PUBLIC_RECORD, C.BOOK)
    _licenses = _PD
    _priority = 12
    _cost = "free"
    _capabilities = ("search", "metadata", "download")
    _reliability = "HIGH"


class NationalArchivesProvider(BaseDiscoveryProvider):
    name = "national_archives"
    _media = (C.PUBLIC_RECORD, C.POLICE_DOCUMENT, C.COURT_DOCUMENT, C.MAP, C.OFFICIAL_STATEMENT)
    _licenses = _PD + ("UNKNOWN",)
    _priority = 12
    _cost = "free"
    _capabilities = ("search", "metadata")
    _reliability = "HIGH"


class BBCArchiveProvider(BaseDiscoveryProvider):
    name = "bbc_archive"
    _media = (C.ARCHIVE_VIDEO, C.TV_REPORT, C.INTERVIEW, C.AUDIO)
    _licenses = _RIGHTS
    _priority = 30
    _cost = "restricted"
    _capabilities = ("search",)
    _reliability = "HIGH"


class ReutersArchiveProvider(BaseDiscoveryProvider):
    name = "reuters_archive"
    _media = (C.NEWS, C.ARCHIVE_VIDEO, C.PHOTO)
    _licenses = _RIGHTS
    _priority = 35
    _cost = "paid"
    _capabilities = ("search",)
    _reliability = "HIGH"


class AssociatedPressProvider(BaseDiscoveryProvider):
    name = "associated_press"
    _media = (C.NEWS, C.ARCHIVE_VIDEO, C.PHOTO)
    _licenses = _RIGHTS
    _priority = 35
    _cost = "paid"
    _capabilities = ("search",)
    _reliability = "HIGH"


class GoogleBooksProvider(BaseDiscoveryProvider):
    name = "google_books"
    _media = (C.BOOK,)
    _licenses = ("UNKNOWN",)
    _priority = 40
    _cost = "free"
    _capabilities = ("search", "metadata")
    _reliability = "MEDIUM"


class GovernmentRepositoryProvider(BaseDiscoveryProvider):
    name = "government"
    _media = (C.PUBLIC_RECORD, C.OFFICIAL_STATEMENT, C.POLICE_DOCUMENT, C.COURT_DOCUMENT,
              C.FORENSIC_IMAGE)
    _licenses = _PD + ("UNKNOWN",)
    _priority = 14
    _cost = "free"
    _capabilities = ("search", "metadata")
    _reliability = "HIGH"


class PublicCourtRepositoryProvider(BaseDiscoveryProvider):
    name = "public_court"
    _media = (C.COURT_DOCUMENT, C.PUBLIC_RECORD, C.OFFICIAL_STATEMENT)
    _licenses = _PD + ("UNKNOWN",)
    _priority = 14
    _cost = "free"
    _capabilities = ("search", "metadata")
    _reliability = "HIGH"


class YouTubeDiscoveryProvider(BaseDiscoveryProvider):
    name = "youtube"
    _media = (C.VIDEO, C.INTERVIEW, C.PRESS_CONFERENCE, C.TV_REPORT, C.ARCHIVE_VIDEO)
    _licenses = ("UNKNOWN", "CC-BY")
    _priority = 28
    _cost = "free"
    _capabilities = ("search", "metadata", "download")
    _reliability = "MEDIUM"


def contract_providers() -> list[BaseDiscoveryProvider]:
    return [
        EuropeanaProvider(), FlickrCommonsProvider(), LibraryOfCongressProvider(),
        NationalArchivesProvider(), BBCArchiveProvider(), ReutersArchiveProvider(),
        AssociatedPressProvider(), GoogleBooksProvider(), GovernmentRepositoryProvider(),
        PublicCourtRepositoryProvider(), YouTubeDiscoveryProvider(),
    ]


def default_providers(http=None, cache=None) -> list[BaseDiscoveryProvider]:
    """Reales (con HTTP inyectable; sin él, contratos) + contratos del resto de fuentes."""
    return real_providers(http, cache) + contract_providers()
