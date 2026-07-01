"""Modelos del Git Sanitizer (INF-003). Tipados, serializables, deterministas."""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.gitops import GITOPS_SCHEMA_VERSION

# Límites de GitHub: aviso a 50 MB, rechazo duro a 100 MB.
WARN_BYTES = 50 * 1024 * 1024
HARD_BYTES = 100 * 1024 * 1024


class FileCategory:
    SOURCE = "SOURCE"
    CONFIG = "CONFIG"
    KNOWLEDGE = "KNOWLEDGE"
    DATASET = "DATASET"
    OUTPUT = "OUTPUT"
    TEMPORARY = "TEMPORARY"
    GENERATED = "GENERATED"
    CACHE = "CACHE"
    BINARIES = "BINARIES"
    LARGE_FILES = "LARGE_FILES"
    ALL = (SOURCE, CONFIG, KNOWLEDGE, DATASET, OUTPUT, TEMPORARY, GENERATED, CACHE,
           BINARIES, LARGE_FILES)


@dataclass
class LargeFile:
    path: str
    size_bytes: int
    reason: str
    blocks_push: bool = False        # True si supera el límite duro de GitHub (100 MB)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SecretFinding:
    path: str
    line: int
    kind: str
    severity: str = "ERROR"          # ERROR | WARNING
    hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GitState:
    is_repo: bool = False
    branch: str = "UNKNOWN"
    remote: str = "UNKNOWN"
    tracked: int = 0
    would_commit: int = 0
    ignored_paths: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GitReadiness:
    schema_version: str = GITOPS_SCHEMA_VERSION
    gitops_version: str = ""
    ready_for_push: bool = False
    git: GitState = field(default_factory=GitState)
    category_counts: dict = field(default_factory=dict)      # categoría -> {files, size_bytes}
    top_level_commit: dict = field(default_factory=dict)     # dir -> nº de ficheros a subir
    large_files: list[LargeFile] = field(default_factory=list)
    secrets: list[SecretFinding] = field(default_factory=list)
    env_ignored: bool = False
    gitignore_missing: list[str] = field(default_factory=list)   # entradas recomendadas que faltan
    would_commit_sample: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "gitops_version": self.gitops_version,
            "ready_for_push": self.ready_for_push,
            "git": self.git.to_dict(),
            "env_ignored": self.env_ignored,
            "category_counts": self.category_counts,
            "top_level_commit": self.top_level_commit,
            "large_files": [f.to_dict() for f in self.large_files],
            "secrets": [s.to_dict() for s in self.secrets],
            "gitignore_missing": list(self.gitignore_missing),
            "would_commit_sample": list(self.would_commit_sample),
            "blockers": list(self.blockers),
            "notes": list(self.notes),
        }
