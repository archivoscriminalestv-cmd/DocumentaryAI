"""Tests del Documentary Knowledge Synthesizer (DKS-001) — deterministas, sin vídeo."""

import json
import os

from app.dks.loader import load_corpus
from app.dks.persistence import write_styles
from app.dks.stats import distribution, histogram, mean, median, pearson, summarize
from app.dks.synthesizer import KnowledgeSynthesizer


# --- helpers para construir un corpus sintético en disco ---------------------
def _write_doc(root, doc_id, *, duration, stats, shots):
    d = os.path.join(root, "documentaries", doc_id)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "documentary.json"), "w", encoding="utf-8") as h:
        json.dump({"metadata": {"duration": duration}}, h)
    with open(os.path.join(d, "statistics.json"), "w", encoding="utf-8") as h:
        json.dump(stats, h)
    with open(os.path.join(d, "shots.json"), "w", encoding="utf-8") as h:
        json.dump(shots, h)


def _shot(duration, motion, brightness, contrast, size, movement, lighting):
    return {"duration": duration, "motion_magnitude": motion, "brightness": brightness,
            "contrast": contrast, "shot_size": size, "movement": movement,
            "lighting": lighting, "color_temperature": "NEUTRAL", "dominant_color": "GRAY",
            "composition": "CENTERED"}


