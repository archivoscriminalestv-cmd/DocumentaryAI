"""Tests del DCA Self Evaluation (DCA-003) — deterministas, solo lectura, sin IA."""

import json
import os
from dataclasses import dataclass, field

from app.dca.evaluation.comparator import build_comparisons
from app.dca.evaluation.gap_analyzer import analyze_gaps, owner_of
from app.dca.evaluation.models import MetricStatus
from app.dca.evaluation.persistence import write_evaluation_outputs
from app.dca.orchestrator import DocumentaryChiefArchitect


# --- contexto y plan sintéticos (contratos públicos) -------------------------
class _Ctx:
    """ProductionContext mínimo (corpus)."""
    genre = "true_crime"
    _d = {("storytelling", "pacing"): "moderate",
          ("storytelling", "average_shot_duration"): 2.97,
          ("cinematography", "dominant_movement"): "subtle",
          ("cinematography", "color_temperature"): "warm",
          ("cinematography", "lighting"): "balanced"}

    def get(self, section, key, *, min_confidence=0.0, default=None):
        return self._d.get((section, key), default)


@dataclass
class _Shot:
    duration: float
    lighting: str = "balanced"


@dataclass
class _Plan:
    pacing_tier: str = "slow"
    movement_tendency: str = "dynamic"
    lighting_tendency: str = "balanced flat"
    grade: str = "neutral moderate color grade"
    shots: list = field(default_factory=lambda: [_Shot(4.6), _Shot(4.6), _Shot(4.6)])


# --- comparator --------------------------------------------------------------
def test_comparator_measures_each_dimension():
    comps = {c.dimension: c for c in build_comparisons(_Ctx(), [_Plan()])}
    assert comps["pacing"].status == MetricStatus.DIFFERS           # moderate vs slow
    assert comps["average_shot_duration"].deviation > 0.4           # 2.97 vs 4.6 ~55%
    assert comps["movement"].status == MetricStatus.DIFFERS         # subtle(low) vs dynamic(high)
    assert comps["color_temperature"].status == MetricStatus.DIFFERS  # warm vs neutral
    assert comps["lighting"].status == MetricStatus.ALIGNED         # balanced vs balanced


def test_comparator_evidence_and_recreation():
    coverage = {"dimensions": [{"name": "photographs", "required": 2, "discovered": 1},
                               {"name": "documents", "required": 1, "discovered": 0},
                               {"name": "chronology", "required": 1, "discovered": 0,
                                "state": "MISSING"}]}
    comps = {c.dimension: c for c in build_comparisons(
        _Ctx(), [_Plan()], ece_coverage=coverage, recreation_candidates=[1, 2, 3],
        composer_used=1)}
    assert comps["evidence_coverage"].status == MetricStatus.DIFFERS   # 1/3
    assert comps["chronology"].status == MetricStatus.DIFFERS
    assert comps["recreation_usage"].status == MetricStatus.DIFFERS    # 0 de 3


def test_comparator_unknown_when_no_corpus():
    class _Empty:
        genre = "x"
        def get(self, *a, **k):
            return None
    comps = {c.dimension: c for c in build_comparisons(_Empty(), [_Plan()])}
    assert comps["pacing"].status == MetricStatus.UNKNOWN             # sin corpus -> UNKNOWN


# --- gap analyzer (capability mapping) ---------------------------------------
def test_gaps_map_to_owners():
    gaps = analyze_gaps(build_comparisons(_Ctx(), [_Plan()]))
    owners = {g.dimension: g.owner for g in gaps}
    assert owners["average_shot_duration"] == "VIS"
    assert owners["movement"] == "VAI"
    assert owners["color_temperature"] == "VAI"
    assert owner_of("evidence_coverage") == "EAE" and owner_of("chronology") == "ECE"
    # los huecos son hechos, no opiniones
    assert all("difiere" in g.description or "cubierto" in g.description for g in gaps)


# --- orquestador: evaluate() integrado en el DCA -----------------------------
def test_dca_evaluate_full_cycle():
    gk = {"summary": {"known_ratio": 0.22, "unknown": 32}}
    result = DocumentaryChiefArchitect().evaluate(
        production_context=_Ctx(), visual_plans=[_Plan()], generation_knowledge=gk)
    assert result.comparisons and result.gaps and result.roadmap
    # roadmap ordenado por prioridad 1..n
    ranks = [i.priority_rank for i in result.roadmap]
    assert ranks == list(range(1, len(ranks) + 1))
    # health derivada de datos
    assert 0.0 <= result.health.corpus_alignment <= 1.0
    assert result.health.knowledge_utilization == 0.22
    assert isinstance(result.health.missing_capabilities, int)
    assert result.summary["next_improvement"] != "UNKNOWN"


def test_dca_evaluate_is_deterministic():
    a = DocumentaryChiefArchitect().evaluate(production_context=_Ctx(), visual_plans=[_Plan()])
    b = DocumentaryChiefArchitect().evaluate(production_context=_Ctx(), visual_plans=[_Plan()])
    assert a.to_dict() == b.to_dict()


def test_roadmap_includes_architectural_targets():
    # VUE (no integrado) debe aparecer como objetivo de mejora con consumidores afectados
    result = DocumentaryChiefArchitect().evaluate(production_context=_Ctx(), visual_plans=[_Plan()])
    targets = {i.target for i in result.roadmap}
    assert "VUE" in targets


# --- persistencia ------------------------------------------------------------
def test_persistence_writes_five_files(tmp_path):
    result = DocumentaryChiefArchitect().evaluate(production_context=_Ctx(), visual_plans=[_Plan()])
    paths = write_evaluation_outputs(str(tmp_path / "dca"), result)
    for name in ("evaluation.json", "generation_vs_corpus.json", "improvement_plan.json",
                 "system_health.json", "evaluation_report.md"):
        assert os.path.exists(paths[name])
    gvc = json.load(open(paths["generation_vs_corpus.json"], encoding="utf-8"))
    assert "pacing" in gvc and gvc["average_shot_duration"]["status"] == "differs"
