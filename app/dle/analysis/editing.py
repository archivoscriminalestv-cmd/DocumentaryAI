"""Análisis de edición: cortes, escenas y ritmo agregado (determinista)."""

from app.dle.models import ShotAnalysis


def cut_count(shots: list[ShotAnalysis]) -> int:
    return max(0, len(shots) - 1)


def cuts_per_minute(shots: list[ShotAnalysis], duration: float) -> float:
    if duration <= 0:
        return 0.0
    return round(cut_count(shots) / (duration / 60.0), 3)


def time_where(shots: list[ShotAnalysis], attr: str, value: str = "true") -> float:
    return round(sum(s.duration for s in shots if getattr(s, attr) == value), 3)
