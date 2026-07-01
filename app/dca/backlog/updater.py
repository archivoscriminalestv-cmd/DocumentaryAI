"""Updater del Architectural Backlog (DCA-004).

Tras un sprint, el DCA PROPONE cambios: qué entradas se resolvieron, qué estados deben cambiar,
qué ideas nuevas aparecieron y qué relaciones añadir. Valida la propuesta contra el backlog
cargado (las entradas existen, las transiciones de estado son válidas) y devuelve un
``BacklogProposal``. NUNCA escribe el documento: el desarrollador aprueba y edita a mano.
"""

from app.dca.backlog.models import (
    ArchitecturalBacklog,
    BacklogProposal,
    EntryStatus,
    NewIdea,
    Priority,
    Section,
    StatusChange,
    ValidationIssue,
)


def _transition_ok(frm: str, to: str) -> bool:
    """Transición válida: igual, hacia REJECTED, o avance hacia delante en el ciclo."""
    if to == frm:
        return True
    if to == EntryStatus.REJECTED:
        return True
    order = EntryStatus.ORDER
    return frm in order and to in order and order[to] > order[frm]


class BacklogUpdater:
    def propose(self, backlog: ArchitecturalBacklog, sprint_review: dict) -> BacklogProposal:
        sprint = str(sprint_review.get("sprint", "UNKNOWN"))
        proposal = BacklogProposal(sprint=sprint, notes=list(sprint_review.get("notes", [])))
        changes_by_id: dict[str, StatusChange] = {}

        def add_change(entry_id: str, to_status: str, reason: str) -> None:
            entry = backlog.get(entry_id)
            if entry is None:
                proposal.issues.append(ValidationIssue(
                    "ERROR", entry_id, "la entrada no existe en el backlog"))
                return
            to_status = (to_status or "").upper()
            if to_status not in EntryStatus.ALL:
                proposal.issues.append(ValidationIssue(
                    "ERROR", entry_id, f"estado destino no permitido: '{to_status}'"))
                return
            ok = _transition_ok(entry.status, to_status)
            change = StatusChange(entry_id=entry_id, from_status=entry.status,
                                  to_status=to_status, reason=reason, accepted=ok,
                                  note="" if ok else "transición no estándar: revisar manualmente")
            if not ok:
                proposal.issues.append(ValidationIssue(
                    "WARNING", entry_id,
                    f"transición {entry.status}→{to_status} no estándar"))
            changes_by_id[entry_id] = change

        # entradas resueltas → COMPLETED
        for entry_id in sprint_review.get("resolved", []) or []:
            add_change(entry_id, EntryStatus.COMPLETED, f"resuelto en {sprint}")
            if backlog.get(entry_id) is not None:
                proposal.resolved.append(entry_id)

        # cambios de estado explícitos
        for ch in sprint_review.get("status_changes", []) or []:
            add_change(str(ch.get("id", "")), str(ch.get("to", "")),
                       str(ch.get("reason", f"actualizado en {sprint}")))

        proposal.status_changes = [changes_by_id[k] for k in sorted(changes_by_id)]

        # ideas nuevas (no se convierten en RFC automáticamente: solo se registran)
        existing_ids = {e.id for e in backlog.entries}
        for idea in sprint_review.get("new_ideas", []) or []:
            title = str(idea.get("title", "")).strip()
            if not title:
                continue
            section = str(idea.get("section", Section.OPEN_IDEAS)).upper()
            status = str(idea.get("status", EntryStatus.IDEA)).upper()
            priority = str(idea.get("priority", "")).upper()
            ni = NewIdea(title=title, section=section if section in Section.ALL else Section.OPEN_IDEAS,
                         status=status if status in EntryStatus.ALL else EntryStatus.IDEA,
                         priority=priority if priority in Priority.ALL else "",
                         description=str(idea.get("description", "")),
                         related=list(idea.get("related", []) or []))
            proposal.new_ideas.append(ni)
            from app.dca.backlog.loader import _slug
            if _slug(title) in existing_ids:
                proposal.issues.append(ValidationIssue(
                    "WARNING", _slug(title), "una idea con id similar ya existe"))

        # relaciones a añadir
        for rel in sprint_review.get("related_to_add", []) or []:
            entry_id = str(rel.get("id", ""))
            related = [r for r in (rel.get("related", []) or [])]
            if backlog.get(entry_id) is None:
                proposal.issues.append(ValidationIssue(
                    "ERROR", entry_id, "no se puede relacionar: la entrada no existe"))
                continue
            missing = [r for r in related if backlog.get(r) is None]
            for r in missing:
                proposal.issues.append(ValidationIssue(
                    "WARNING", entry_id, f"related propuesto '{r}' no existe aún"))
            proposal.related_to_add.append({"id": entry_id, "related": related})

        return proposal

    @staticmethod
    def suggest_related(backlog: ArchitecturalBacklog, keywords: list[str]) -> list[str]:
        """Sugiere (no decide) entradas cuyo id/título contiene alguna keyword. Determinista."""
        kws = [k.lower() for k in keywords if k]
        hits = []
        for e in backlog.entries:
            hay = f"{e.id} {e.title}".lower()
            if any(k in hay for k in kws):
                hits.append(e.id)
        return sorted(set(hits))
