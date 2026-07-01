"""Política de ciclo de vida del vídeo del DLE (DLE-002A).

El vídeo descargado es un recurso TEMPORAL: un medio para extraer conocimiento, no parte
de la base de datos. La fuente de verdad es el conocimiento (URL + metadatos + análisis +
estadísticas + embeddings + informes), nunca el fichero de vídeo (salvo ARCHIVE explícito).

Subsistema desacoplado: el Downloader nunca decide qué hacer con el fichero; lo decide la
política. Modos: TEMPORARY (por defecto, borra el vídeo), ARCHIVE (lo conserva), STREAM
(interfaz preparada, sin implementación todavía).
"""

from app.dle.storage_policy.base import ARCHIVE, STREAM, TEMPORARY, BaseStoragePolicy
from app.dle.storage_policy.storage_policy import build_storage_policy

__all__ = ["TEMPORARY", "ARCHIVE", "STREAM", "BaseStoragePolicy", "build_storage_policy"]
