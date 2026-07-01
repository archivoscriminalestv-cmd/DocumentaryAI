"""ARCHIVE: descargar → analizar → guardar conocimiento → CONSERVAR el vídeo.

Pensado solo para vídeos de referencia. Mueve los vídeos del workspace a un directorio
de archivo permanente y limpia el resto de temporales (fotogramas, etc.).
"""

import os
import shutil

from app.dle.storage_policy.base import (
    ARCHIVE,
    BaseStoragePolicy,
    find_videos,
    safe_rmtree,
    workspace_key,
)


class ArchiveStoragePolicy(BaseStoragePolicy):
    mode = ARCHIVE

    def __init__(self, temp_root: str = os.path.join("cache", "learning"),
                 archive_root: str = os.path.join("archive", "videos")) -> None:
        super().__init__(temp_root)
        self.archive_root = archive_root
        self.last_archived: list[str] = []

    def _finalize(self, work: str) -> None:
        self.last_archived = []
        dest_dir = os.path.join(self.archive_root, os.path.basename(work) or workspace_key(work))
        os.makedirs(dest_dir, exist_ok=True)
        for video in find_videos(work):
            dest = os.path.join(dest_dir, os.path.basename(video))
            try:
                shutil.move(video, dest)
                self.last_archived.append(dest)
            except OSError:
                pass
        # Limpia los temporales restantes (fotogramas, etc.); el vídeo ya está a salvo.
        safe_rmtree(work, allowed_root=self.temp_root)
