"""Proveedor de vídeo local: usa el fichero tal cual (sin red)."""

import hashlib
import os


def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


class LocalVideoProvider:
    name = "local"

    def resolve(self, ref: str, work_dir: str) -> dict:
        if not os.path.exists(ref):
            raise FileNotFoundError(f"vídeo local no encontrado: {ref}")
        return {"path": ref, "source_type": "local", "source_ref": os.path.abspath(ref),
                "video_id": f"doc_{_file_hash(ref)}"}
