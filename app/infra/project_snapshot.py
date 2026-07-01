"""Project Snapshot (INF-001) — fotografía completa del proyecto.

Compone manifiesto + conocimiento + plan de backup + integridad + plan de restauración para
responder: "¿cómo era DocumentaryAI exactamente el día X?". Determinista (la fecha se inyecta).
"""

from app.infra import UNKNOWN
from app.infra.backup_manager import build_backup_plan
from app.infra.integrity import check_integrity
from app.infra.knowledge_snapshot import build_knowledge_snapshot
from app.infra.manifest import build_manifest
from app.infra.models import Health, ProjectSnapshot
from app.infra.restore import build_restore_plan


def build_project_snapshot(root: str = ".", as_of: str = UNKNOWN,
                           baseline_manifest: dict | None = None) -> ProjectSnapshot:
    manifest = build_manifest(root, as_of=as_of)
    knowledge = build_knowledge_snapshot(root)
    backup = build_backup_plan(root)
    integrity = check_integrity(root, baseline_manifest=baseline_manifest)
    restore = build_restore_plan(root)

    ready = integrity.health != Health.CRITICAL
    return ProjectSnapshot(
        generated_for_date=as_of or UNKNOWN,
        health=integrity.health,
        ready_for_backup=ready,
        manifest=manifest, knowledge=knowledge, backup_plan=backup,
        integrity=integrity, restore_plan=restore)
