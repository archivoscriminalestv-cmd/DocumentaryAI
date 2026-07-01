"""Adaptadores de adquisición multi-fuente del ERE (ERE-003) — PREPARADOS.

Amplían el catálogo de fuentes públicas (archivos abiertos, hemerotecas, repositorios
académicos, RSS…). Solo APIs oficiales o contenido público permitido; **sin scraping
inventado**. Se entregan con la interfaz completa y ``client`` inyectable, devolviendo
``available=False`` hasta que se wire cada integración real. Activarlos NO exige tocar
el orquestador, el graph builder ni el dossier.
"""

from app.ere.providers.prepared import _PreparedProvider


class OpenverseProvider(_PreparedProvider):
    name = "openverse"
    _kind = "imágenes con licencia abierta (Openverse)"


class EuropeanaProvider(_PreparedProvider):
    name = "europeana"
    _kind = "patrimonio digital (Europeana)"


class ArchiveOrgProvider(_PreparedProvider):
    name = "archive-org"
    _kind = "Internet Archive (archive.org)"


class RssProvider(_PreparedProvider):
    name = "rss"
    _kind = "feeds RSS de medios"


class LibraryProvider(_PreparedProvider):
    name = "library"
    _kind = "catálogos de bibliotecas"


class HemerotecaProvider(_PreparedProvider):
    name = "hemeroteca"
    _kind = "hemerotecas (prensa histórica)"


class GoogleBooksProvider(_PreparedProvider):
    name = "google-books"
    _kind = "Google Books"


class DoajProvider(_PreparedProvider):
    name = "doaj"
    _kind = "DOAJ (revistas de acceso abierto)"


class OpenAlexProvider(_PreparedProvider):
    name = "openalex"
    _kind = "OpenAlex (literatura académica)"
