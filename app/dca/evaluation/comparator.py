"""Comparator (DCA-003) — mide la distancia entre la generación y el corpus.

Determinista. Cada dimensión se mide con datos públicos (ProductionContext = corpus;
VisualPlan = generado; Evidence Coverage / Recreation Candidates = evidencias). Nunca
interpreta: solo reporta valor de corpus, valor generado, desviación y estado.
"""

from app.dca.evaluation.models import ComparisonMetric, MetricStatus

UNKNOWN = "UNKNOWN"
_TOLERANCE = 0.10                      # bucket de reporte (no es juicio de calidad)

_MOVE_TIER = {
    "static": "low", "mostly_static": "low", "subtle": "low", "slow": "low",
    "pan": "medium", "tilt": "medium", "zoom": "medium", "moderate": "medium", "push_in": "medium",
    "tracking": "high", "handheld": "high", "dynamic": "high", "fast": "high",
}


def _known(v) -> bool:
    return v is not None and v != UNKNOWN


def _move_tier(v):
    return _MOVE_TIER.get(str(v).lower()) if _known(v) else None


def _light_tier(v):
    s = str(v).lower()
    if not _known(v):
        return None
    if "low-key" in s:
        return "low-key"
    if "high-key" in s:
        return "high-key"
    return "balanced"


def _color_token(grade):
    s = str(grade).lower()
    for t in ("warm", "cool", "neutral"):
        if t in s:
            return t
    return None


def _categorical(dim, corpus, generated, *, corpus_norm=None, gen_norm=None, unit=""):
    if not _known(corpus) or not _known(generated):
        return ComparisonMetric(dim, corpus if corpus is not None else UNKNOWN,
                                generated if generated is not None else UNKNOWN,
                                None, "categorical", MetricStatus.UNKNOWN, unit)
    c = corpus_norm if corpus_norm is not None else corpus
    g = gen_norm if gen_norm is not None else generated
    aligned = (c == g)
    return ComparisonMetric(dim, corpus, generated, 0.0 if aligned else 1.0, "categorical",
                            MetricStatus.ALIGNED if aligned else MetricStatus.DIFFERS, unit,
                            note=f"corpus={c} generado={g}")


def _numeric(dim, corpus, generated, *, unit=""):
    if not _known(corpus) or not _known(generated) or not isinstance(corpus, (int, float)) \
            or not isinstance(generated, (int, float)):
        return ComparisonMetric(dim, corpus if corpus is not None else UNKNOWN,
                                generated if generated is not None else UNKNOWN,
                                None, "numeric", MetricStatus.UNKNOWN, unit)
    dev = round(abs(generated - corpus) / corpus, 4) if corpus else None
    status = MetricStatus.ALIGNED if (dev is not None and dev <= _TOLERANCE) else MetricStatus.DIFFERS
    return ComparisonMetric(dim, corpus, generated, dev, "numeric", status, unit,
                            note=f"desviación {round((dev or 0) * 100)}%")


def _coverage(dim, requested, obtained, owner_note=""):
    if requested is None or obtained is None:
        return ComparisonMetric(dim, requested if requested is not None else UNKNOWN,
                                obtained if obtained is not None else UNKNOWN, None,
                                "coverage", MetricStatus.UNKNOWN)
    dev = round(max(0.0, (requested - obtained) / requested), 4) if requested else 0.0
    status = MetricStatus.ALIGNED if obtained >= requested else MetricStatus.DIFFERS
    return ComparisonMetric(dim, requested, obtained, dev, "coverage", status, "items",
                            note=owner_note or f"{obtained}/{requested}")


def _mean(values):
    values = [v for v in values if isinstance(v, (int, float))]
    return round(sum(values) / len(values), 2) if values else None


def build_comparisons(production_context, visual_plans, *, ece_coverage=None,
                      recreation_candidates=None, composer_used=None,
                      recreation_used=None) -> list[ComparisonMetric]:
    ctx = production_context
    plans = list(visual_plans or [])
    shots = [s for p in plans for s in getattr(p, "shots", [])]

    gen_avg = _mean([s.duration for s in shots])
    gen_pacing = next((p.pacing_tier for p in plans if getattr(p, "pacing_tier", "")), None)
    gen_move = next((p.movement_tendency for p in plans if getattr(p, "movement_tendency", "")), None)
    gen_color = _color_token(plans[0].grade) if plans else None
    gen_light = _light_tier(plans[0].lighting_tendency or (shots[0].lighting if shots else "")) \
        if plans else None

    def _ctx(section, key):
        return ctx.get(section, key) if ctx is not None else None

    comparisons = [
        _categorical("pacing", _ctx("storytelling", "pacing"), gen_pacing),
        _numeric("average_shot_duration", _ctx("storytelling", "average_shot_duration"),
                 gen_avg, unit="s"),
        _categorical("movement", _ctx("cinematography", "dominant_movement"), gen_move,
                     corpus_norm=_move_tier(_ctx("cinematography", "dominant_movement")),
                     gen_norm=_move_tier(gen_move)),
        _categorical("color_temperature", _ctx("cinematography", "color_temperature"), gen_color),
        _categorical("lighting", _ctx("cinematography", "lighting"), gen_light,
                     corpus_norm=_light_tier(_ctx("cinematography", "lighting")),
                     gen_norm=gen_light),
    ]

    # Evidencias (si hay coverage del ECE)
    if isinstance(ece_coverage, dict):
        dims = {d.get("name"): d for d in ece_coverage.get("dimensions", [])}
        required = sum(int(d.get("required", 0)) for d in dims.values())
        found = sum(int(d.get("discovered", 0)) for d in dims.values())
        comparisons.append(_coverage("evidence_coverage", required, found))
        if composer_used is not None:
            comparisons.append(_coverage("evidence_utilization", found, composer_used))
        chrono = dims.get("chronology")
        if chrono:
            comparisons.append(ComparisonMetric(
                "chronology", "COMPLETE", chrono.get("state", UNKNOWN),
                0.0 if chrono.get("state") == "COMPLETE" else 1.0, "categorical",
                MetricStatus.ALIGNED if chrono.get("state") == "COMPLETE" else MetricStatus.DIFFERS))

    # Recreaciones (si hay candidatas del ECE)
    if recreation_candidates is not None:
        recommended = len(recreation_candidates)
        used = recreation_used if recreation_used is not None else 0
        comparisons.append(_coverage("recreation_usage", recommended, used,
                                     owner_note=f"recomendadas {recommended}, usadas {used}"))
    return comparisons
