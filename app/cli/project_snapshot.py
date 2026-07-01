"""CLI: genera la fotografía completa del proyecto (INF-001).

Escribe en output/system/: project_manifest.json, knowledge_snapshot.json, project_snapshot.json,
backup_plan.json, integrity_report.json, restore_plan.json. Solo lectura del proyecto; no sube
nada a Internet, no usa Git.

    python -m app.cli.project_snapshot
"""

import argparse
import datetime
import os

from app.infra.persistence import DEFAULT_OUT, load_manifest, write_snapshot_bundle
from app.infra.project_snapshot import build_project_snapshot


def main() -> None:
    ap = argparse.ArgumentParser(description="Project Snapshot (INF-001).")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--date", default=None, help="fecha (YYYY-MM-DD); por defecto hoy")
    ap.add_argument("--baseline", default=None,
                    help="manifiesto previo para comparar hashes (def: output/system/project_manifest.json)")
    args = ap.parse_args()

    as_of = args.date or datetime.date.today().isoformat()
    baseline_path = args.baseline or os.path.join(args.out, "project_manifest.json")
    baseline = load_manifest(baseline_path) if os.path.exists(baseline_path) else None

    snapshot = build_project_snapshot(args.root, as_of=as_of, baseline_manifest=baseline)
    paths = write_snapshot_bundle(snapshot, out_dir=args.out)

    print(f"Project Snapshot ({as_of}) — salud: {snapshot.health} · "
          f"listo para backup: {'SI' if snapshot.ready_for_backup else 'NO'}")
    for key in ("project_manifest", "knowledge_snapshot", "project_snapshot",
                "backup_plan", "integrity_report", "restore_plan"):
        if key in paths:
            print(f"  {key:20s} -> {paths[key]}")


if __name__ == "__main__":
    main()
