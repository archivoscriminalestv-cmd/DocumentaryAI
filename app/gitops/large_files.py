"""Detección de archivos grandes (INF-003).

Aviso a partir de 50 MB; BLOQUEO a partir de 100 MB (GitHub rechaza el push de un fichero así en
un repositorio normal). Nunca borra nada: solo informa (ruta, tamaño, motivo). También revisa el
árbol completo por si hay un fichero enorme aunque esté ignorado (para avisar antes del push).
"""

import os

from app.gitops.models import HARD_BYTES, WARN_BYTES, LargeFile


def _size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def scan(root: str, would_commit: list[str], tree_scan: bool = True) -> list[LargeFile]:
    found: dict[str, LargeFile] = {}

    # 1) Ficheros que se subirían: cualquier tamaño relevante es crítico.
    for rel in would_commit:
        size = _size(os.path.join(root, rel.replace("/", os.sep)))
        if size >= HARD_BYTES:
            found[rel] = LargeFile(rel, size, "supera 100 MB: GitHub rechazará el push",
                                   blocks_push=True)
        elif size >= WARN_BYTES:
            found[rel] = LargeFile(rel, size, "supera 50 MB: GitHub avisa (considera excluirlo)")

    # 2) Árbol completo (aunque esté ignorado): avisar de binarios enormes presentes en disco.
    if tree_scan:
        skip = {".git", "__pycache__", ".venv", "venv", "node_modules"}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for name in filenames:
                full = os.path.join(dirpath, name)
                size = _size(full)
                if size >= HARD_BYTES:
                    rel = os.path.relpath(full, root).replace(os.sep, "/")
                    if rel not in found:
                        found[rel] = LargeFile(
                            rel, size, "supera 100 MB (presente en disco; gestionar aparte)",
                            blocks_push=False)

    return sorted(found.values(), key=lambda f: -f.size_bytes)
