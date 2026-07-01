"""Recreation Candidates (ECE) — DÓNDE podría hacer falta una recreación (no se genera).

Principio fundamental: la evidencia real tiene prioridad absoluta. Solo se proponen
candidatos para necesidades REQUERIDAS (mínimo > 0) que NO están cubiertas por evidencia
real (descubierto < mínimo). Nunca se propone una recreación si hay evidencia suficiente.
Cada candidato indica los hechos reales en los que deberá basarse; la IA solo complementa.
"""

from app.eae.planner.models import EvidenceCategory as C
from app.ece.models import CoverageState, RecreationCandidate

# Tipo de recreación sugerido por categoría (determinista; solo una sugerencia).
_SUGGESTED_TYPE = {
    C.SCENE_PHOTO: "scene_reconstruction", C.PRESS_CONFERENCE: "scene_reconstruction",
    C.INTERVIEW: "scene_reconstruction", C.VIDEO: "scene_reconstruction",
    C.ARCHIVE_VIDEO: "scene_reconstruction", C.TV_REPORT: "scene_reconstruction",
    C.MAP: "animated_map", C.SATELLITE: "animated_map",
    C.PHOTO: "portrait_illustration",
    C.COURT_DOCUMENT: "document_visualization", C.POLICE_DOCUMENT: "document_visualization",
    C.PUBLIC_RECORD: "document_visualization", C.OFFICIAL_STATEMENT: "document_visualization",
    C.FORENSIC_IMAGE: "3d_reconstruction",
    C.TIMELINE: "timeline_animation", C.NEWS: "headline_montage",
    C.NEWSPAPER: "headline_montage", C.AUDIO: "audio_dramatization", C.BOOK: "illustration",
}


def detect_recreation_candidates(plan, discovery_plan) -> list[RecreationCandidate]:
    profile = plan.profile
    case_facts = {
        "people": list(profile.people) if profile else [],
        "locations": list(profile.locations) if profile else [],
        "events": list(profile.events) if profile else [],
        "time_period": getattr(profile, "time_period", "") if profile else "",
    }

    candidates: list[RecreationCandidate] = []
    for need in discovery_plan.needs:
        if need.minimum <= 0:
            continue                          # opcional: no es un hueco requerido
        if need.discovered >= need.minimum:
            continue                          # evidencia real suficiente -> NUNCA recrear
        missing_count = need.minimum - need.discovered
        existing = (CoverageState.PARTIAL if need.discovered > 0 else CoverageState.MISSING)
        target = need.target if need.target != "case" else (profile.title if profile else "case")
        candidates.append(RecreationCandidate(
            id=f"recreation:{need.need_id.split(':', 1)[-1]}",
            story_segment=f"{need.category} — {target}",
            reason=(f"evidencia real insuficiente ({need.discovered}/{need.minimum}); "
                    f"hueco documental requerido"),
            existing_coverage=existing,
            suggested_type=_SUGGESTED_TYPE.get(need.category, "illustration"),
            available_evidence=list(need.evidence_ids),
            missing_evidence=[f"{need.category} x{missing_count}"],
            factual_basis={
                "target": target, "category": need.category,
                "based_on_evidence": list(need.evidence_ids),
                "case_facts": case_facts,
                "note": ("basar EXCLUSIVAMENTE en hechos verificados; la recreación nunca "
                         "sustituye ni se mezcla con la evidencia real"),
            }))
    candidates.sort(key=lambda c: c.id)
    return candidates
