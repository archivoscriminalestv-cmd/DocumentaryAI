"""Tests de los detectores de disposición/localización del VUE (VUE-003) — deterministas."""

from PIL import Image, ImageDraw

from app.vue import UNKNOWN, FrameRef, VisualUnderstandingEngine
from app.vue.layout_detectors import (
    EmptySpaceDetector,
    LayoutBalanceDetector,
    SubjectLocalizationDetector,
    VisualWeightDetector,
    layout_detectors,
)


def _save(img, tmp_path, name) -> FrameRef:
    p = tmp_path / name
    img.save(p)
    return FrameRef(path=str(p), index=0, frame_id=name)


def _subject_image(size=(256, 144), box=(96, 48, 160, 104)):
    """Fondo plano oscuro con un recuadro detallado (sujeto) en el centro."""
    img = Image.new("RGB", size, (15, 15, 15))
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=(200, 200, 200))
    for x in range(box[0], box[2], 4):           # textura -> bordes salientes
        d.line([(x, box[1]), (x, box[3])], fill=(40, 40, 40))
    return img


# --- SubjectLocalization -----------------------------------------------------

def test_subject_localization_centered(tmp_path):
    obs = SubjectLocalizationDetector().detect(_save(_subject_image(), tmp_path, "s.png"))
    f = obs.facts
    assert obs.value == UNKNOWN and obs.confidence is None   # localiza, no clasifica
    assert f["bbox"] is not None and f["occupancy"] > 0.0
    assert 0.3 < f["center"]["x"] < 0.7 and 0.3 < f["center"]["y"] < 0.7
    assert f["position"] == "middle-center"
    assert set(f["distances"]) == {"left", "right", "top", "bottom"}


def test_subject_localization_unknown_on_flat(tmp_path):
    flat = Image.new("RGB", (256, 144), (120, 120, 120))
    obs = SubjectLocalizationDetector().detect(_save(flat, tmp_path, "flat.png"))
    assert obs.is_unknown()                       # nada destaca -> UNKNOWN (no inventa)


def test_subject_localization_left_position(tmp_path):
    img = _subject_image(box=(10, 50, 70, 100))
    obs = SubjectLocalizationDetector().detect(_save(img, tmp_path, "l.png"))
    assert obs.facts["center"]["x"] < 1 / 3       # sujeto a la izquierda
    assert obs.facts["position"].endswith("left")


# --- LayoutBalance -----------------------------------------------------------

def test_layout_balance_symmetry(tmp_path):
    sym = Image.new("RGB", (256, 144), (0, 0, 0))
    d = ImageDraw.Draw(sym)
    d.rectangle([108, 0, 148, 144], fill=(220, 220, 220))   # banda central → simétrico
    obs = LayoutBalanceDetector().detect(_save(sym, tmp_path, "sym.png"))
    f = obs.facts
    assert f["horizontal_symmetry"] > 0.9          # casi perfecto
    assert abs(f["horizontal"]["left"] - f["horizontal"]["right"]) < 0.05
    assert 0.0 <= f["dispersion"] <= 1.0 and 0.0 <= f["concentration"] <= 1.0


# --- VisualWeight ------------------------------------------------------------

def test_visual_weight_left_heavy(tmp_path):
    img = Image.new("RGB", (256, 144), (0, 0, 0))
    ImageDraw.Draw(img).rectangle([0, 0, 100, 144], fill=(230, 230, 230))  # masa izquierda
    obs = VisualWeightDetector().detect(_save(img, tmp_path, "w.png"))
    f = obs.facts
    assert f["left"] > f["right"] and f["center_of_gravity"]["x"] < 0.5


# --- EmptySpace --------------------------------------------------------------

def test_empty_space_mostly_empty(tmp_path):
    img = _subject_image()                          # fondo plano grande + sujeto pequeño
    obs = EmptySpaceDetector().detect(_save(img, tmp_path, "e.png"))
    f = obs.facts
    assert f["empty_fraction"] > 0.5                # mayoría plano
    assert f["largest_empty_bbox"] is not None
    assert 0.0 <= f["largest_empty_fraction"] <= 1.0


def test_empty_space_full_detail_low_empty(tmp_path):
    busy = Image.new("RGB", (256, 144), (0, 0, 0))
    d = ImageDraw.Draw(busy)
    for x in range(0, 256, 6):
        d.line([(x, 0), (x, 144)], fill=(255, 255, 255))   # textura por todo el frame
    obs = EmptySpaceDetector().detect(_save(busy, tmp_path, "busy.png"))
    assert obs.facts["empty_fraction"] < 0.5


# --- nunca lanzar / determinismo / registro ----------------------------------

def test_layout_missing_frame_unknown_never_raises():
    missing = FrameRef(path="/no/such/frame.png")
    for det in layout_detectors():
        assert det.detect(missing).is_unknown()


def test_layout_detectors_deterministic(tmp_path):
    ref = _save(_subject_image(), tmp_path, "d.png")
    for det in layout_detectors():
        assert det.detect(ref).to_dict() == det.detect(ref).to_dict()


def test_engine_registers_layout_capabilities(tmp_path):
    caps = {d.capability for d in VisualUnderstandingEngine().detectors}
    assert {"subject_localization", "layout_balance", "visual_weight", "empty_space"} <= caps
    analysis = VisualUnderstandingEngine().analyze(_save(_subject_image(), tmp_path, "f.png"))
    sub = analysis.by_capability("subject_localization")
    assert sub is not None and sub.method == "classical_cv" and sub.facts["bbox"] is not None
