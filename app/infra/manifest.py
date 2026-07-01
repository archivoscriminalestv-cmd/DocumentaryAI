"""Project Manifest (INF-001) — identidad determinista del proyecto + hashes críticos.

También expone los helpers de sistema de archivos que reutilizan el resto de módulos del
subsistema. Solo lectura, sin red, sin IA. Las rutas se normalizan a estilo POSIX para que los
hashes y listados sean reproducibles entre máquinas.
"""

import hashlib
import json
import os

from app.infra import INFRA_VERSION, UNKNOWN
from app.infra.models import ArtifactHash, ProjectManifest

# Carpetas que nunca cuentan para el tamaño del proyecto ni se respaldan.
TEMP_DIR_NAMES = {
    "cache", "__pycache__", ".git", ".hg", "node_modules", "venv", ".venv",
    "tmp", "downloads", "render", "renders", "workspace", "workspaces", "outputs",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
}

# Artefactos críticos que se hashean (texto/JSON; nunca binarios pesados).
_ROOT_FILES = ("requirements.txt", "pyproject.toml", "main.py", "CONTRIBUTING.md",
               ".env.example", ".gitignore")
_KEY_DOCS = ("docs/VISION.md", "docs/README.md", "docs/PROJECT.md",
             "docs/DEVELOPMENT_GUIDE.md", "docs/TEAM_CHARTER.md",
             "docs/roadmap/ARCHITECTURAL-BACKLOG.md")


def rel(root: str, path: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def file_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def dir_stats(path: str, exclude: set[str] | None = None) -> tuple[int, int]:
    """(file_count, size_bytes) recursivo, podando carpetas excluidas. Solo stat (rápido)."""
    exclude = exclude or set()
    files = 0
    size = 0
    if not os.path.isdir(path):
        return (0, 0)
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for name in filenames:
            files += 1
            size += file_size(os.path.join(dirpath, name))
    return (files, size)


def list_packages(app_dir: str) -> list[str]:
    """Subsistemas = subcarpetas de app/ con __init__.py."""
    if not os.path.isdir(app_dir):
        return []
    out = []
    for name in sorted(os.listdir(app_dir)):
        d = os.path.join(app_dir, name)
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "__init__.py")):
            out.append(name)
    return out


def list_docs(docs_dir: str, ext: str = ".md") -> list[str]:
    if not os.path.isdir(docs_dir):
        return []
    return sorted(f for f in os.listdir(docs_dir) if f.endswith(ext))


def count_tests(tests_dir: str) -> int:
    """Número de funciones de test (`def test_`) en tests/."""
    if not os.path.isdir(tests_dir):
        return 0
    total = 0
    for dirpath, _dirs, filenames in os.walk(tests_dir):
        for name in filenames:
            if name.startswith("test_") and name.endswith(".py"):
                try:
                    with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
                        for line in fh:
                            if line.lstrip().startswith("def test_"):
                                total += 1
                except OSError:
                    continue
    return total


def _capability_count(root: str):
    """Cuenta capacidades vía DCA (solo lectura). UNKNOWN si no está disponible."""
    try:
        from app.dca.orchestrator import DocumentaryChiefArchitect
        caps = DocumentaryChiefArchitect(root=root).capabilities()
        return len(caps)
    except Exception:
        return UNKNOWN


def _load_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _critical_artifact_paths(root: str) -> list[str]:
    paths: list[str] = [os.path.join(root, f) for f in _ROOT_FILES]
    paths += [os.path.join(root, *d.split("/")) for d in _KEY_DOCS]
    paths.append(os.path.join(root, "knowledge", "learning_statistics.json"))
    styles_dir = os.path.join(root, "knowledge", "styles")
    if os.path.isdir(styles_dir):
        paths += [os.path.join(styles_dir, f) for f in sorted(os.listdir(styles_dir))
                  if f.endswith(".json")]
    for sub in ("adr", "rfc", "spec"):
        d = os.path.join(root, "docs", sub)
        if os.path.isdir(d):
            paths += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".md")]
    return paths


def hash_artifacts(root: str) -> list[ArtifactHash]:
    out: list[ArtifactHash] = []
    for p in _critical_artifact_paths(root):
        if os.path.isfile(p):
            out.append(ArtifactHash(path=rel(root, p), sha256=sha256_file(p),
                                    size_bytes=file_size(p)))
    out.sort(key=lambda a: a.path)
    return out


def build_manifest(root: str = ".", as_of: str = UNKNOWN) -> ProjectManifest:
    stats = _load_json(os.path.join(root, "knowledge", "learning_statistics.json"))
    engines = list_packages(os.path.join(root, "app"))
    _kfiles, ksize = dir_stats(os.path.join(root, "knowledge"), exclude=TEMP_DIR_NAMES)
    _pfiles, psize = dir_stats(root, exclude=TEMP_DIR_NAMES)

    return ProjectManifest(
        infra_version=INFRA_VERSION,
        generated_for_date=as_of or UNKNOWN,
        root=rel(root, root) if os.path.abspath(root) != os.path.abspath(".") else ".",
        engines=engines,
        subsystem_count=len(engines),
        adrs=list_docs(os.path.join(root, "docs", "adr")),
        rfcs=list_docs(os.path.join(root, "docs", "rfc")),
        specs=list_docs(os.path.join(root, "docs", "spec")),
        test_count=count_tests(os.path.join(root, "tests")),
        capability_count=_capability_count(root),
        documentaries_learned=int(stats.get("documentaries_learned", 0) or 0),
        shots_analyzed=int(stats.get("shots_analyzed", 0) or 0),
        scenes_analyzed=int(stats.get("scenes", 0) or 0),
        hours_learned=float(stats.get("hours_learned", 0.0) or 0.0),
        knowledge_size_bytes=ksize,
        project_size_bytes=psize,
        artifact_hashes=hash_artifacts(root),
    )
