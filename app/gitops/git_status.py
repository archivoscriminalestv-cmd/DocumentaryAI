"""Lectura del estado de Git (INF-003) — solo lectura, nunca modifica el repositorio.

Envuelve comandos git en modo lectura. En Windows usa CREATE_NO_WINDOW para no abrir consolas
(misma lección que DAS-001A). Si git no está disponible, degrada a valores vacíos sin lanzar.
"""

import os
import subprocess

_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _git(root: str, args: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                             creationflags=_NO_WINDOW, timeout=60)
        return out.returncode, out.stdout or ""
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def is_repo(root: str) -> bool:
    code, out = _git(root, ["rev-parse", "--is-inside-work-tree"])
    return code == 0 and out.strip() == "true"


def branch(root: str) -> str:
    code, out = _git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    return out.strip() if code == 0 and out.strip() else "UNKNOWN"


def remote(root: str) -> str:
    code, out = _git(root, ["remote", "get-url", "origin"])
    return out.strip() if code == 0 and out.strip() else "UNKNOWN"


def tracked_files(root: str) -> list[str]:
    return _lines(_git(root, ["ls-files"])[1])


def untracked_not_ignored(root: str) -> list[str]:
    """Lo que `git add .` añadiría de nuevo (ficheros no seguidos y NO ignorados)."""
    return _lines(_git(root, ["ls-files", "--others", "--exclude-standard"])[1])


def ignored_entries(root: str) -> list[str]:
    return _lines(_git(root, ["ls-files", "--others", "--ignored",
                              "--exclude-standard", "--directory"])[1])


def would_commit(root: str) -> list[str]:
    """Conjunto que quedará en el repo tras `git add .`: seguidos ∪ no-ignorados nuevos."""
    return sorted(set(tracked_files(root)) | set(untracked_not_ignored(root)))


def is_path_ignored(root: str, relpath: str) -> bool:
    code, _ = _git(root, ["check-ignore", "-q", relpath])
    return code == 0
