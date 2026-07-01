"""Planificador de colocación de evidencias y recreaciones (NAR-001).

Decide QUÉ material aparece en cada segmento y POR QUÉ, con tres reglas inquebrantables:

1. La evidencia REAL tiene prioridad. Si la dimensión tiene material, se coloca.
2. Donde NO hay evidencia real, solo se justifica una RECREACIÓN si el ECE detectó un
   candidato para esa categoría (recreación = explícita y trazable, nunca encubierta).
3. Si no hay ni evidencia ni recreación, el hueco se convierte en una PREGUNTA ABIERTA para
   el espectador. Nunca se inventa material (UNKNOWN sobre inventar).
"""

from app.nar.models import (
    EvidencePlacement,
    NarrativeContext,
    NarrativeSegment,
    RecreationPlacement,
    ViewerQuestion,
    slugify,
)
from app.nar.vocabulary import EvidenceUse as U
from app.nar.vocabulary import NarrativeBeat as B
from app.nar.vocabulary import QuestionType

# Qué dimensiones de cobertura quiere cada beat, y con qué función narrativa.
_BEAT_EVIDENCE: dict[str, list[tuple[str, str]]] = {
    B.HOOK: [("photographs", U.REVEAL), ("news", U.REVEAL)],
    B.SETUP: [("maps", U.LOCATE), ("locations", U.ESTABLISH)],
    B.INTRODUCE_SUBJECT: [("photographs", U.INTRODUCE), ("people", U.INTRODUCE)],
    B.BACKGROUND: [("news", U.SUPPORT), ("chronology", U.CHRONICLE)],
    B.INCITING_INCIDENT: [("news", U.REVEAL), ("chronology", U.CHRONICLE)],
    B.RISING_ACTION: [("documents", U.SUPPORT), ("news", U.SUPPORT)],
    B.INVESTIGATION: [("documents", U.SUPPORT), ("maps", U.LOCATE)],
    B.CLUE: [("documents", U.REVEAL), ("photographs", U.CORROBORATE)],
    B.COMPLICATION: [("news", U.CONTRAST), ("documents", U.CONTRAST)],
    B.RED_HERRING: [("news", U.CONTRAST)],
    B.MIDPOINT: [("videos", U.REVEAL), ("documents", U.REVEAL)],
    B.TURNING_POINT: [("videos", U.REVEAL), ("documents", U.CONTRAST)],
    B.REVELATION: [("videos", U.REVEAL), ("photographs", U.REVEAL)],
    B.CLIMAX: [("videos", U.REVEAL), ("news", U.CONTRAST)],
    B.FALLING_ACTION: [("chronology", U.CHRONICLE), ("news", U.SUPPORT)],
    B.AFTERMATH: [("chronology", U.CHRONICLE), ("photographs", U.ILLUSTRATE)],
    B.RESOLUTION: [("chronology", U.CHRONICLE)],
    B.REFLECTION: [("photographs", U.ILLUSTRATE)],
    B.OPEN_QUESTION: [("documents", U.REVEAL)],
    # Viaje del héroe / biografía
    B.CALL_TO_ADVENTURE: [("people", U.INTRODUCE), ("news", U.SUPPORT)],
    B.THRESHOLD: [("news", U.SUPPORT)],
    B.ORDEAL: [("news", U.CONTRAST), ("documents", U.SUPPORT)],
    B.REWARD: [("photographs", U.ILLUSTRATE)],
    B.RETURN: [("chronology", U.CHRONICLE)],
}

_DEFAULT_EVIDENCE = [("news", U.SUPPORT)]

# Dimensión → categorías de recreación admisibles (deben venir del ECE).
_RECREATION_CATEGORIES = {
    "documents": {"COURT_DOCUMENT", "POLICE_DOCUMENT", "PUBLIC_RECORD", "OFFICIAL_STATEMENT"},
    "photographs": {"PHOTO", "SCENE_PHOTO", "FORENSIC_IMAGE"},
    "people": {"PHOTO"},
    "maps": {"MAP", "SATELLITE"},
    "videos": {"ARCHIVE_VIDEO", "TV_REPORT", "VIDEO", "INTERVIEW"},
    "chronology": {"TIMELINE"},
    "news": {"NEWS", "NEWSPAPER"},
}

_QUESTION_TYPE = {
    "photographs": QuestionType.WHO, "people": QuestionType.WHO,
    "maps": QuestionType.WHERE, "locations": QuestionType.WHERE,
    "chronology": QuestionType.WHEN, "audio": QuestionType.WHAT,
    "documents": QuestionType.WHAT, "news": QuestionType.WHAT, "videos": QuestionType.WHAT,
}


class EvidencePlacementPlanner:
    def place(self, context: NarrativeContext, segment: NarrativeSegment
              ) -> tuple[list[EvidencePlacement], list[RecreationPlacement], list[ViewerQuestion]]:
        rules = _BEAT_EVIDENCE.get(segment.beat, _DEFAULT_EVIDENCE)
        placements: list[EvidencePlacement] = []
        recreations: list[RecreationPlacement] = []
        questions: list[ViewerQuestion] = []
        seen: set[str] = set()

        for dimension, use in rules:
            if dimension in seen:
                continue
            seen.add(dimension)
            cd = context.dimension(dimension)
            if cd and cd.discovered > 0:
                placements.append(EvidencePlacement(
                    dimension=dimension, use=use,
                    reason=f"dimensión '{dimension}' {cd.state} ({cd.discovered} disponibles)",
                    coverage_state=cd.state, available=cd.discovered,
                    evidence_ids=list(cd.evidence_ids[:3])))
                continue

            # No hay evidencia real: ¿recreación justificada o pregunta abierta?
            rc = self._recreation_for(context, dimension)
            if rc is not None:
                recreations.append(RecreationPlacement(
                    category=rc.category,
                    reason=(f"'{dimension}' sin evidencia real; el ECE detectó un candidato de "
                            f"recreación ({rc.category})"),
                    factual_basis=dict(rc.factual_basis)))
            else:
                questions.append(self._gap_question(context, dimension, segment.index))

        return placements, recreations, questions

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def _recreation_for(context: NarrativeContext, dimension: str):
        cats = _RECREATION_CATEGORIES.get(dimension, set())
        for rc in context.recreation_candidates:
            if rc.category in cats and rc.existing_coverage == "MISSING":
                return rc
        return None

    @staticmethod
    def _gap_question(context: NarrativeContext, dimension: str, seg_index: int) -> ViewerQuestion:
        qtype = _QUESTION_TYPE.get(dimension, QuestionType.WHAT)
        if qtype == QuestionType.WHO:
            target = context.subject or (context.people[0] if context.people else context.title)
        elif qtype == QuestionType.WHERE:
            target = context.locations[0] if context.locations else context.title
        elif qtype == QuestionType.WHEN:
            target = context.events[0] if context.events else context.title
        else:
            target = context.subject or context.title or context.case_id
        target = target or context.case_id
        qid = f"q_{slugify(target)}_{dimension}"
        return ViewerQuestion(id=qid, type=qtype, target=target,
                              origin=f"missing_coverage:{dimension}", opened_in=seg_index)
