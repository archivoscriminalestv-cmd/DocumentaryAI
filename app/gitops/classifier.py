"""Clasificador de archivos del repositorio (INF-003).

Asigna a cada ruta relativa (estilo POSIX) una categoría objetiva. Reglas por carpeta y por
extensión; el orden importa (lo más específico primero). Determinista, sin efectos.
"""

import os

from app.gitops.models import FileCategory as C

_CACHE_DIRS = ("__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache")
_OUTPUT_DIRS = ("output", "outputs")
_GENERATED_DIRS = ("library", "render", "renders", "dist", "build")
_TEMP_DIRS = ("cache", "tmp", "temp", "workspace", "workspaces", "downloads", "logs", "archive")
_CONFIG_TOP = {".gitignore", "pyproject.toml", ".env.example", "setup.cfg", "setup.py",
               "requirements.txt", "mypy.ini", "pytest.ini", "tox.ini"}
_CONFIG_DIRS = ("config", ".github")
_BINARY_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".wav", ".mp3", ".m4a", ".flac",
               ".aac", ".ogg", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".ico",
               ".pt", ".pth", ".ckpt", ".safetensors", ".onnx", ".gguf", ".bin", ".pb",
               ".zip", ".tar", ".gz", ".7z", ".rar", ".exe", ".dll", ".so", ".dylib", ".pdf"}
_SOURCE_EXT = {".py", ".pyi", ".md", ".txt", ".rst", ".sh", ".bat", ".spec", ".cfg", ".ini"}
_CONFIG_EXT = {".toml", ".yaml", ".yml", ".json"}


def _parts(relpath: str) -> list[str]:
    return relpath.replace("\\", "/").split("/")


def classify(relpath: str) -> str:
    rel = relpath.replace("\\", "/")
    parts = _parts(rel)
    top = parts[0]
    name = parts[-1]
    ext = os.path.splitext(name)[1].lower()

    if any(p in _CACHE_DIRS for p in parts) or ext in (".pyc", ".pyo", ".pyd"):
        return C.CACHE
    if top in _OUTPUT_DIRS:
        return C.OUTPUT
    if any(p in _GENERATED_DIRS for p in parts):
        return C.GENERATED
    if top == "knowledge":
        return C.KNOWLEDGE
    if any(p in _TEMP_DIRS for p in parts):
        return C.TEMPORARY
    if top == "datasets":
        return C.DATASET
    if name in _CONFIG_TOP or top in _CONFIG_DIRS or ext in _CONFIG_EXT:
        return C.CONFIG
    if ext in _BINARY_EXT:
        return C.BINARIES
    if ext in _SOURCE_EXT or top in ("app", "tests", "scripts", "tools", "prompts", "docs",
                                     "Agents", "templates"):
        return C.SOURCE
    return C.SOURCE
