"""EvidenceInvestigationPlanner (EAE-002).

Recibe ÚNICAMENTE un ``CaseProfile`` y produce un ``InvestigationPlan`` completamente
determinista: necesidades de evidencia con prioridad y cobertura mínima/ideal, tareas de
búsqueda y adquisición (que minimizan descargas), y un ``EvidenceManifest`` del proyecto.
NO consulta Internet, NO descarga, NO usa IA. Solo planifica con reglas + plantillas.
"""

from app.eae.planner.models import (
    AcquisitionTask,
    CaseProfile,
    CoverageRequirement,
    EvidenceCategory as C,
    EvidenceManifest,
    EvidenceNeed,
    EvidencePriority as P,
    ExpectedEvidence,
    InvestigationPlan,
    InvestigationTarget,
    ResearchStage,
    SearchTask,
    slugify,
)

# Proveedores prioritarios sugeridos por categoría (hints; no se llama a ninguno).
_CATEGORY_SOURCES = {
    C.PHOTO: ["wikimedia", "internet_archive"], C.VIDEO: ["youtube", "internet_archive"],
    C.PRESS_CONFERENCE: ["youtube"], C.NEWS: ["news", "wayback"],
    C.NEWSPAPER: ["news", "internet_archive"], C.COURT_DOCUMENT: ["government"],
    C.POLICE_DOCUMENT: ["government"], C.MAP: ["wikimedia"], C.SATELLITE: ["wikimedia"],
    C.INTERVIEW: ["youtube"], C.TV_REPORT: ["youtube", "internet_archive"],
    C.SOCIAL_POST: ["wayback"], C.BOOK: ["internet_archive"], C.AUDIO: ["internet_archive"],
    C.TIMELINE: ["news", "government"], C.PUBLIC_RECORD: ["government"],
    C.OFFICIAL_STATEMENT: ["government"], C.FORENSIC_IMAGE: ["government"],
    C.SCENE_PHOTO: ["news", "government"], C.ARCHIVE_VIDEO: ["internet_archive", "youtube"],
}

# Plantillas por género: necesidades a nivel de CASO (categoría, prioridad, mín, ideal).
_GENRE_TEMPLATES = {
    "generic": [(C.PHOTO, P.HIGH, 1, 3), (C.VIDEO, P.MEDIUM, 1, 2), (C.NEWS, P.MEDIUM, 1, 3),
                (C.TIMELINE, P.HIGH, 1, 1), (C.MAP, P.LOW, 0, 1)],
    "true_crime": [(C.SCENE_PHOTO, P.CRITICAL, 1, 3), (C.COURT_DOCUMENT, P.HIGH, 1, 2),
                   (C.POLICE_DOCUMENT, P.HIGH, 1, 2), (C.NEWS, P.HIGH, 2, 4),
                   (C.PRESS_CONFERENCE, P.MEDIUM, 0, 1), (C.TIMELINE, P.CRITICAL, 1, 1),
                   (C.MAP, P.MEDIUM, 1, 1), (C.ARCHIVE_VIDEO, P.MEDIUM, 0, 2),
                   (C.OFFICIAL_STATEMENT, P.MEDIUM, 0, 1)],
    "history": [(C.ARCHIVE_VIDEO, P.HIGH, 1, 3), (C.PHOTO, P.HIGH, 2, 5),
                (C.NEWSPAPER, P.MEDIUM, 1, 3), (C.MAP, P.MEDIUM, 1, 2),
                (C.BOOK, P.LOW, 0, 1), (C.TIMELINE, P.HIGH, 1, 1)],
    "biography": [(C.PHOTO, P.CRITICAL, 2, 5), (C.INTERVIEW, P.HIGH, 1, 3),
                  (C.ARCHIVE_VIDEO, P.MEDIUM, 1, 2), (C.NEWS, P.MEDIUM, 1, 2),
                  (C.TIMELINE, P.HIGH, 1, 1)],
    "nature": [(C.VIDEO, P.CRITICAL, 2, 5), (C.PHOTO, P.HIGH, 2, 5),
               (C.MAP, P.MEDIUM, 1, 2), (C.SATELLITE, P.MEDIUM, 0, 2)],
}


