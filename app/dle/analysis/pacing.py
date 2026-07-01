"""Análisis de ritmo: longitudes de plano y clasificación de pacing (determinista)."""

from statistics import median

from app.dle import UNKNOWN
from app.dle.models import ShotAnalysis


def shot_length_stats(shots: list[ShotAnalysis]) -> dict:
    lengths = [s.duration for s in shots if s.duration > 0]
    if not lengths:
        return {"average": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "tier": UNKNOWN}
    avg = sum(lengths) / len(lengths)
    return {
        "average": round(avg, 3), "median": round(median(lengths), 3),
        "min": round(min(lengths), 3), "max": round(max(lengths), 3),
        "tier": _pacing_tier(avg),
    }


def _pacing_tier(avg_shot_length: float) -> str:
    if avg_shot_length <= 0:
        return UNKNOWN
    if avg_shot_length < 2.5:
        return "fast"
    if avg_shot_length < 5.0:
        return "moderate"
    return "slow"
