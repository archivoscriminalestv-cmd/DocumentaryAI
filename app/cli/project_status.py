"""CLI: estado del proyecto, legible (INF-001).

Resume versión, arquitectura, conocimiento, integridad, backups, carpetas críticas, archivos
faltantes, salud y si está listo para un backup. Solo lectura; no escribe nada por defecto.

    python -m app.cli.project_status
"""

import argparse
import datetime
import os

from app.infra import INFRA_VERSION
from app.infra.models import BackupClass
from app.infra.persistence import DEFAULT_OUT, load_manifest
from app.infra.project_snapshot import build_project_snapshot


def _human(n: int) -> str:
    size = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{n} B"


def main() -> None:
    ap = argparse.ArgumentParser(description="Project Status (INF-001).")
    ap.add_argument("--root", default=".")
    ap.add_argument("--date", default=None)
    args = ap.parse_args()

    as_of = args.date or datetime.date.today().isoformat()
    baseline_path = os.path.join(DEFAULT_OUT, "project_manifest.json")
    baseline = load_manifest(baseline_path) if os.path.exists(baseline_path) else None

    snap = build_project_snapshot(args.root, as_of=as_of, baseline_manifest=baseline)
    m, k, bp, ig = snap.manifest, snap.knowledge, snap.backup_plan, snap.integrity

    line = "=" * 40
    print(line)
    print("DOCUMENTARYAI PROJECT STATUS")
    print(line)

    print("\nVersion")
    print(f"  infra: {INFRA_VERSION} · schema: {m.schema_version} · fecha: {snap.generated_for_date}")

    print("\nArchitecture")
    print(f"  subsistemas: {m.subsystem_count} · capacidades: {m.capability_count}")
    print(f"  ADR: {len(m.adrs)} · RFC: {len(m.rfcs)} · SPEC: {len(m.specs)} · tests: {m.test_count}")
    print(f"  artefactos hasheados: {len(m.artifact_hashes)}")

    print("\nKnowledge")
    print(f"  documentales: {k.documentaries_learned} · planos: {k.shots_analyzed} · "
          f"escenas: {k.scenes_analyzed} · horas: {k.hours_learned}")
    print(f"  estilos: {len(k.styles)} · tamaño knowledge: {_human(k.knowledge_size_bytes)}")

    print("\nIntegrity")
    s = ig.to_dict()["summary"]
    print(f"  estado: {ig.health} · errores: {s['errors']} · avisos: {s['warnings']} · "
          f"comprobado: {ig.checked}" + (" · (baseline)" if ig.baseline_used else ""))

    print("\nBackups")
    t = bp.to_dict()["totals"]
    print(f"  CRITICAL: {t['critical']} ({t['critical_present']} presentes, "
          f"{_human(t['critical_size_bytes'])})")
    print(f"  IMPORTANT: {t['important']} ({_human(t['important_size_bytes'])})")
    print(f"  TEMPORARY: {t['temporary']} (nunca se copian)")
    print(f"  tamaño total de backup: {_human(t['backup_size_bytes'])}")

    print("\nCritical folders")
    for e in bp.critical:
        if e.classification == BackupClass.CRITICAL and "/" not in e.path and "." not in e.path:
            mark = "OK " if e.exists else "!! "
            print(f"  [{mark}] {e.path}")

    print("\nMissing files")
    missing = ig.by_kind("missing_file") + ig.by_kind("missing_folder")
    if not missing:
        print("  (ninguno)")
    for i in missing:
        print(f"  - {i.path}: {i.detail}")

    print("\nProject health")
    print(f"  {snap.health}")

    print("\nReady for backup")
    print(f"  {'SI — el proyecto puede respaldarse de forma completa' if snap.ready_for_backup else 'NO — resolver los problemas de integridad'}")
    print(line)


if __name__ == "__main__":
    main()
