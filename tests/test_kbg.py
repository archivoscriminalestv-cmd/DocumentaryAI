"""Tests del Knowledge Bridge (KBG-001) — deterministas, solo lectura, sin red ni IA.

Usan una FIXTURE de estilos en disco (no la knowledge/styles real, que cambia mientras el
DLE aprende). Cubren loader, resolver, decision engine, bridge, evidencia (ECE), UNKNOWN,
determinismo y persistencia.
"""

import json
import os

from app.kbg.bridge import KnowledgeBridge
from app.kbg.knowledge_loader import load_styles
from app.kbg.persistence import write_outputs
from app.kbg.style_resolver import StyleResolver


def _dist(fractions, total):
    counts = {k: int(round(v * total)) for k, v in fractions.items()}
    return {"counts": counts, "fractions": fractions, "total": total}


def _summ(count, mean, median):
    return {"count": count, "mean": mean, "median": median, "min": 0.2, "max": 60.0,
            "stdev": 8.0}


def _fixture(tmp_path) -> str:
    root = tmp_path / "styles"
    os.makedirs(root)
    files = {
        "cinematography_patterns": {
            "shot_size": _dist({"UNKNOWN": 1.0}, 100),          # sin señal -> UNKNOWN
            "composition": _dist({"UNKNOWN": 1.0}, 100),
            "close_up_frequency": _summ(98, 0.0, 0.0)},
        "editing_patterns": {
            "pacing_tier": _dist({"fast": 0.03, "moderate": 0.48, "slow": 0.49}, 100),
            "shot_length": _summ(1000, 6.0, 3.0),               # median/mean = 0.5
            "cuts_per_minute": _summ(100, 12.0, 11.0)},
        "lighting_patterns": {
            "color_temperature": _dist({"UNKNOWN": 0.01, "cool": 0.10, "neutral": 0.40,
                                        "warm": 0.49}, 100),
            "lighting": _dist({"balanced": 0.6, "low-key": 0.3, "high-key": 0.1}, 100),
            "contrast": _summ(100, 0.42, 0.40), "brightness": _summ(100, 0.50, 0.50)},
        "motion_patterns": {"movement": _dist({"static": 0.7, "pan": 0.3}, 100)},
        "true_crime": {"distributions": {"shot_size": _dist({"wide": 0.6, "close": 0.4}, 50)}},
    }
    for name, data in files.items():
        with open(root / f"{name}.json", "w", encoding="utf-8") as h:
            json.dump(data, h)
    return str(root)


# --- loader / resolver -------------------------------------------------------
def test_loader_reads_styles(tmp_path):
    bundle = load_styles(_fixture(tmp_path))
    assert bundle.style("editing_patterns") is not None
    assert bundle.source("editing_patterns").endswith("editing_patterns.json")


def test_resolver_collects_areas_and_genre(tmp_path):
    bundle = load_styles(_fixture(tmp_path))
    r = StyleResolver().resolve(bundle, "true_crime")
    assert "editing" in r.profiles and "lighting" in r.profiles
    assert r.genre_profile is not None
    dist, src = r.dist("editing", "pacing_tier")
    assert dist["fractions"]["slow"] == 0.49


def test_resolver_genre_fallback(tmp_path):
    # solo true_crime con distributions.shot_size; sin cinematography_patterns
    root = tmp_path / "styles"
    os.makedirs(root)
    with open(root / "true_crime.json", "w", encoding="utf-8") as h:
        json.dump({"distributions": {"shot_size": _dist({"wide": 0.6, "close": 0.4}, 50)}}, h)
    r = StyleResolver().resolve(load_styles(str(root)), "true_crime")
    dist, src = r.dist("cinematography", "shot_size", "shot_size")
    assert dist["fractions"]["wide"] == 0.6      # cae al perfil de género


# --- decisiones --------------------------------------------------------------
def _gk(tmp_path, genre="true_crime", ece=""):
    return KnowledgeBridge(styles_root=_fixture(tmp_path)).build(genre=genre, ece_coverage_path=ece)


def _find(gk, section, key):
    return next(d for d in gk.sections[section] if d.key == key)


def test_distribution_decisions(tmp_path):
    gk = _gk(tmp_path)
    assert _find(gk, "storytelling", "pacing").value == "slow"
    assert _find(gk, "cinematography", "color_temperature").value == "warm"
    assert _find(gk, "cinematography", "dominant_movement").value == "static"
    ct = _find(gk, "cinematography", "color_temperature")
    assert ct.confidence == 0.49 and "DKS:lighting_patterns" in ct.origin


def test_unknown_before_invent(tmp_path):
    gk = _gk(tmp_path)
    shot = _find(gk, "cinematography", "dominant_shot_size")
    assert shot.value == "UNKNOWN" and shot.confidence == 0.0   # corpus es todo UNKNOWN
    assert _find(gk, "cinematography", "secondary_shot_sizes").value == "UNKNOWN"
    assert _find(gk, "narration", "style").value == "UNKNOWN"


def test_numeric_decision_confidence_from_data(tmp_path):
    d = _find(_gk(tmp_path), "storytelling", "average_shot_duration")
    assert d.value == 3.0 and d.confidence == 0.5              # median/mean = 3/6


def test_each_decision_is_traceable(tmp_path):
    for d in _gk(tmp_path).all_decisions():
        assert d.key and isinstance(d.confidence, float)
        if d.known:
            assert d.origin != "UNKNOWN" and d.reason and d.knowledge_sources


# --- evidencias desde el ECE -------------------------------------------------
def test_evidence_from_ece_coverage(tmp_path):
    coverage = {"dimensions": [
        {"name": "photographs", "discovered": 6}, {"name": "videos", "discovered": 2},
        {"name": "documents", "discovered": 0}, {"name": "maps", "discovered": 2},
        {"name": "news", "discovered": 0}]}
    cov_path = tmp_path / "coverage_report.json"
    with open(cov_path, "w", encoding="utf-8") as h:
        json.dump(coverage, h)
    gk = _gk(tmp_path, ece=str(cov_path))
    photos = _find(gk, "evidence", "photographs")
    assert photos.value == 0.6 and photos.origin == "ECE:coverage_report"   # 6/10


def test_evidence_unknown_without_ece(tmp_path):
    assert _find(_gk(tmp_path), "evidence", "photographs").value == "UNKNOWN"


# --- determinismo / persistencia ---------------------------------------------
def test_bridge_is_deterministic(tmp_path):
    root = _fixture(tmp_path)
    a = KnowledgeBridge(styles_root=root).build(genre="true_crime")
    b = KnowledgeBridge(styles_root=root).build(genre="true_crime")
    assert a.to_dict() == b.to_dict()


def test_summary_counts_known(tmp_path):
    gk = _gk(tmp_path)
    s = gk.summary
    assert s["total_decisions"] == len(gk.all_decisions())
    assert 0 < s["known"] < s["total_decisions"]      # algunas conocidas, otras UNKNOWN


def test_persistence_writes_outputs(tmp_path):
    gk = _gk(tmp_path)
    paths = write_outputs(str(tmp_path / "out"), gk)
    assert os.path.exists(paths["generation_knowledge"]) and os.path.exists(paths["report"])
    data = json.load(open(paths["generation_knowledge"], encoding="utf-8"))
    assert data["genre"] == "true_crime" and "storytelling" in data["sections"]
