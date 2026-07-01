"""Tests del Narrative Intelligence Engine (NAR-001) — deterministas, sin red, sin IA.

Verifican que el motor DECIDE cómo contar la historia (estructura, emoción, evidencias,
mecanismos, narración) sin escribir texto, priorizando evidencia real y marcando UNKNOWN en
lugar de inventar.
"""

import json
import os

import pytest

from app.nar.contracts import NAR_DELEGATES
from app.nar.engine import NarrativeIntelligenceEngine
from app.nar.inputs import NarrativeInputs
from app.nar.persistence import write_blueprint
from app.nar.selection import StructureSelector
from app.nar.strategies.reverse_chronology import ReverseChronologyStructure
from app.nar.vocabulary import (
    Emotion,
    NarrationMode,
    QuestionType,
    StructureType,
    TensionLevel,
    TimelineOrder,
    UNKNOWN,
)


# --- helpers -----------------------------------------------------------------

def _coverage(**states):
    """states: dimension -> (required, discovered, state, [ids])."""
    dims = []
    for name, (req, disc, st, ids) in states.items():
        dims.append({"name": name, "required": req, "discovered": disc, "state": st,
                     "evidence_ids": ids})
    return {"dimensions": dims}


def _ctx(genre="true_crime", **over):
    profile = {"case_id": over.get("case_id", "case"), "title": "Caso", "genre": genre,
               "subject": over.get("subject", "Sujeto"),
               "people": over.get("people", ["Ana", "Juan"]),
               "locations": over.get("locations", ["Almassora"]),
               "events": over.get("events", ["arrest", "trial"])}
    coverage = over.get("coverage", _coverage(
        news=(3, 10, "COMPLETE", ["a", "b"]),
        maps=(2, 4, "COMPLETE", ["m"]),
        chronology=(1, 5, "COMPLETE", ["c"]),
        videos=(0, 25, "COMPLETE", ["v"]),
        photographs=(5, 0, "MISSING", []),
        documents=(2, 0, "MISSING", [])))
    return NarrativeInputs.from_sources(
        profile,
        coverage=coverage,
        conflicts=over.get("conflicts", {"conflicts": [{"basis": "dates", "relation": "CONTRADICTS"}]}),
        recreation_candidates=over.get("recreation_candidates",
                                       {"recreation_candidates": [
                                           {"factual_basis": {"category": "COURT_DOCUMENT"},
                                            "existing_coverage": "MISSING"}]}),
        generation_knowledge=over.get("generation_knowledge", {"sections": {
            "storytelling": [{"key": "pacing", "value": "moderate", "confidence": 0.49}],
            "narration": [{"key": "type", "value": "UNKNOWN", "confidence": 0.0}],
            "music": [{"key": "energy", "value": "UNKNOWN", "confidence": 0.0}]}}))


def _design(**over):
    return NarrativeIntelligenceEngine().design(_ctx(**over))


# --- estructura del blueprint ------------------------------------------------

def test_blueprint_is_complete():
    bp = _design()
    assert bp.structure in StructureType.ALL
    assert bp.segments and bp.arc and bp.emotion_curve and bp.timeline_decision
    assert len(bp.directives) == len(bp.segments)
    assert bp.totals["segments"] == len(bp.segments)
    # cada segmento tiene su contrato para VIS
    assert all(s.directive is not None for s in bp.segments)


def test_no_text_only_symbols():
    """El NAR no escribe texto: emociones/tensiones/preguntas son símbolos del vocabulario."""
    bp = _design()
    for s in bp.segments:
        assert s.emotion in Emotion.ALL
        assert s.tension in TensionLevel.ALL
    for q in bp.viewer_questions:
        assert q.type in QuestionType.ALL


# --- selección de estructura (auto-puntuada, trazable) -----------------------

def test_true_crime_selects_mystery():
    bp = _design(genre="true_crime")
    assert bp.structure == StructureType.MYSTERY_INVESTIGATION


def test_biography_selects_hero_journey():
    bp = _design(genre="biography")
    assert bp.structure == StructureType.HERO_JOURNEY


def test_selection_is_traceable_and_ranked():
    bp = _design()
    scores = [c.score for c in bp.candidates]
    assert scores == sorted(scores, reverse=True)         # ranking descendente
    assert bp.candidates[0].selected and bp.candidates[0].reasons
    assert sum(1 for c in bp.candidates if c.selected) == 1


def test_selector_deterministic_tie_break():
    ctx = _ctx()
    a = [c.structure for c in StructureSelector().rank(ctx)]
    b = [c.structure for c in StructureSelector().rank(ctx)]
    assert a == b


# --- colocación de evidencia: real > recreación > pregunta -------------------

def test_real_evidence_is_placed():
    bp = _design()
    placed = {e.dimension for s in bp.segments for e in s.evidence}
    assert "news" in placed and "maps" in placed     # dimensiones COMPLETE aparecen
    for s in bp.segments:
        for e in s.evidence:
            assert e.coverage_state in ("COMPLETE", "PARTIAL") and e.available > 0


def test_recreation_only_where_real_missing():
    bp = _design()
    # hay recreaciones (documents MISSING + candidato COURT_DOCUMENT)
    recs = [r for s in bp.segments for r in s.recreations]
    assert recs and all(r.justified_by == "missing_real_evidence" for r in recs)
    # nunca se recrea una dimensión que tiene evidencia real
    placed = {e.dimension for s in bp.segments for e in s.evidence}
    assert "news" in placed   # news real
    # COURT_DOCUMENT recreación porque documents está MISSING
    assert any(r.category == "COURT_DOCUMENT" for r in recs)


