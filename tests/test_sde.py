"""Tests del Shot Diversity Engine (SDE) — deterministas, sin red, sin aleatoriedad."""

from app.sde import SDEContext, ShotDiversityEngine, ShotHistory
from app.sde.continuity import IMMUTABLE_DIMENSIONS, identity_preserved
from app.sde.models import VARIABLE_DIMENSIONS, ShotFingerprint
from app.sde.rules import classify_narrative, parse_base_fingerprint, render_to_spec
from app.sde.scoring import diversity_against, similarity
from app.vai.models import ShotExecutionRequest, VisualSpecification


def _req(shot_id="s1", scene="scene-01", lens="35mm lens", angle="eye-level",
         lead="wide cinematic shot", comp="layered foreground and background"):
    spec = VisualSpecification(
        shot_id=shot_id, scene_id=scene, media_type="image", subject="Coquito", style="documentary",
        composition=[comp, "clear foreground-background separation"],
        camera_language=[lead, "parallax depth motion"],
        negatives=["toy-like"],
    )
    return ShotExecutionRequest(
        shot_id=shot_id, scene_id=scene, media_type="image", prompt="", negative_prompt="",
        lens=lens, angle=angle, composition=comp, specification=spec, motion={"move": "static"},
    )


def _ctx(scene="scene-01", style="observational documentary", role=""):
    return SDEContext(scene_id=scene, documentary_style=style, location="Almassora",
                      color_palette="muted cold tones", time_of_day="morning", weather="overcast",
                      lighting="soft overcast", character_name="Coquito", identity="vid_x",
                      shot_role=role)


# --- determinismo / sin aleatoriedad -----------------------------------------

def test_engine_is_deterministic():
    def run():
        eng = ShotDiversityEngine()
        for i in range(8):
            eng.process(_req(shot_id=f"s{i}"), _ctx())
        return [r.fingerprint.variable_tuple() for r in eng.history.all()]
    assert run() == run()


def test_no_random_import_in_package():
    import importlib
    import pkgutil

    import app.sde as pkg
    for mod in pkgutil.iter_modules(pkg.__path__):
        source = importlib.import_module(f"app.sde.{mod.name}")
        assert "random" not in getattr(source, "__dict__", {})  # no se importó random


# --- reduce composiciones repetidas ------------------------------------------

def test_reduces_repeated_compositions():
    eng = ShotDiversityEngine()
    finals = [eng.process(_req(shot_id=f"s{i}"), _ctx()).specification for i in range(6)]
    fps = [r.fingerprint for r in eng.history.all()]
    # 6 planos base idénticos -> el SDE los diversifica (no todos iguales).
    assert len({fp.variable_tuple() for fp in fps}) >= 4
    # y los camera_language ya no son todos idénticos
    assert len({tuple(s.camera_language) for s in finals}) >= 4


def test_diversity_increases_vs_identical_base():
    eng = ShotDiversityEngine()
    base = parse_base_fingerprint(_req(), _ctx())
    for i in range(6):
        eng.process(_req(shot_id=f"s{i}"), _ctx())
    fps = [r.fingerprint for r in eng.history.all()]
    # diversidad media alta pese a que el VAI entregaba siempre el mismo plano
    assert eng.average_diversity() > 0.5
    assert diversity_against(base, fps[1:]) >= 0.0


# --- nunca rompe identidad ni continuidad de escena --------------------------

def test_identity_and_scene_never_change():
    eng = ShotDiversityEngine()
    for i in range(10):
        eng.process(_req(shot_id=f"s{i}"), _ctx())
    for r in eng.history.all():
        assert identity_preserved(r.base_fingerprint, r.fingerprint)
        for d in IMMUTABLE_DIMENSIONS:
            assert getattr(r.fingerprint, d) == getattr(r.base_fingerprint, d)


def test_interview_mode_keeps_continuity():
    eng = ShotDiversityEngine()
    for i in range(6):
        eng.process(_req(shot_id=f"s{i}"), _ctx(style="interview"))
    fps = [r.fingerprint for r in eng.history.all()]
    # en entrevista NO cambian tamaño ni lente (continuidad); pueden variar composición/posición
    assert len({fp.shot_size for fp in fps}) == 1
    assert len({fp.lens for fp in fps}) == 1


def test_broll_mode_allows_more_diversity():
    eng = ShotDiversityEngine()
    for i in range(6):
        eng.process(_req(shot_id=f"s{i}"), _ctx(role="cutaway"))
    fps = [r.fingerprint for r in eng.history.all()]
    # plano recurso: máxima libertad -> varían tamaño y lente
    assert len({fp.shot_size for fp in fps}) > 1
    assert len({fp.lens for fp in fps}) > 1


# --- no modifica identidad/subject ni el contrato del request ----------------

def test_subject_and_negatives_untouched():
    eng = ShotDiversityEngine()
    out = eng.process(_req(), _ctx())
    assert out.specification.subject == "Coquito"
    assert out.specification.negatives == ["toy-like"]
    assert out.shot_id == "s1" and out.scene_id == "scene-01"


def test_only_structured_fields_modified():
    eng = ShotDiversityEngine()
    base = _req()
    out = eng.process(base, _ctx())
    # devuelve un objeto nuevo (no muta el original)
    assert base.specification.camera_language == ["wide cinematic shot", "parallax depth motion"]
    assert out is not base


# --- narrativa / parseo / scoring --------------------------------------------

def test_classify_narrative():
    assert classify_narrative("intimate documentary") == "intimate"
    assert classify_narrative("observational documentary") == "observational"
    assert classify_narrative("anything", "cutaway") == "broll"
    assert classify_narrative("interview with subject") == "interview"


def test_render_to_spec_shapes():
    fp = ShotFingerprint(shot_size="close", camera_angle="low", lens=85, composition="symmetry",
                         subject_position="left", gaze="camera", movement="push_in")
    cam, comp = render_to_spec(fp)
    assert cam[0] == "close-up" and "85mm lens" in cam
    assert comp[0] == "symmetrical composition" and comp[1] == "subject framed left"


def test_similarity_bounds():
    a = ShotFingerprint()
    b = ShotFingerprint()
    assert similarity(a, b) == 1.0                      # idénticos
    c = ShotFingerprint(shot_size="extreme wide", camera_angle="dutch", lens=135,
                        composition="silhouette", subject_position="right", gaze="up",
                        camera_height="drone", movement="orbit")
    assert similarity(a, c) == 0.0                      # todo distinto


# --- persistencia ------------------------------------------------------------

def test_history_roundtrip():
    eng = ShotDiversityEngine()
    for i in range(5):
        eng.process(_req(shot_id=f"s{i}"), _ctx())
    restored = ShotHistory.from_dict(eng.history.to_dict())
    assert len(restored) == 5
    assert [r.fingerprint.variable_tuple() for r in restored.all()] == \
           [r.fingerprint.variable_tuple() for r in eng.history.all()]


# --- pipeline intacto (build_requests sigue dando 26) ------------------------

def test_build_requests_with_and_without_sde():
    from app.cli.compile_coquito import build_requests
    plain = build_requests()
    sde = ShotDiversityEngine()
    enriched = build_requests(sde=sde, character_name="Coquito", identity="vid_x")
    assert len(plain) == len(enriched) == 26
    # el SDE cambia los prompts (más variedad) pero mantiene el nº de planos
    assert sum(1 for p, e in zip(plain, enriched) if p.prompt != e.prompt) > 0
