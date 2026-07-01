"""Validador del Architectural Backlog (DCA-004).

Comprueba que el documento es coherente y respeta las reglas. Solo lectura: devuelve una lista
de incidencias (ERROR/WARNING) deterministas; nunca modifica el backlog.
"""

from app.dca.backlog.models import (
    ArchitecturalBacklog,
    EntryStatus,
    HypothesisStatus,
    Priority,
    Section,
    ValidationIssue,
)


class BacklogValidator:
    def validate(self, backlog: ArchitecturalBacklog) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []

        def err(eid: str, msg: str) -> None:
            issues.append(ValidationIssue("ERROR", eid, msg))

        def warn(eid: str, msg: str) -> None:
            issues.append(ValidationIssue("WARNING", eid, msg))

        # ids únicos
        seen: dict[str, int] = {}
        for e in backlog.entries:
            seen[e.id] = seen.get(e.id, 0) + 1
        for eid, n in sorted(seen.items()):
            if n > 1:
                err(eid, f"id duplicado ({n} veces)")

        ids = set(seen)
        for e in backlog.entries:
            # estado permitido
            if e.status not in EntryStatus.ALL:
                err(e.id, f"estado no permitido: '{e.status}'")
            # Strategic Priorities → prioridad obligatoria y válida
            if e.section == Section.STRATEGIC_PRIORITIES:
                if not e.priority:
                    err(e.id, "entrada en Strategic Priorities sin prioridad")
                elif e.priority not in Priority.ALL:
                    err(e.id, f"prioridad no válida: '{e.priority}'")
            elif e.priority:
                warn(e.id, f"prioridad '{e.priority}' fuera de Strategic Priorities")
            # Hypotheses → estado de hipótesis obligatorio y válido
            if e.section == Section.HYPOTHESES:
                if not e.hypothesis_status:
                    err(e.id, "hipótesis sin status (UNKNOWN/VALIDATED/REJECTED)")
                elif e.hypothesis_status not in HypothesisStatus.ALL:
                    err(e.id, f"status de hipótesis no válido: '{e.hypothesis_status}'")
            elif e.hypothesis_status:
                warn(e.id, "hypothesis_status fuera de la sección Hypotheses")
            # Completed → debe estar COMPLETED o REJECTED
            if e.section == Section.COMPLETED and e.status not in (EntryStatus.COMPLETED, EntryStatus.REJECTED):
                err(e.id, f"en Completed pero estado '{e.status}' (debe ser COMPLETED/REJECTED)")
            # related deben resolver
            for rel in e.related:
                if rel not in ids:
                    warn(e.id, f"related '{rel}' no existe en el backlog")
            # descripción mínima
            if not e.description:
                warn(e.id, "entrada sin descripción")

        return issues