def test_gap_without_candidate_becomes_question_not_invention():
    # photographs MISSING y SIN candidato de recreación → pregunta abierta, nunca se inventa
    bp = _design(recreation_candidates={"recreation_candidates": []},
                 coverage=_coverage(news=(3, 10, "COMPLETE", ["a"]),
                                    photographs=(5, 0, "MISSING", [])))
    origins = {q.origin for q in bp.viewer_questions}
    assert any(o.startswith("missing_coverage:") for o in origins)
    # y no hay recreaciones inventadas sin candidato
    assert sum(len(s.recreations) for s in bp.segments) == 0


# --- curva emocional ---------------------------------------------------------

def test_emotion_curve_peaks_and_intensity():
    bp = _design()
    pts = bp.emotion_curve.points
    assert len(pts) == len(bp.segments)
    peak = max(pts, key=lambda p: TensionLevel.RANK[p.tension])
    assert bp.emotion_curve.peak_index == peak.index
    for p in pts:
        assert abs(p.intensity - TensionLevel.RANK[p.tension] / 4.0) < 1e-6


def test_genre_floor_colors_neutral():
    bp = _design(genre="true_crime")
    # en true_crime ningún segmento queda NEUTRAL (suelo emocional UNEASE)
    assert all(s.emotion != Emotion.NEUTRAL for s in bp.segments)


def test_silence_is_a_decision():
    bp = _design()
    # el NAR decide DÓNDE callar (revelación / pregunta abierta)
    assert any(s.narration.mode == NarrationMode.SILENCE for s in bp.segments)


# --- mecanismos: foreshadow→reveal→payoff, cliffhangers ----------------------

def test_reveals_and_foreshadow_order():
    bp = _design()
    assert bp.reveals
    fmap = {f.id: f for f in bp.foreshadows}
    for r in bp.reveals:
        if r.foreshadowed_by:
            f = fmap[r.foreshadowed_by]
            assert f.segment_index < r.segment_index      # se siembra antes de revelar
            assert f.pays_off_in == r.segment_index
    for p in bp.payoffs:
        rev = next((r for r in bp.reveals if r.id == p.resolves), None)
        assert rev is not None and p.segment_index > rev.segment_index


def test_narrative_state_progression():
    bp = _design()
    revealed = [s.revealed for s in bp.narrative_states]
    pending = [s.pending_reveals for s in bp.narrative_states]
    assert revealed == sorted(revealed)                   # monótono no decreciente
    assert pending == sorted(pending, reverse=True)       # las revelaciones pendientes bajan
    assert pending[-1] == 0                               # al final no queda nada por revelar


# --- frontera de responsabilidades (no decide lo de VIS/VAI/Composer) --------

def test_directives_delegate_visual_decisions():
    bp = _design()
    for d in bp.directives:
        assert "shot_size" in d.delegated_to and d.delegated_to["shot_size"] == "VIS"
        assert d.delegated_to["camera_movement"] == "VAI"
        assert d.delegated_to["cut_type"] == "Composer"
        # el directive expresa intención, no ejecución visual
        assert d.pacing_intent and d.purpose and d.emotion


# --- orden temporal ----------------------------------------------------------

def test_reverse_chronology_order():
    strat = ReverseChronologyStructure()
    assert strat.timeline_order() == TimelineOrder.REVERSE


def test_default_timeline_is_chronological():
    bp = _design()  # mystery → cronológico
    assert bp.timeline_decision.order == TimelineOrder.CHRONOLOGICAL


# --- procedencia: UNKNOWN sobre inventar -------------------------------------

def test_provenance_flags_unknown_inputs():
    bp = _design()
    # narration y music son UNKNOWN en el corpus → se declaran, no se inventan
    assert "kbg:narration" in bp.provenance.unknown_inputs
    assert "kbg:music" in bp.provenance.unknown_inputs
    assert "kbg:storytelling.pacing" in bp.provenance.knowledge_used


# --- determinismo ------------------------------------------------------------

def test_engine_is_deterministic():
    a = json.dumps(_design().to_dict(), sort_keys=True)
    b = json.dumps(_design().to_dict(), sort_keys=True)
    assert a == b


# --- persistencia (output/narrative, nunca knowledge/) -----------------------

def test_persistence_writes_outside_knowledge(tmp_path):
    bp = _design()
    out = str(tmp_path / "output" / "narrative")
    paths = write_blueprint(bp, out_dir=out)
    assert os.path.exists(paths["blueprint"]) and paths["blueprint"].endswith("blueprint.json")
    data = json.loads(open(paths["blueprint"], encoding="utf-8").read())
    assert data["case_id"] == bp.case_id and data["segments"]


def test_persistence_refuses_knowledge():
    bp = _design()
    with pytest.raises(ValueError):
        write_blueprint(bp, out_dir=os.path.join("knowledge", "narrative"))


# --- sin red / sin azar / sin IA ---------------------------------------------

def test_no_network_random_or_ai_imports():
    import importlib
    import pkgutil

    import app.nar as pkg
    forbidden = ("requests", "bs4", "selenium", "playwright", "httpx", "random",
                 "openai", "anthropic", "datetime")
    for mod in pkgutil.walk_packages(pkg.__path__, prefix="app.nar."):
        source = importlib.import_module(mod.name)
        for name in forbidden:
            assert name not in getattr(source, "__dict__", {}), f"{mod.name} importa {name}"
