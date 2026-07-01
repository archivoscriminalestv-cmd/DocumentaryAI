"""Persistencia del informe Git Readiness (INF-003) → output/system/. Nunca knowledge/."""

import json
import os

from app.gitops.models import GitReadiness

DEFAULT_OUT = os.path.join("output", "system")


def _guard(out_dir: str) -> None:
    if "knowledge" in os.path.normpath(out_dir).split(os.sep):
        raise ValueError("INF-003 nunca escribe dentro de knowledge/")


def _human(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{n} B"


def write_reports(rep: GitReadiness, out_dir: str = DEFAULT_OUT) -> dict[str, str]:
    _guard(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "git_readiness.json")
    with open(json_path, "w", encoding="utf-8") as h:
        json.dump(rep.to_dict(), h, ensure_ascii=False, indent=2, sort_keys=True)
    md_path = os.path.join(out_dir, "git_readiness_report.md")
    with open(md_path, "w", encoding="utf-8") as h:
        h.write(render_markdown(rep))
    return {"git_readiness": json_path, "git_readiness_report": md_path}


def render_markdown(rep: GitReadiness) -> str:
    g = rep.git
    verdict = "SI — listo para el primer push" if rep.ready_for_push else "NO — resolver bloqueadores"
    lines = [
        "# Git Readiness — DocumentaryAI (INF-003)",
        "",
        f"- versión: `{rep.gitops_version}`",
        f"- **Repositorio listo para push: {verdict}**",
        f"- repo git: {g.is_repo} · rama: {g.branch} · remoto: {g.remote}",
        f"- seguidos: {g.tracked} · se subirían (git add .): {g.would_commit} · "
        f"rutas ignoradas: {g.ignored_paths}",
        f"- .env ignorado: {'sí' if rep.env_ignored else 'NO'}",
        "",
    ]
    if rep.blockers:
        lines.append("## Bloqueadores")
        for b in rep.blockers:
            lines.append(f"- ❌ {b}")
        lines.append("")
    else:
        lines.append("## Bloqueadores\n- (ninguno) ✅\n")

    lines.append("## Qué se subirá — por categoría")
    lines.append("| categoría | ficheros | tamaño |")
    lines.append("|---|---|---|")
    for cat, info in rep.category_counts.items():
        lines.append(f"| {cat} | {info['files']} | {_human(info['size_bytes'])} |")
    lines.append("")

    lines.append("## Qué se subirá — por carpeta raíz")
    for top, n in rep.top_level_commit.items():
        lines.append(f"- `{top}` — {n}")
    lines.append("")

    lines.append("## Archivos grandes")
    if not rep.large_files:
        lines.append("- (ninguno relevante) ✅")
    for f in rep.large_files:
        flag = "BLOQUEA PUSH" if f.blocks_push else "aviso"
        lines.append(f"- `{f.path}` — {_human(f.size_bytes)} — {flag}: {f.reason}")
    lines.append("")

    lines.append("## Secretos")
    if not rep.secrets:
        lines.append("- (ninguno detectado) ✅")
    for s in rep.secrets:
        lines.append(f"- [{s.severity}] `{s.path}:{s.line}` — {s.kind} ({s.hint})")
    lines.append("")

    if rep.gitignore_missing:
        lines.append("## .gitignore — exclusiones recomendadas que faltan")
        for e in rep.gitignore_missing:
            lines.append(f"- `{e}`")
        lines.append("")

    lines.append("## Muestra de ficheros que se subirán (primeros 40)")
    for p in rep.would_commit_sample:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("> INF-003 NO ejecuta git add/commit/push. El primer commit lo haces tú a mano.")
    return "\n".join(lines)
