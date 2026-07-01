"""Coverage Analysis (ECE) — cobertura documental por dimensiones.

Clasifica cada dimensión como COMPLETE / PARTIAL / MISSING a partir de las evidencias
descubiertas y los mínimos del plan. Determinista; no inventa.
"""

from app.eae.planner.models import EvidenceCategory as C
from app.ece.models import CoverageDimension, CoverageReport, CoverageState

# Dimensiones por categorías de evidencia.
_CATEGORY_DIMENSIONS = {
    "photographs": {C.PHOTO, C.SCENE_PHOTO, C.FORENSIC_IMAGE},
    "videos": {C.VIDEO, C.ARCHIVE_VIDEO, C.TV_REPORT, C.INTERVIEW, C.PRESS_CONFERENCE},
    "documents": {C.COURT_DOCUMENT, C.POLICE_DOCUMENT, C.PUBLIC_RECORD, C.OFFICIAL_STATEMENT,
                  C.BOOK},
    "audio": {C.AUDIO},
    "maps": {C.MAP, C.SATELLITE},
    "news": {C.NEWS, C.NEWSPAPER},
}


def _state(required: int, discovered: int) -> str:
    if discovered == 0:
        return CoverageState.MISSING if required > 0 else CoverageState.MISSING
    if discovered >= required:
        return CoverageState.COMPLETE
    return CoverageState.PARTIAL


def _entity_state(required: int, covered: int) -> str:
    if required == 0:
        return CoverageState.COMPLETE          # nada que cubrir
    if covered == 0:
        return CoverageState.MISSING
    return CoverageState.COMPLETE if covered >= required else CoverageState.PARTIAL


def analyze_coverage(plan, discovery_plan) -> CoverageReport:
    profile = plan.profile
    people = list(profile.people) if profile else []
    locations = list(profile.locations) if profile else []
    events = list(profile.events) if profile else []

    discovered = discovery_plan.discovered
    min_by_cat: dict[str, int] = {}
    for need in plan.needs:
        min_by_cat[need.category] = min_by_cat.get(need.category, 0) + need.requirement.minimum

    dims: list[CoverageDimension] = []

    # --- dimensiones por entidad ---------------------------------------------
    def _entity_dim(name, entity_names, kinds):
        ids_by_entity = {n: [] for n in entity_names}
        for ev in discovered:
            if ev.target in ids_by_entity and ev.category in kinds:
                ids_by_entity[ev.target].append(ev.id)
        covered = sum(1 for n in entity_names if ids_by_entity[n])
        return CoverageDimension(
            name=name, required=len(entity_names), discovered=covered,
            state=_entity_state(len(entity_names), covered),
            evidence_ids=sorted(i for ids in ids_by_entity.values() for i in ids),
            detail={n: len(ids_by_entity[n]) for n in entity_names})

    dims.append(_entity_dim("people", people, _CATEGORY_DIMENSIONS["photographs"]))
    dims.append(_entity_dim("locations", locations,
                            _CATEGORY_DIMENSIONS["maps"] | {C.SCENE_PHOTO}))

    # --- cronología ----------------------------------------------------------
    dated_ids = sorted(ev.id for ev in discovered if ev.date and ev.date != "UNKNOWN")
    timeline_ids = sorted(ev.id for ev in discovered if ev.category == C.TIMELINE)
    chrono_ids = sorted(set(dated_ids) | set(timeline_ids))
    chrono_required = max(len(events), min_by_cat.get(C.TIMELINE, 0))
    dims.append(CoverageDimension(
        name="chronology", required=chrono_required, discovered=len(chrono_ids),
        state=_state(chrono_required, len(chrono_ids)), evidence_ids=chrono_ids,
        detail={"dated_evidence": len(dated_ids), "timeline_evidence": len(timeline_ids)}))

    # --- dimensiones por categoría -------------------------------------------
    for name, cats in _CATEGORY_DIMENSIONS.items():
        required = sum(min_by_cat.get(c, 0) for c in cats)
        ids = sorted(ev.id for ev in discovered if ev.category in cats)
        dims.append(CoverageDimension(
            name=name, required=required, discovered=len(ids),
            state=_state(required, len(ids)), evidence_ids=ids))

    dims.sort(key=lambda d: d.name)
    summary = {
        "dimensions": len(dims),
        "complete": sum(1 for d in dims if d.state == CoverageState.COMPLETE),
        "partial": sum(1 for d in dims if d.state == CoverageState.PARTIAL),
        "missing": sum(1 for d in dims if d.state == CoverageState.MISSING),
    }
    return CoverageReport(case_id=plan.case_id, dimensions=dims, summary=summary)