def _corpus_dir(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_doc(root, "doc_a", duration=120.0,
               stats={"shot_count": 2, "scene_count": 1, "average_shot_length": 3.0,
                      "cuts_per_minute": 20.0, "close_up_frequency": 0.5, "pacing_tier": "FAST"},
               shots=[_shot(2.0, 0.1, 0.4, 0.2, "WIDE", "STATIC", "LOW_KEY"),
                      _shot(4.0, 0.5, 0.6, 0.3, "CLOSE", "PAN", "HIGH_KEY")])
    _write_doc(root, "doc_b", duration=60.0,
               stats={"shot_count": 1, "scene_count": 1, "average_shot_length": 6.0,
                      "cuts_per_minute": 10.0, "close_up_frequency": 0.0, "pacing_tier": "SLOW"},
               shots=[_shot(6.0, 0.9, 0.8, 0.4, "MEDIUM", "STATIC", "LOW_KEY")])
    return root


# --- stats puros -------------------------------------------------------------
def test_stats_helpers():
    assert mean([2, 4, 6]) == 4.0
    assert median([1, 2, 3, 4]) == 2.5
    assert pearson([1, 2, 3], [2, 4, 6]) == 1.0
    assert pearson([1, 2, 3], [3, 2, 1]) == -1.0
    assert pearson([1, 1, 1], [1, 2, 3]) is None          # sin varianza
    s = summarize([2.0, 4.0, 6.0])
    assert s["count"] == 3 and s["mean"] == 4.0 and s["max"] == 6.0


def test_histogram_bins():
    h = histogram([1, 2, 3, 4, 5], bins=2)
    assert [b["count"] for b in h] == [2, 3]              # [1,3)->2, [3,5]->3
    assert histogram([]) == []
    assert histogram([5, 5, 5])[0]["count"] == 3          # todos iguales -> un bin


def test_distribution_counts_and_fractions():
    d = distribution([{"A": 2, "B": 1}, {"A": 1}])
    assert d["counts"] == {"A": 3, "B": 1} and d["total"] == 4
    assert d["fractions"] == {"A": 0.75, "B": 0.25}


# --- loader ------------------------------------------------------------------
def test_loader_reads_corpus(tmp_path):
    root = _corpus_dir(tmp_path)
    corpus = load_corpus(root)
    assert len(corpus) == 2
    assert [d.documentary_id for d in corpus.documentaries] == ["doc_a", "doc_b"]
    assert len(corpus.all_shots()) == 3


def test_loader_empty_when_no_knowledge(tmp_path):
    assert len(load_corpus(str(tmp_path / "nope"))) == 0


# --- synthesizer -------------------------------------------------------------
def test_synthesize_produces_six_profiles(tmp_path):
    corpus = load_corpus(_corpus_dir(tmp_path))
    profiles = KnowledgeSynthesizer(corpus).synthesize()
    assert set(profiles) == {"true_crime", "documentary_style", "cinematography_patterns",
                             "editing_patterns", "motion_patterns", "lighting_patterns"}


def test_editing_profile_aggregates_shot_lengths(tmp_path):
    corpus = load_corpus(_corpus_dir(tmp_path))
    editing = KnowledgeSynthesizer(corpus).editing()
    assert editing["shot_length"]["count"] == 3
    assert editing["shot_length"]["mean"] == 4.0          # (2+4+6)/3
    assert editing["pacing_tier"]["counts"] == {"FAST": 1, "SLOW": 1}
    # correlación avg_shot_length vs cuts_per_minute: (3,20),(6,10) -> -1.0
    assert editing["correlations"]["avg_shot_length__cuts_per_minute"] == -1.0


def test_distributions_sum_to_total_shots(tmp_path):
    corpus = load_corpus(_corpus_dir(tmp_path))
    prof = KnowledgeSynthesizer(corpus).cinematography()
    assert prof["shot_size"]["total"] == 3
    assert prof["shot_size"]["counts"] == {"CLOSE": 1, "MEDIUM": 1, "WIDE": 1}


def test_motion_and_lighting_profiles(tmp_path):
    corpus = load_corpus(_corpus_dir(tmp_path))
    syn = KnowledgeSynthesizer(corpus)
    motion = syn.motion()
    assert motion["motion_magnitude"]["count"] == 3
    assert motion["movement"]["counts"] == {"PAN": 1, "STATIC": 2}
    lighting = syn.lighting()
    assert lighting["lighting"]["counts"] == {"HIGH_KEY": 1, "LOW_KEY": 2}
    assert lighting["correlations"]["brightness__contrast"] is not None


def test_true_crime_is_labeled_not_inferred(tmp_path):
    corpus = load_corpus(_corpus_dir(tmp_path))
    tc = KnowledgeSynthesizer(corpus).synthesize()["true_crime"]
    assert tc["genre"] == "true_crime" and "no inferido" in tc["note"]
    assert tc["corpus"]["documentaries"] == 2


def test_synthesis_is_reproducible(tmp_path):
    corpus = load_corpus(_corpus_dir(tmp_path))
    assert KnowledgeSynthesizer(corpus).synthesize() == KnowledgeSynthesizer(corpus).synthesize()


def test_empty_corpus_produces_profiles_without_crash(tmp_path):
    corpus = load_corpus(str(tmp_path / "empty"))
    profiles = KnowledgeSynthesizer(corpus).synthesize()
    assert profiles["editing_patterns"]["shot_length"]["count"] == 0
    assert profiles["documentary_style"]["corpus"]["documentaries"] == 0


# --- persistencia / CLI ------------------------------------------------------
def test_write_styles_creates_six_files(tmp_path):
    corpus = load_corpus(_corpus_dir(tmp_path))
    profiles = KnowledgeSynthesizer(corpus).synthesize()
    out = str(tmp_path / "styles")
    paths = write_styles(profiles, out)
    for name in profiles:
        assert os.path.exists(paths[name])
        data = json.load(open(paths[name], encoding="utf-8"))
        assert data["schema_version"] == "1.0" and data["dks_version"] == "DKS-001"


def test_cli_synthesize_knowledge(tmp_path):
    import app.cli.synthesize_knowledge as cli
    root = _corpus_dir(tmp_path)
    out = str(tmp_path / "styles")
    result = cli.run(root, out)
    assert result["documentaries"] == 2
    assert os.path.exists(os.path.join(out, "true_crime.json"))
    assert os.path.exists(os.path.join(out, "lighting_patterns.json"))
