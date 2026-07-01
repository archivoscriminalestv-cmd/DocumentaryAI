"""Modelos del subsistema de protección (INF-001).

Tipados, serializables y deterministas. Describen el estado del proyecto y los planes de backup,
integridad y restauración. Sin binarios: solo metadatos, recuentos y hashes.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.infra import INFRA_SCHEMA_VERSION


class BackupClass:
    CRITICAL = "CRITICAL"        # nunca perder
    IMPORTANT = "IMPORTANT"      # recomendado
    TEMPORARY = "TEMPORARY"      # nunca copiar
    ALL = (CRITICAL, IMPORTANT, TEMPORARY)


class Health:
    OK = "OK"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


@dataclass
class ArtifactHash:
    path: str
    sha256: str
    size_bytes: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectManifest:
    """Documento determinista con la identidad completa del proyecto + hashes críticos."""

    schema_version: str = INFRA_SCHEMA_VERSION
    infra_version: str = ""
    generated_for_date: str = "UNKNOWN"
    root: str = "."
    engines: list[str] = field(default_factory=list)
    subsystem_count: int = 0
    adrs: list[str] = field(default_factory=list)
    rfcs: list[str] = field(default_factory=list)
    specs: list[str] = field(default_factory=list)
    test_count: int = 0
    capability_count: Any = "UNKNOWN"
    documentaries_learned: int = 0
    shots_analyzed: int = 0
    scenes_analyzed: int = 0
    hours_learned: float = 0.0
    knowledge_size_bytes: int = 0
    project_size_bytes: int = 0
    artifact_hashes: list[ArtifactHash] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["artifact_hashes"] = [a.to_dict() for a in self.artifact_hashes]
        d["totals"] = {
            "engines": len(self.engines),
            "adrs": len(self.adrs),
            "rfcs": len(self.rfcs),
            "specs": len(self.specs),
            "hashed_artifacts": len(self.artifact_hashes),
        }
        return d


@dataclass
class KnowledgeSnapshot:
    """Resumen completo del estado del conocimiento. Nunca copia vídeos ni output."""

    schema_version: str = INFRA_SCHEMA_VERSION
    documentaries_learned: int = 0
    shots_analyzed: int = 0
    scenes_analyzed: int = 0
    hours_learned: float = 0.0
    styles: list[str] = field(default_factory=list)
    documentary_count: int = 0
    statistics: dict = field(default_factory=dict)
    style_hashes: list[ArtifactHash] = field(default_factory=list)
    knowledge_size_bytes: int = 0
    note: str = "Solo conocimiento. Nunca vídeos, nunca output, nunca binarios."

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["style_hashes"] = [a.to_dict() for a in self.style_hashes]
        return d


@dataclass
class BackupEntry:
    path: str
    classification: str
    exists: bool = False
    reason: str = ""
    file_count: int = 0
    size_bytes: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BackupPlan:
    schema_version: str = INFRA_SCHEMA_VERSION
    critical: list[BackupEntry] = field(default_factory=list)
    important: list[BackupEntry] = field(default_factory=list)
    temporary: list[BackupEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        crit_size = sum(e.size_bytes for e in self.critical if e.exists)
        imp_size = sum(e.size_bytes for e in self.important if e.exists)
        return {
            "schema_version": self.schema_version,
            "critical": [e.to_dict() for e in self.critical],
            "important": [e.to_dict() for e in self.important],
            "temporary": [e.to_dict() for e in self.temporary],
            "totals": {
                "critical": len(self.critical),
                "important": len(self.important),
                "temporary": len(self.temporary),
                "critical_present": sum(1 for e in self.critical if e.exists),
                "critical_size_bytes": crit_size,
                "important_size_bytes": imp_size,
                "backup_size_bytes": crit_size + imp_size,
            },
        }


@dataclass
class IntegrityIssue:
    kind: str                    # missing_file | missing_folder | hash_mismatch | corrupt_knowledge | missing_doc
    path: str
    detail: str = ""
    severity: str = "ERROR"      # ERROR | WARNING

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IntegrityReport:
    schema_version: str = INFRA_SCHEMA_VERSION
    checked: int = 0
    health: str = Health.OK
    issues: list[IntegrityIssue] = field(default_factory=list)
    baseline_used: bool = False

    @property
    def errors(self) -> int:
        return sum(1 for i in self.issues if i.severity == "ERROR")

    @property
    def warnings(self) -> int:
        return sum(1 for i in self.issues if i.severity == "WARNING")

    def by_kind(self, kind: str) -> list[IntegrityIssue]:
        return [i for i in self.issues if i.kind == kind]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "checked": self.checked,
            "health": self.health,
            "baseline_used": self.baseline_used,
            "summary": {
                "errors": self.errors,
                "warnings": self.warnings,
                "missing_files": len(self.by_kind("missing_file")),
                "missing_folders": len(self.by_kind("missing_folder")),
                "hash_mismatches": len(self.by_kind("hash_mismatch")),
                "corrupt_knowledge": len(self.by_kind("corrupt_knowledge")),
                "missing_docs": len(self.by_kind("missing_doc")),
            },
            "issues": [i.to_dict() for i in self.issues],
        }


@dataclass
class RestoreStep:
    order: int
    action: str
    target: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RestorePlan:
    schema_version: str = INFRA_SCHEMA_VERSION
    steps: list[RestoreStep] = field(default_factory=list)
    do_not_restore: list[str] = field(default_factory=list)
    requirements_file: str = "UNKNOWN"
    note: str = "Reconstruye la estructura desde un backup. Nunca restaura binarios temporales."

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "requirements_file": self.requirements_file,
            "note": self.note,
            "steps": [s.to_dict() for s in self.steps],
            "do_not_restore": list(self.do_not_restore),
        }


@dataclass
class ProjectSnapshot:
    """Fotografía completa: responde '¿cómo era DocumentaryAI exactamente el día X?'."""

    schema_version: str = INFRA_SCHEMA_VERSION
    generated_for_date: str = "UNKNOWN"
    health: str = Health.OK
    ready_for_backup: bool = False
    manifest: ProjectManifest | None = None
    knowledge: KnowledgeSnapshot | None = None
    backup_plan: BackupPlan | None = None
    integrity: IntegrityReport | None = None
    restore_plan: RestorePlan | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_for_date": self.generated_for_date,
            "health": self.health,
            "ready_for_backup": self.ready_for_backup,
            "manifest": self.manifest.to_dict() if self.manifest else None,
            "knowledge": self.knowledge.to_dict() if self.knowledge else None,
            "backup_plan": self.backup_plan.to_dict() if self.backup_plan else None,
            "integrity": self.integrity.to_dict() if self.integrity else None,
            "restore_plan": self.restore_plan.to_dict() if self.restore_plan else None,
        }
