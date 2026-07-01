"""Tests del Production Advisor (scaffold) — deterministas, aislados de knowledge/ real."""

import json
import os

from app.advisor import (
    AdvisorReport,
    CorpusSnapshot,
    ProductionAdvisor,
)
from app.advisor.knowledge_reader import KnowledgeReader
from app.advisor.models import CAPABILITIES
from app.advisor.persistence import ReportWriter, render_report


def _write_knowledge(root, *, stats=True, styles=True, corrupt=False):
    os.makedirs(root, exist_ok=True)
    if stats:
        payload = {"documentaries_learned": 6, "hours_learned": 3.5,
                   "shots_analyzed": 1500, "scenes": 1200}
        with open(os.path.join(root, "learning_statistics.json"), "w", encoding="utf-8") as h:
            h.write("{ broken" if corrupt else json.dumps(payload))
    if styles:
        sdir = os.path.join(root, "styles")
        os.makedirs(sdir, exist_ok=True)
        with open(os.path.join(sdir, "editing_patterns.json"), "w", encoding="utf-8") as h:
            json.dump({"x": 1}, h)


# --- reader (solo lectura, defensivo) ----------------------------------------

def test_reader_builds_snapshot(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_knowledge(root)
    snap = KnowledgeReader(root).snapshot()
    assert snap.available and snap.documentaries == 6 and snap.shots == 1500
    assert "learning_statistics.json" in snap.sources_read
    assert any(s.startswith("styles") for s in snap.sources_read)
    assert len(snap.capabilities) == len(CAPABILITIES)


def test_reader_handles_missing_knowledge(tmp_path):
    snap = KnowledgeReader(str(tmp_path / "nope")).snapshot()
    assert snap.available is False and snap.documentaries == 0


def test_reader_tolerates_corrupt_file(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_knowledge(root, stats=True, styles=False, corrupt=True)
    snap = KnowledgeReader(root).snapshot()
    # fichero a medio escribir -> no disponible por esa vía, sin lanzar
    assert snap.documentaries == 0


def test_reader_is_readonly(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_knowledge(root)
    before = sorted(os.listdir(root))
    KnowledgeReader(root).snapshot()
    assert sorted(os.listdir(root)) == before   # no escribe nada en knowledge/


# --- orquestador --------------------------------------------------------------

def test_advisor_produces_report(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_knowledge(root)
    report = ProductionAdvisor(knowledge_root=root).advise()
    assert isinstance(report, AdvisorReport)
    assert report.snapshot.documentaries == 6
    assert any(g.id.startswith("capability.") for g in report.gaps)
    assert report.recommendations and report.roadmap


def test_advisor_is_deterministic(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_knowledge(root)
    a = ProductionAdvisor(knowledge_root=root).advise().to_dict()
    b = ProductionAdvisor(knowledge_root=root).advise().to_dict()
    assert a == b


def test_advisor_empty_corpus_gap(tmp_path):
    report = ProductionAdvisor(knowledge_root=str(tmp_path / "empty")).advise()
    assert any(g.id == "corpus.empty" for g in report.gaps)


# --- persistencia (nunca en knowledge/) --------------------------------------

def test_persistence_writes_outside_knowledge(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_knowledge(root)
    out = str(tmp_path / "output" / "advisor")
    report, paths = ProductionAdvisor(knowledge_root=root).advise_and_write(out_dir=out)
    assert os.path.exists(paths["json"]) and os.path.exists(paths["markdown"])
    # no se creó nada nuevo dentro de knowledge/
    assert "advisor_report.json" not in os.listdir(root)
    data = json.loads(open(paths["json"], encoding="utf-8").read())
    assert data["snapshot"]["documentaries"] == 6


def test_render_report_sections(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_knowledge(root)
    text = render_report(ProductionAdvisor(knowledge_root=root).advise())
    for section in ("Production Advisor report", "Capability coverage", "Gaps",
                    "Recommendations", "Notes"):
        assert section in text


# --- serialización + interfaces ----------------------------------------------

def test_snapshot_serialization_roundtrip():
    snap = CorpusSnapshot(available=True, documentaries=2, hours=1.0)
    assert snap.to_dict()["documentaries"] == 2


def test_writer_default_dir_is_output_advisor():
    assert os.path.join("output", "advisor") in ReportWriter().out_dir


def test_no_random_in_package():
    import importlib
    import pkgutil

    import app.advisor as pkg
    for mod in pkgutil.iter_modules(pkg.__path__):
        source = importlib.import_module(f"app.advisor.{mod.name}")
        assert "random" not in getattr(source, "__dict__", {})


# =========================== ADV-002 ==========================================

def _write_corpus_with_styles(root):
    """knowledge/ con learning_statistics + styles DKS (distribuciones medidas)."""
    os.makedirs(os.path.join(root, "styles"), exist_ok=True)
    with open(os.path.join(root, "learning_statistics.json"), "w", encoding="utf-8") as h:
        json.dump({"documentaries_learned": 68, "hours_learned": 36.0,
                   "shots_analyzed": 19000, "scenes": 16000}, h)
    motion = {"total_shots": 19000, "documentaries": 68,
              "movement": {"counts": {"subtle": 7000, "moderate": 4800, "static": 3800,
                                      "dynamic": 3380, "UNKNOWN": 20},
                           "fractions": {"subtle": 0.368, "moderate": 0.253, "static": 0.2,
                                         "dynamic": 0.178, "UNKNOWN": 0.001},
                           "total": 19000}}
    lighting = {"total_shots": 19000, "documentaries": 68,
                "lighting": {"counts": {"balanced": 10600, "low-key": 6900, "high-key": 1500},
                             "fractions": {"balanced": 0.558, "low-key": 0.363, "high-key": 0.079},
                             "total": 19000},
                "color_temperature": {"counts": {"neutral": 8700, "warm": 8200, "cool": 2100},
                                      "fractions": {"neutral": 0.458, "warm": 0.432, "cool": 0.11},
                                      "total": 19000}}
    cine = {"total_shots": 19000, "documentaries": 68,
            "shot_size": {"counts": {"UNKNOWN": 19000}, "fractions": {"UNKNOWN": 1.0}, "total": 19000},
            "composition": {"counts": {"UNKNOWN": 19000}, "fractions": {"UNKNOWN": 1.0}, "total": 19000}}
    editing = {"total_shots": 19000, "documentaries": 68,
               "pacing_tier": {"counts": {"slow": 44, "moderate": 22, "fast": 2},
                               "fractions": {"slow": 0.647, "moderate": 0.323, "fast": 0.029},
                               "total": 68},
               "cuts_per_minute": {"count": 68, "mean": 8.4, "median": 8.2, "min": 0.8,
                                   "max": 32.0, "stdev": 6.4}}
    for name, payload in (("motion_patterns", motion), ("lighting_patterns", lighting),
                          ("cinematography_patterns", cine), ("editing_patterns", editing)):
        with open(os.path.join(root, "styles", f"{name}.json"), "w", encoding="utf-8") as h:
            json.dump(payload, h)


def test_capability_matrix_measured_vs_unknown(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_corpus_with_styles(root)
    report = ProductionAdvisor(knowledge_root=root).advise()
    rows = {r.name: r for r in report.capability_matrix}
    assert rows["movement"].status == "SUPPORTED" and rows["movement"].corpus_observed
    assert rows["shot_size"].status == "UNKNOWN" and rows["shot_size"].corpus_observed is False
    assert rows["interviews"].status == "MISSING"     # pipeline no lo produce (hecho)
    assert rows["narration"].status == "SUPPORTED"


def test_gaps_quantified_blindspots_outrank_unquantified(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_corpus_with_styles(root)
    report = ProductionAdvisor(knowledge_root=root).advise()
    ids = [g.id for g in report.gaps]
    assert "blindspot.shot_size" in ids and "blindspot.composition" in ids
    # los gaps con frecuencia medida van primero (rank menor) que los no cuantificados
    quant = [g for g in report.gaps if g.frequency is not None]
    unquant = [g for g in report.gaps if g.frequency is None]
    assert quant and unquant
    assert max(g.rank for g in quant) < min(g.rank for g in unquant)
    # blindspot 100% UNKNOWN es el de mayor frecuencia → rank 1
    assert report.gaps[0].frequency == 1.0


def test_impact_ranking_is_frequency_based(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_corpus_with_styles(root)
    report = ProductionAdvisor(knowledge_root=root).advise()
    quant = [g for g in report.gaps if g.frequency is not None]
    freqs = [g.frequency for g in quant]
    assert freqs == sorted(freqs, reverse=True)        # orden por frecuencia desc


def test_completeness_flags_underrepresented(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_corpus_with_styles(root)
    report = ProductionAdvisor(knowledge_root=root).advise()
    flagged = {(c.dimension, c.category) for c in report.completeness}
    assert ("pacing_tier", "fast") in flagged          # 2.9% << media
    assert all(c.recommendation for c in report.completeness)


def test_confidence_by_sample_size(tmp_path):
    from app.advisor.models import confidence_from
    assert confidence_from(19000, high=5000, medium=500) == "HIGH"
    assert confidence_from(600, high=5000, medium=500) == "MEDIUM"
    assert confidence_from(10, high=5000, medium=500) == "LOW"
    root = str(tmp_path / "knowledge")
    _write_corpus_with_styles(root)
    report = ProductionAdvisor(knowledge_root=root).advise()
    assert any(g.confidence == "HIGH" for g in report.gaps)   # 19000 obs → alta


def test_discoveries_are_deterministic_aggregates(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_corpus_with_styles(root)
    a = ProductionAdvisor(knowledge_root=root).advise()
    b = ProductionAdvisor(knowledge_root=root).advise()
    assert [d.to_dict() for d in a.discoveries] == [d.to_dict() for d in b.discoveries]
    statements = " ".join(d.statement for d in a.discoveries)
    assert "movement" in statements and "subtle" in statements   # dominante real


def test_adv002_writes_four_reports_outside_knowledge(tmp_path):
    root = str(tmp_path / "knowledge")
    _write_corpus_with_styles(root)
    out = str(tmp_path / "output" / "advisor")
    _report, paths = ProductionAdvisor(knowledge_root=root).advise_and_write(out_dir=out)
    for key in ("production_advisor", "capability_matrix", "gap_report", "discoveries"):
        assert os.path.exists(paths[key])
    assert os.path.basename(paths["production_advisor"]) == "production_advisor.md"
    # nada nuevo dentro de knowledge/
    assert "production_advisor.md" not in os.listdir(root)
    matrix = json.loads(open(paths["capability_matrix"], encoding="utf-8").read())
    assert any(r["name"] == "movement" for r in matrix["rows"])
