"""Algoritmo determinista de diversidad cinematográfica.

La diversidad de un plano = 1 - (máxima similitud con los últimos N planos). La
similitud entre dos planos es la fracción PONDERADA de dimensiones variables que
coinciden. Sin aleatoriedad: mismas entradas → mismo resultado.
"""

from app.sde.models import VARIABLE_DIMENSIONS, ShotFingerprint

# Peso de cada dimensión variable (suma = 1.0). Tamaño/ángulo/composición pesan más.
_WEIGHTS = {
    "shot_size": 0.20,
    "camera_angle": 0.18,
    "composition": 0.16,
    "lens": 0.14,
    "subject_position": 0.10,
    "camera_height": 0.10,
    "gaze": 0.07,
    "movement": 0.05,
}


def similarity(a: ShotFingerprint, b: ShotFingerprint) -> float:
    """0.0 (totalmente distintos) .. 1.0 (misma composición)."""
    score = 0.0
    for dim in VARIABLE_DIMENSIONS:
        if getattr(a, dim) == getattr(b, dim):
            score += _WEIGHTS[dim]
    return round(score, 4)


def diversity_against(fp: ShotFingerprint, history_fps: list[ShotFingerprint]) -> float:
    """1.0 si no se parece a ninguno de los recientes; 0.0 si es idéntico a alguno."""
    if not history_fps:
        return 1.0
    worst = max(similarity(fp, other) for other in history_fps)
    return round(1.0 - worst, 4)


def average_diversity(fingerprints: list[ShotFingerprint], window: int) -> float:
    """Diversidad media de una secuencia, cada plano contra los ``window`` previos."""
    if not fingerprints:
        return 0.0
    total = 0.0
    for i, fp in enumerate(fingerprints):
        prev = fingerprints[max(0, i - window):i]
        total += diversity_against(fp, prev)
    return round(total / len(fingerprints), 4)
