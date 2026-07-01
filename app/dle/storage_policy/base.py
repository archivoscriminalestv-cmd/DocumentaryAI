"""Base de las políticas de almacenamiento + salvaguardas de borrado.

Reglas de seguridad DURAS: solo se eliminan ficheros temporales creados por el propio
aprendizaje (bajo la raíz temporal de la política). NUNCA se borra knowledge/, library/,
output/ ni assets/.
"""

import contextlib
import hashlib
import os
import shutil

TEMPORARY = "TEMPORARY"
ARCHIVE = "ARCHIVE"
STREAM = "STREAM"

# Directorios PERMANENTES que jamás deben borrarse.
PROTECTED_DIRS = ("knowledge", "library", "output", "assets")

_VIDEO_EXTS = (".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v", ".flv")


def workspace_key(ref: str) -> str:
    return hashlib.sha256((ref or "src").encode("utf-8")).hexdigest()[:12]


def _resolved_parts(path: str) -> list[str]:
    return os.path.abspath(path).replace("\\", "/").rstrip("/").split("/")


def is_protected(path: str) -> bool:
    """True si la ruta ES o ESTÁ DENTRO de un directorio permanente protegido."""
    parts = _resolved_parts(path)
    cwd_parts = _resolved_parts(os.getcwd())
    for prot in PROTECTED_DIRS:
        target = cwd_parts + [prot]
        if parts[: len(target)] == target:
            return True
    return False


def safe_rmtree(path: str, *, allowed_root: str) -> bool:
    """Borra ``path`` solo si está dentro de ``allowed_root`` y no es protegido.

    Devuelve True si borró algo. Nunca lanza por ausencia.
    """
    if not path or not os.path.exists(path):
        return False
    abs_path = os.path.abspath(path)
    abs_root = os.path.abspath(allowed_root)
    inside = abs_path == abs_root or abs_path.startswith(abs_root + os.sep)
    if not inside or is_protected(abs_path) or is_protected(abs_root):
        return False
    shutil.rmtree(abs_path, ignore_errors=True)
    return True


def find_videos(directory: str) -> list[str]:
    out = []
    for root, _dirs, files in os.walk(directory):
        for f in files:
            if os.path.splitext(f)[1].lower() in _VIDEO_EXTS:
                out.append(os.path.join(root, f))
    return out


class BaseStoragePolicy:
    """Gestiona el workspace de UN aprendizaje y su limpieza/archivado."""

    mode = "BASE"

    def __init__(self, temp_root: str = os.path.join("cache", "learning")) -> None:
        self.temp_root = temp_root

    def _create(self, ref: str) -> str:
        path = os.path.join(self.temp_root, workspace_key(ref))
        os.makedirs(path, exist_ok=True)
        return path

    @contextlib.contextmanager
    def workspace(self, ref: str, work_dir: str | None = None):
        """Cede un directorio de trabajo. Si ``work_dir`` se indica, lo gestiona el caller
        (no se toca). Si no, lo crea la política y lo finaliza SIEMPRE (éxito o error)."""
        if work_dir:
            yield work_dir
            return
        path = self._create(ref)
        try:
            yield path
        finally:
            self._finalize(path)

    def _finalize(self, work: str) -> None:  # pragma: no cover - override
        raise NotImplementedError
