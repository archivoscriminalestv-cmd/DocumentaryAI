"""Git Readiness (INF-003) — compone la auditoría completa y emite el veredicto.

Determina si el repositorio está listo para el primer `git push`: solo código/documentación/
arquitectura/tests/knowledge*/configuración; nada generado/temporal/caché; sin secretos; sin
ficheros que GitHub rechace. (*knowledge se ignora en git por política; se respalda vía INF.)
"""

import os

from app.gitops import GITOPS_VERSION, git_status, gitignore_manager, large_files, secrets
from app.gitops.classifier import classify
from app.gitops.models import FileCategory as C
from app.gitops.models import GitReadiness, GitState

_GENERATED_LIKE = {C.OUTPUT, C.GENERATED, C.CACHE, C.TEMPORARY}


def _size(root: str, rel: str) -> int:
    try:
        return os.path.getsize(os.path.join(root, rel.replace("/", os.sep)))
    except OSError:
        return 0


def build_readiness(root: str = ".", gitignore_path: str | None = None) -> GitReadiness:
    root = os.path.abspath(root)
    gi_path = gitignore_path or os.path.join(root, ".gitignore")
    rep = GitReadiness(gitops_version=GITOPS_VERSION)

    repo = git_status.is_repo(root)
    commit_set = git_status.would_commit(root) if repo else []
    rep.git = GitState(
        is_repo=repo, branch=git_status.branch(root), remote=git_status.remote(root),
        tracked=len(git_status.tracked_files(root)) if repo else 0,
        would_commit=len(commit_set),
        ignored_paths=len(git_status.ignored_entries(root)) if repo else 0)

    # clasificación del conjunto que se subiría
    cat_counts: dict[str, dict] = {}
    top_counts: dict[str, int] = {}
    for rel in commit_set:
        cat = classify(rel)
        entry = cat_counts.setdefault(cat, {"files": 0, "size_bytes": 0})
        entry["files"] += 1
        entry["size_bytes"] += _size(root, rel)
        top = rel.split("/")[0]
        top_counts[top] = top_counts.get(top, 0) + 1
    rep.category_counts = {k: cat_counts[k] for k in sorted(cat_counts)}
    rep.top_level_commit = {k: top_counts[k] for k in sorted(top_counts)}

    rep.large_files = large_files.scan(root, commit_set)
    rep.secrets = secrets.scan(root, commit_set)
    rep.env_ignored = secrets.env_ignored(root)
    rep.gitignore_missing = gitignore_manager.missing_entries(gi_path)
    rep.would_commit_sample = commit_set[:40]

    # bloqueadores
    blockers: list[str] = []
    if not repo:
        blockers.append("no es un repositorio git")
    if not rep.env_ignored:
        blockers.append(".env NO está ignorado (riesgo de subir secretos)")
    err_secrets = [s for s in rep.secrets if s.severity == "ERROR"]
    if err_secrets:
        blockers.append(f"{len(err_secrets)} secreto(s) crítico(s) en ficheros que se subirían")
    hard = [f for f in rep.large_files if f.blocks_push]
    if hard:
        blockers.append(f"{len(hard)} fichero(s) >100 MB en el commit (GitHub los rechazará)")
    generated = sorted(c for c in rep.category_counts if c in _GENERATED_LIKE)
    if generated:
        n = sum(rep.category_counts[c]["files"] for c in generated)
        blockers.append(f"{n} fichero(s) generado/temporal se subirían ({', '.join(generated)})")

    rep.blockers = blockers
    rep.ready_for_push = not blockers
    rep.notes = _notes(rep)
    return rep


def _notes(rep: GitReadiness) -> list[str]:
    notes = ["INF-003 no ejecuta git add/commit/push: solo deja el repo preparado."]
    if rep.gitignore_missing:
        notes.append(f"faltan {len(rep.gitignore_missing)} exclusiones recomendadas en .gitignore "
                     "(usa el CLI con --write-gitignore o el informe).")
    if rep.large_files and not any(f.blocks_push for f in rep.large_files):
        notes.append("hay binarios grandes en disco, pero ninguno se subiría ni supera 100 MB.")
    return notes
