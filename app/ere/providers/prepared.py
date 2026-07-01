"""Proveedores PREPARADOS del ERE (interfaz lista, integración pendiente).

Son las fuentes más relevantes para true-crime / actualidad (noticias, vídeo,
imágenes de buscador, hemerotecas, documentación judicial). Requieren claves de API
o acuerdos de uso, por lo que aquí se entregan con la interfaz completa pero
devolviendo ``available=False`` (el pipeline continúa, sin inventar). Wirearlas más
adelante NO exige tocar el orquestador, el graph builder ni el resto del sistema:
basta sustituir el cuerpo de ``research`` por la llamada real (reciben ya un
``client`` inyectable).

Nota legal: ``CourtDocumentsProvider`` solo registrará REFERENCIAS públicas; nunca
interpreta contenido jurídico.
"""

from app.ere.http import HttpClient
from app.ere.models import ProjectQuery
from app.ere.providers.base import EvidenceProvider, EvidenceResult


class _PreparedProvider(EvidenceProvider):
    name = "prepared"
    _kind = "fuente"

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client  # inyectable para la integración futura

    def research(self, query: ProjectQuery) -> EvidenceResult:
        return EvidenceResult(
            provider=self.name,
            available=False,
            notes=f"Integración de {self._kind} no implementada (interfaz preparada).",
        )


class NewsProvider(_PreparedProvider):
    name = "news"
    _kind = "noticias"


class YoutubeProvider(_PreparedProvider):
    name = "youtube"
    _kind = "vídeo (YouTube)"


class GoogleImagesProvider(_PreparedProvider):
    name = "google-images"
    _kind = "imágenes de buscador"


class ArchiveProvider(_PreparedProvider):
    name = "archive"
    _kind = "hemeroteca/archivo"


class CourtDocumentsProvider(_PreparedProvider):
    name = "court-documents"
    _kind = "documentación judicial (solo referencias públicas)"
