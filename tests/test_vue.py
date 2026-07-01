"""Tests del Visual Understanding Engine (VUE-001) — foundation, deterministas."""

import json
import os

import pytest

from app.vue import (
    NOT_IMPLEMENTED,
    UNKNOWN,
    FrameRef,
    VisualAnalysis,
    VisualUnderstandingEngine,
    default_detectors,
)
from app.vue.detectors import ShotSizeDetector, TextDetector
from app.vue.models import CAPABILITIES, DetectedText, VisualObservation
from app.vue.persistence import VisualAnalysisWriter, from_payload, to_payload


def _frame(i=0):
    return FrameRef(path=f"/tmp/f{i}.png", index=i, timestamp=float(i), frame_id=f"f{i}")


# --- detectores: solo hechos, UNKNOWN antes que inventar ---------------------

def test_detector_returns_unknown_fact_without_invented_score():
    obs = ShotSizeDetector().detect(_frame())
    assert obs.capability == "shot_size" and obs.value == UNKNOWN
    assert obs.confidence is None              # jamás se inventa una puntuación
    assert obs.method == NOT_IMPLEMENTED
    assert obs.is_unknown()


def test_text_detector_typed_facts():
    obs = TextDetector().detect(_frame())
    assert obs.capability == "text"
    assert obs.facts["present"] == UNKNOWN     # payload tipado UNKNOWN


def test_one_detector_one_capability():
    caps = [getattr(d, "capability") for d in default_detectors()]
    assert len(caps) == len(set(caps))         # sin solapes
    assert set(caps) == set(CAPABILITIES)


# --- orquestador: solo coordina, determinista, no rompe ----------------------

def test_orchestrator_runs_all_detectors():
    analysis = VisualUnderstandingEngine().analyze(_frame(3))
    assert isinstance(analysis, VisualAnalysis)
    assert len(analysis.observations) == len(CAPABILITIES)
    assert analysis.frame_index == 3 and analysis.frame_id == "f3"
    assert all(o.is_unknown() for o in analysis.observations)


def test_orchestrator_is_deterministic():
    a = VisualUnderstandingEngine().analyze(_frame()).to_dict()
    b = VisualUnderstandingEngine().analyze(_frame()).to_dict()
    assert a == b


def test_failing_detector_does_not_break_analysis():
    class _Boom:
        capability = "boom"

        def detect(self, frame, context=None):
            raise RuntimeError("explode")

    eng = VisualUnderstandingEngine(detectors=[ShotSizeDetector(), _Boom()])
    analysis = eng.analyze(_frame())
    assert len(analysis.observations) == 2        # la del fallo cae a UNKNOWN
    assert any(e["detector"] == "boom" for e in analysis.errors)
    boom_obs = analysis.by_capability("boom")
    assert boom_obs is not None and boom_obs.is_unknown()


def test_register_new_detector():
    eng = VisualUnderstandingEngine(detectors=[ShotSizeDetector()])
    eng.register(TextDetector())
    caps = [o.capability for o in eng.analyze(_frame()).observations]
    assert caps == ["shot_size", "text"]          # orden preservado


# --- serialización + contrato de persistencia (nunca knowledge/) -------------

def test_analysis_serialization_roundtrip():
    analysis = VisualUnderstandingEngine().analyze(_frame(5))
    restored = VisualAnalysis.from_dict(analysis.to_dict())
    assert restored.to_dict() == analysis.to_dict()


def test_payload_roundtrip():
    analyses = VisualUnderstandingEngine().analyze_many([_frame(0), _frame(1)])
    payload = to_payload(analyses, source="demo")
    assert payload["schema_version"] and len(payload["frames"]) == 2
    assert [a.to_dict() for a in from_payload(payload)] == [a.to_dict() for a in analyses]


def test_writer_refuses_knowledge_dir():
    with pytest.raises(ValueError):
        VisualAnalysisWriter(out_dir=os.path.join("knowledge", "vue"))


def test_writer_writes_to_output(tmp_path):
    analyses = VisualUnderstandingEngine().analyze_many([_frame(0)])
    out = str(tmp_path / "out" / "vue")
    path = VisualAnalysisWriter(out_dir=out).write(analyses, source="demo")
    assert os.path.exists(path)
    data = json.loads(open(path, encoding="utf-8").read())
    assert data["source"] == "demo" and len(data["frames"]) == 1


# --- provider-agnóstico / sin dependencias de visión ni azar -----------------

def test_no_cv_or_random_imports():
    import importlib
    import pkgutil

    import app.vue as pkg
    forbidden = ("random", "cv2", "torch", "ultralytics", "numpy")
    for mod in pkgutil.iter_modules(pkg.__path__):
        source = importlib.import_module(f"app.vue.{mod.name}")
        for name in forbidden:
            assert name not in getattr(source, "__dict__", {})


def test_observation_defaults_are_unknown():
    obs = VisualObservation(detector="X", capability="y")
    assert obs.value == UNKNOWN and obs.confidence is None
    assert DetectedText().present == UNKNOWN
