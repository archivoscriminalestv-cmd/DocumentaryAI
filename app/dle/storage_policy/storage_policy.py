"""Factory de política de almacenamiento (selección por ``LEARNING_STORAGE_MODE``).

TEMPORARY (por defecto) | ARCHIVE | STREAM (interfaz preparada, sin implementación).
"""

import contextlib
import os

from app.dle.storage_policy.archive import ArchiveStoragePolicy
from app.dle.storage_policy.base import ARCHIVE, STREAM, TEMPORARY, BaseStoragePolicy
from app.dle.storage_policy.temporary import TemporaryStoragePolicy


class StreamStoragePolicy(BaseStoragePolicy):
    """Reservado para análisis por streaming (sin descarga). Interfaz lista; sin
    implementación todavía (DLE-002A deja la arquitectura preparada)."""

    mode = STREAM

    @contextlib.contextmanager
    def workspace(self, ref: str, work_dir: str | None = None):
        raise NotImplementedError(
            "LEARNING_STORAGE_MODE=STREAM aún no está implementado (interfaz reservada)")
        yield  # pragma: no cover

    def _finalize(self, work: str) -> None:  # pragma: no cover
        raise NotImplementedError


def build_storage_policy(mode: str | None = None, *,
                         temp_root: str = os.path.join("cache", "learning"),
                         archive_root: str = os.path.join("archive", "videos")) -> BaseStoragePolicy:
    resolved = (mode or os.environ.get("LEARNING_STORAGE_MODE", TEMPORARY)).strip().upper()
    if resolved == ARCHIVE:
        return ArchiveStoragePolicy(temp_root=temp_root, archive_root=archive_root)
    if resolved == STREAM:
        return StreamStoragePolicy(temp_root=temp_root)
    return TemporaryStoragePolicy(temp_root=temp_root)
