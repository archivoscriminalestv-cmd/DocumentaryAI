"""Detección de secretos (INF-003).

Escanea SOLO los ficheros de texto que se subirían (would_commit) en busca de claves de API,
tokens, contraseñas o claves privadas. Verifica además que ``.env`` permanece ignorado. Nunca
imprime el valor del secreto; solo su ubicación y tipo. Conservador para evitar falsos positivos
(ignora placeholders típicos de los .env.example).
"""

import os
import re

from app.gitops import git_status
from app.gitops.models import SecretFinding

_TEXT_EXT = {".py", ".pyi", ".md", ".txt", ".rst", ".toml", ".yaml", ".yml", ".json", ".cfg",
             ".ini", ".sh", ".bat", ".spec", ".env", ".example", ".gitignore", ""}
_PLACEHOLDER = ("example", "your", "placeholder", "xxxx", "changeme", "<", "dummy", "sample",
                "todo", "redacted", "fake")

# Patrones de secreto REAL (valor con forma de credencial) → ERROR.
_ERROR_PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("hf_token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
]
# Asignación genérica key=... → se filtra el VALOR para evitar falsos positivos.
_GENERIC = re.compile(r"(?i)(?:api[_-]?key|secret|token|passwd|password|pwd)\s*[:=]\s*"
                      r"['\"](?P<val>[A-Za-z0-9_\-\/\+=]{16,})['\"]")
# Un valor que es un NOMBRE (env var / constante) no es un secreto: p.ej. "REPLICATE_API_TOKEN".
_ENV_NAME = re.compile(r"[A-Z][A-Z0-9_]{2,}$")


def _looks_placeholder(text: str) -> bool:
    low = text.lower()
    return any(p in low for p in _PLACEHOLDER)


def scan(root: str, would_commit: list[str] | None = None) -> list[SecretFinding]:
    if would_commit is None:
        would_commit = git_status.would_commit(root)
    findings: list[SecretFinding] = []
    for rel in would_commit:
        ext = os.path.splitext(rel)[1].lower()
        base = os.path.basename(rel)
        if ext not in _TEXT_EXT and not base.startswith(".env"):
            continue
        full = os.path.join(root, rel.replace("/", os.sep))
        try:
            if os.path.getsize(full) > 1_000_000:
                continue
            with open(full, "r", encoding="utf-8", errors="strict") as fh:
                lines = fh.readlines()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines, start=1):
            hit = None
            for kind, rx in _ERROR_PATTERNS:
                if rx.search(line):
                    hit = SecretFinding(path=rel, line=i, kind=kind, severity="ERROR",
                                        hint="revisar y retirar antes del push")
                    break
            if hit is None:
                m = _GENERIC.search(line)
                if m:
                    val = m.group("val")
                    # descartar nombres de variable/entorno y placeholders (no son secretos)
                    if not _ENV_NAME.fullmatch(val) and not _looks_placeholder(line):
                        hit = SecretFinding(path=rel, line=i, kind="generic_secret_assignment",
                                            severity="WARNING", hint="revisar y retirar antes del push")
            if hit is not None:
                findings.append(hit)
    return findings


def env_ignored(root: str) -> bool:
    """.env debe estar ignorado Y no seguido."""
    if ".env" in git_status.tracked_files(root):
        return False
    if not os.path.exists(os.path.join(root, ".env")):
        return True                       # no hay .env: nada que filtrar
    return git_status.is_path_ignored(root, ".env")
