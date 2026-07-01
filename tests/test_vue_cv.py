"""Tests de los detectores de visión clásica del VUE (VUE-002) — deterministas."""

import os

from PIL import Image, ImageDraw

from app.vue import UNKNOWN, FrameRef, VisualUnderstandingEngine
from app.vue.cv_detectors import (
    ColorAnalysisDetector,
    CompositionDetector,
    EdgeDensityDetector,
    FrameGeometryDetector,
    MotionEnergyDetector,
)


def _save(img, tmp_path, name) -> FrameRef:
    p = tmp_path / name
    img.save(p)
    return FrameRef(path=str(p), index=0, frame_id=name)


def _solid(color, size=(256, 144)):
    return Image.new("RGB", size, color)


# --- Composition (solo geometría) --------------------------------------------

def test_composition_measures_balance(tmp_path):
    img = Image.new("RGB", (256, 144), (0, 0, 0))
    ImageDraw.Draw(img).rectangle([128, 0, 256, 144], fill=(160, 160, 160))  # masa a la derecha
    obs = CompositionDetector().detect(_save(img, tmp_path, "c.png"))
    f = obs.facts
    assert obs.value == UNKNOWN                    # nunca interpreta intención
    assert obs.confidence is None
    assert f["center_x"] > 0.5                      # centro de masa a la derecha
    assert f["left_right_balance"] < 0.5            # menos masa a la izquierda
    assert 0.0 <= f["negative_space"] <= 1.0


# --- Color -------------------------------------------------------------------

def test_color_dominant_and_temperature(tmp_path):
    obs = ColorAnalysisDetector().detect(_save(_solid((220, 40, 40)), tmp_path, "r.png"))
    f = obs.facts
    assert obs.value == "red" and f["dominant_color"] == "red"
    assert f["temperature"] == "warm"
    assert f["saturation"] > 0.5
    assert len(f["rgb_histogram"]["R"]) == 8


def test_color_cool_image(tmp_path):
    obs = ColorAnalysisDetector().detect(_save(_solid((40, 60, 210)), tmp_path, "b.png"))
    assert obs.facts["temperature"] == "cool"


# --- Edge density ------------------------------------------------------------

def test_edge_density_solid_vs_stripes(tmp_path):
    solid = EdgeDensityDetector().detect(_save(_solid((120, 120, 120)), tmp_path, "s.png"))
    stripes_img = Image.new("RGB", (256, 144), (0, 0, 0))
    d = ImageDraw.Draw(stripes_img)
    for x in range(0, 256, 8):
        d.rectangle([x, 0, x + 3, 144], fill=(255, 255, 255))
    stripes = EdgeDensityDetector().detect(_save(stripes_img, tmp_path, "st.png"))
    assert solid.facts["edge_density"] < 0.05
    assert stripes.facts["edge_density"] > solid.facts["edge_density"]
    assert len(stripes.facts["detail_grid"]) == 3


# --- Motion energy (dos frames) ----------------------------------------------

def test_motion_requires_previous_frame(tmp_path):
    cur = _save(_solid((100, 100, 100)), tmp_path, "cur.png")
    obs = MotionEnergyDetector().detect(cur)
    assert obs.is_unknown()                         # sin frame previo -> UNKNOWN


def test_motion_identical_vs_different(tmp_path):
    a = _save(_solid((10, 10, 10)), tmp_path, "a.png")
    same = MotionEnergyDetector().detect(a, {"previous_frame": a})
    assert same.facts["changed_pixel_pct"] == 0.0 and same.facts["intensity"] == 0.0
    b = _save(_solid((200, 200, 200)), tmp_path, "b.png")
    moved = MotionEnergyDetector().detect(b, {"previous_path": a.path})
    assert moved.facts["changed_pixel_pct"] > 0.9 and moved.facts["intensity"] > 0.5


# --- Frame geometry ----------------------------------------------------------

def test_geometry_orientation_and_aspect(tmp_path):
    land = FrameGeometryDetector().detect(_save(_solid((90, 90, 90), (320, 180)), tmp_path, "l.png"))
    assert land.value == "landscape" and land.facts["aspect_ratio"] == round(320 / 180, 4)
    port = FrameGeometryDetector().detect(_save(_solid((90, 90, 90), (180, 320)), tmp_path, "p.png"))
    assert port.value == "portrait"


def test_geometry_letterbox(tmp_path):
    img = Image.new("RGB", (256, 256), (0, 0, 0))
    ImageDraw.Draw(img).rectangle([0, 64, 256, 192], fill=(200, 200, 200))  # banda central
    obs = FrameGeometryDetector().detect(_save(img, tmp_path, "lb.png"))
    assert obs.facts["letterbox"] is True and obs.facts["pillarbox"] is False


# --- nunca lanzar / UNKNOWN; determinismo ------------------------------------

def test_missing_frame_is_unknown_never_raises():
    missing = FrameRef(path="/no/such/file.png")
    for det in (CompositionDetector(), ColorAnalysisDetector(), EdgeDensityDetector(),
                FrameGeometryDetector()):
        obs = det.detect(missing)
        assert obs.is_unknown()


def test_detectors_are_deterministic(tmp_path):
    ref = _save(_solid((130, 90, 60)), tmp_path, "d.png")
    for det in (CompositionDetector(), ColorAnalysisDetector(), EdgeDensityDetector(),
                FrameGeometryDetector()):
        assert det.detect(ref).to_dict() == det.detect(ref).to_dict()


# --- integración con el orquestador (real) -----------------------------------

def test_engine_runs_classical_detectors_on_real_frame(tmp_path):
    ref = _save(_solid((200, 50, 50)), tmp_path, "frame.png")
    analysis = VisualUnderstandingEngine().analyze(ref)
    caps = {o.capability: o for o in analysis.observations}
    assert caps["color"].value == "red"            # detector real produce un hecho
    assert caps["frame_geometry"].value == "landscape"
    assert caps["composition"].method == "classical_cv"   # midió geometría (value UNKNOWN)
    assert caps["edge_density"].method == "classical_cv"
    assert caps["shot_size"].method == "not_implemented"  # capacidad futura sigue UNKNOWN
    assert caps["motion_energy"].is_unknown()      # sin frame previo


def test_engine_motion_with_context(tmp_path):
    a = _save(_solid((20, 20, 20)), tmp_path, "m0.png")
    b = _save(_solid((220, 220, 220)), tmp_path, "m1.png")
    analysis = VisualUnderstandingEngine().analyze(b, {"previous_frame": a})
    motion = analysis.by_capability("motion_energy")
    # value sigue UNKNOWN (no clasificamos el tipo de movimiento); el hecho está medido.
    assert motion.method == "classical_cv" and motion.facts["intensity"] > 0.5
