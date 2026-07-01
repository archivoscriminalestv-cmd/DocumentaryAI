"""Gestión del .gitignore (INF-003) — idempotente y no destructiva.

Solo AÑADE entradas recomendadas que falten (nunca borra ni reordena lo que el usuario ya tiene).
Las añade bajo un bloque marcado para que sea evidente su origen.
"""

import os

MANAGED_HEADER = "# === INF-003: exclusiones recomendadas (Git Sanitizer) ==="

# Buenas prácticas para DocumentaryAI: generado/temporal/caché/binarios pesados fuera de git.
RECOMMENDED = [
    "output/", "workspace/", "workspaces/", "downloads/", "renders/", "render/",
    "tmp/", "temp/", "logs/", "*.log", "*.tmp", "*.bak",
    ".DS_Store", "Thumbs.db",
    "*.pt", "*.pth", "*.ckpt", "*.safetensors", "*.onnx", "*.gguf",
    "*.zip", "*.7z", "*.rar",
    "*.exe", "*.dll",
    "/channel_intro.mp4",
]


def _existing_entries(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    out = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s and not s.startswith("#"):
                out.add(s)
    return out


def missing_entries(path: str, recommended: list[str] | None = None) -> list[str]:
    existing = _existing_entries(path)
    rec = recommended if recommended is not None else RECOMMENDED
    return [e for e in rec if e not in existing]


def ensure_entries(path: str, recommended: list[str] | None = None,
                   write: bool = False) -> list[str]:
    """Devuelve las entradas que faltan. Si ``write``, las añade al final bajo el bloque marcado."""
    missing = missing_entries(path, recommended)
    if write and missing:
        needs_nl = os.path.exists(path) and os.path.getsize(path) > 0
        with open(path, "a", encoding="utf-8") as fh:
            if needs_nl:
                fh.write("\n")
            fh.write(MANAGED_HEADER + "\n")
            fh.write("\n".join(missing) + "\n")
    return missing
