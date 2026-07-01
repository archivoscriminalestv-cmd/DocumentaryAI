"""Tests del Director (Scene[] -> DirectedScene[], C-08). Determinista, sin IA."""

import json
from dataclasses import asdict

from app.application.director_service import DirectorService
from app.domain.narrative.directed_scene import DirectedScene
from app.domain.narrative.scene import Scene

_VALID_TONES = {"investigative", "explanatory", "dramatic", "neutral", "conclusive"}


def _scene(id_, title, narration, fact_ids):
    return Scene(id=id_, title=title, narration=narration, fact_ids=list(fact_ids))


_CAUSAL = _scene("s-c", "The causal chain behind reactor",
                 "The reactor failed. As a consequence, an explosion occurred.", ["f1", "f2"])
_TEMPORAL = _scene("s-t", "The timeline of 1986",
                   "An explosion occurred. Subsequently, it was recorded in 1986.", ["f2", "f3"])
_GEO = _scene("s-g", "The setting that connects Pripyat",
              "The plant operated. In the same setting, residents lived nearby.", ["f4", "f5"])
_HIER = _scene("s-h", "How RBMK fits into the bigger picture",
               "An RBMK reactor existed. More broadly, it is a nuclear reactor.", ["f6", "f7"])
_ASSOC = _scene("s-a", "The connections around the system",
                "The reactor was gray. Relatedly, it stood tall.", ["f8", "f9"])


def test_reorders_causal_first_associative_last():
    out = DirectorService().direct([_ASSOC, _GEO, _TEMPORAL, _CAUSAL, _HIER])
    order = [d.id for d in out]
    assert order[0] == "s-c"   # causal abre (gancho/escalada)
    assert order[-1] == "s-a"  # asociativo cierra (síntesis)
    # orden completo determinista: causal, temporal, geo, hier, assoc
    assert order == ["s-c", "s-t", "s-g", "s-h", "s-a"]


def test_fact_ids_pass_through_unchanged():
    out = DirectorService().direct([_CAUSAL, _TEMPORAL])
    by_id = {d.id: d for d in out}
    assert by_id["s-c"].fact_ids == ["f1", "f2"]
    assert by_id["s-t"].fact_ids == ["f2", "f3"]


def test_title_and_narration_unchanged():
    out = DirectorService().direct([_CAUSAL])
    assert out[0].title == _CAUSAL.title
    assert out[0].narration == _CAUSAL.narration


def test_causal_high_emphasis_long_duration():
    d = DirectorService().direct([_CAUSAL, _ASSOC])[0]  # s-c primero
    assert d.id == "s-c"
    assert 0.8 <= d.emphasis <= 1.0
    assert 3.0 <= d.duration_hint <= 5.0


def test_associative_low_emphasis_light_duration():
    out = DirectorService().direct([_CAUSAL, _ASSOC])
    d = next(x for x in out if x.id == "s-a")
    assert 0.2 <= d.emphasis <= 0.5
    assert 0.5 <= d.duration_hint <= 1.5


def test_temporal_medium_band():
    out = DirectorService().direct([_CAUSAL, _TEMPORAL, _ASSOC])
    d = next(x for x in out if x.id == "s-t")
    assert 0.5 <= d.emphasis <= 0.7
    assert 1.5 <= d.duration_hint <= 3.0


def test_tone_first_investigative_last_conclusive():
    out = DirectorService().direct([_ASSOC, _CAUSAL, _TEMPORAL])
    assert out[0].tone == "investigative"
    assert out[-1].tone == "conclusive"
    assert all(d.tone in _VALID_TONES for d in out)


def test_all_tones_are_valid_enum_values():
    out = DirectorService().direct([_CAUSAL, _TEMPORAL, _GEO, _HIER, _ASSOC])
    assert all(d.tone in _VALID_TONES for d in out)


def test_scenes_not_added_removed_merged_or_split():
    inputs = [_CAUSAL, _TEMPORAL, _GEO, _HIER, _ASSOC]
    out = DirectorService().direct(inputs)
    assert len(out) == len(inputs)
    assert {d.id for d in out} == {s.id for s in inputs}


def test_empty_input_returns_empty():
    assert DirectorService().direct([]) == []
    assert DirectorService().direct(None) == []


def test_invalid_scenes_skipped_safely():
    out = DirectorService().direct([_CAUSAL, None, object(), _ASSOC])
    assert {d.id for d in out} == {"s-c", "s-a"}


def test_output_is_json_serializable():
    out = DirectorService().direct([_CAUSAL])
    decoded = json.loads(json.dumps([asdict(d) for d in out], ensure_ascii=False))
    assert set(decoded[0].keys()) == {
        "id", "title", "narration", "fact_ids", "duration_hint", "emphasis", "tone",
    }


def test_direction_is_deterministic():
    inputs = [_ASSOC, _CAUSAL, _TEMPORAL, _GEO, _HIER]
    a = DirectorService().direct(inputs)
    b = DirectorService().direct(inputs)
    assert [asdict(x) for x in a] == [asdict(x) for x in b]


def test_single_scene_uses_category_tone():
    out = DirectorService().direct([_CAUSAL])
    assert len(out) == 1
    assert out[0].tone == "dramatic"  # sin override de posición
