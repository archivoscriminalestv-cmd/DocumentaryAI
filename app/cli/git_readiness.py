"""CLI del Git Sanitizer (INF-003).

Audita el repositorio y escribe output/system/git_readiness.json + git_readiness_report.md.
Con --write-gitignore añade al .gitignore las exclusiones recomendadas que falten. NUNCA ejecuta
git add/commit/push.

    python -m app.cli.git_readiness
    python -m app.cli.git_readiness --write-gitignore
"""

import argparse
import os
import sys

from app.gitops import gitignore_manager
from app.gitops.persistence import DEFAULT_OUT, _human, write_reports
from app.gitops.readiness import build_readiness


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="Git Repository Sanitizer & Readiness (INF-003).")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--write-gitignore", action="store_true",
                    help="añade al .gitignore las exclusiones recomendadas que falten")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    gi_path = os.path.join(root, ".gitignore")

    if args.write_gitignore:
        added = gitignore_manager.ensure_entries(gi_path, write=True)
        print(f".gitignore: {len(added)} exclusiones añadidas" +
              (": " + ", ".join(added) if added else " (ya estaba completo)"))
        print()

    rep = build_readiness(root)
    paths = write_reports(rep, out_dir=args.out)

    print("=" * 48)
    print("GIT READINESS — DocumentaryAI (INF-003)")
    print("=" * 48)
    g = rep.git
    print(f"repo git: {g.is_repo} · rama: {g.branch}")
    print(f"remoto:   {g.remote}")
    print(f"seguidos: {g.tracked} · se subirian (git add .): {g.would_commit} · "
          f"rutas ignoradas: {g.ignored_paths}")
    print(f".env ignorado: {'si' if rep.env_ignored else 'NO'}")

    print("\nQue se subira (por categoria):")
    for cat, info in rep.category_counts.items():
        print(f"  {cat:12s} {info['files']:5d}  {_human(info['size_bytes'])}")

    print("\nQue se subira (por carpeta raiz):")
    for top, n in rep.top_level_commit.items():
        print(f"  {top:22s} {n}")

    print(f"\nArchivos grandes: {len(rep.large_files)}")
    for f in rep.large_files[:10]:
        flag = "BLOQUEA" if f.blocks_push else "aviso"
        print(f"  [{flag}] {f.path} — {_human(f.size_bytes)}")

    print(f"\nSecretos detectados: {len(rep.secrets)}")
    for s in rep.secrets[:10]:
        print(f"  [{s.severity}] {s.path}:{s.line} — {s.kind}")

    if rep.gitignore_missing:
        print(f"\n.gitignore — faltan {len(rep.gitignore_missing)} exclusiones "
              "(ejecuta con --write-gitignore):")
        print("  " + ", ".join(rep.gitignore_missing))

    print("\nBloqueadores:")
    if rep.blockers:
        for b in rep.blockers:
            print(f"  - {b}")
    else:
        print("  (ninguno)")

    print("\n" + ("REPO LISTO PARA PUSH ✅" if rep.ready_for_push
                  else "REPO NO LISTO — resolver bloqueadores"))
    print(f"  informe: {paths['git_readiness_report']}")
    print(f"  json:    {paths['git_readiness']}")
    print("\nRecuerda: INF-003 no hace commit/push. El primer commit lo haces tu:")
    print('  git add . && git commit -m "First protected snapshot" && git push')


if __name__ == "__main__":
    main()