class EvidenceInvestigationPlanner:
    def plan(self, profile: CaseProfile) -> InvestigationPlan:
        needs: dict[str, EvidenceNeed] = {}        # id -> need (dedup por id)

        def _add(category, priority, minimum, ideal, target, rationale):
            nid = f"need:{slugify(category)}:{slugify(target)}"
            if nid in needs:                        # dedup: conserva la prioridad más alta
                if P.RANK[priority] < P.RANK[needs[nid].priority]:
                    needs[nid].priority = priority
                return
            needs[nid] = EvidenceNeed(
                id=nid, category=category, priority=priority, target=target,
                requirement=CoverageRequirement(minimum=minimum, ideal=ideal),
                sources=list(_CATEGORY_SOURCES.get(category, [])), rationale=rationale)

        # 1) Necesidades de caso según el género.
        template = _GENRE_TEMPLATES.get(profile.genre, _GENRE_TEMPLATES["generic"])
        for category, priority, minimum, ideal in template:
            _add(category, priority, minimum, ideal, "case", f"plantilla de género '{profile.genre}'")

        # 2) Reglas por entidad (deterministas).
        for person in profile.people:
            _add(C.PHOTO, P.HIGH, 1, 2, person, "retrato/identificación de persona relevante")
        for location in profile.locations:
            if profile.genre == "true_crime":
                _add(C.SCENE_PHOTO, P.CRITICAL, 1, 2, location, "imagen del lugar de los hechos")
            _add(C.MAP, P.MEDIUM, 1, 1, location, "localización geográfica")
        for event in profile.events:
            _add(C.NEWS, P.HIGH, 1, 2, event, "cobertura informativa del evento")

        ordered = sorted(needs.values(), key=lambda n: (P.RANK[n.priority], n.category, n.target))

        # 3) Tareas (una de búsqueda + una de adquisición por necesidad; mínimo = minimiza).
        search_tasks, acq_tasks = [], []
        for n in ordered:
            terms = [t for t in (profile.subject, "" if n.target == "case" else n.target,
                                 n.category.lower().replace("_", " ")) if t]
            search_tasks.append(SearchTask(
                id=f"search:{n.id.split(':', 1)[1]}", need_id=n.id, category=n.category,
                target=n.target, priority=n.priority, query_terms=terms, sources=n.sources))
            acq_tasks.append(AcquisitionTask(
                id=f"acq:{n.id.split(':', 1)[1]}", need_id=n.id, category=n.category,
                target=n.target, priority=n.priority, target_count=n.requirement.minimum))

        targets = self._targets(profile, ordered)
        manifest = self._manifest(profile, ordered)
        summary = self._summary(ordered)

        return InvestigationPlan(
            case_id=profile.case_id, profile=profile, manifest=manifest, targets=targets,
            needs=ordered, search_tasks=search_tasks, acquisition_tasks=acq_tasks,
            stages=list(ResearchStage.ORDER), coverage_summary=summary,
            notes=[
                "EAE-002: plan determinista; sin red, sin descargas, sin IA.",
                "Minimiza descargas: la adquisición apunta a la cantidad MÍNIMA por necesidad.",
                "El material será TEMPORAL (workspace del proyecto); el conocimiento es permanente.",
            ])

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _targets(profile: CaseProfile, needs: list[EvidenceNeed]) -> list[InvestigationTarget]:
        by_target: dict[str, list[str]] = {}
        for n in needs:
            by_target.setdefault(n.target, []).append(n.id)
        targets = [InvestigationTarget(id="target:case", kind="case", name=profile.title or "case",
                                       need_ids=by_target.get("case", []))]
        for kind, names in (("person", profile.people), ("location", profile.locations),
                            ("event", profile.events)):
            for name in names:
                targets.append(InvestigationTarget(
                    id=f"target:{kind}:{slugify(name)}", kind=kind, name=name,
                    need_ids=by_target.get(name, [])))
        return targets

    @staticmethod
    def _manifest(profile: CaseProfile, needs: list[EvidenceNeed]) -> EvidenceManifest:
        desired, pending, expected = {}, [], []
        for n in needs:
            agg = desired.setdefault(n.category, {"minimum": 0, "ideal": 0})
            agg["minimum"] += n.requirement.minimum
            agg["ideal"] += n.requirement.ideal
            expected.append(ExpectedEvidence(target=n.target, category=n.category,
                                             description=n.rationale))
            if n.requirement.missing > 0:
                pending.append(n.id)
        sources = sorted({s for n in needs for s in n.sources})
        return EvidenceManifest(
            case_id=profile.case_id, title=profile.title, people=list(profile.people),
            locations=list(profile.locations), timeline=list(profile.events),
            expected_material=expected, desired_coverage=desired,
            priority_sources=profile.priority_sources or sources,
            constraints=list(profile.constraints), licenses=list(profile.license_requirements),
            coverage_status={"overall_coverage": 0.0, "pending": len(pending)},
            pending_material=pending, acquired_material=[])

    @staticmethod
    def _summary(needs: list[EvidenceNeed]) -> dict:
        by_priority: dict[str, int] = {}
        total_min = 0
        for n in needs:
            by_priority[n.priority] = by_priority.get(n.priority, 0) + 1
            total_min += n.requirement.minimum
        return {
            "total_needs": len(needs), "by_priority": by_priority,
            "total_minimum": total_min, "total_acquired": 0, "overall_coverage": 0.0,
            "pending_count": sum(1 for n in needs if n.requirement.missing > 0),
        }
