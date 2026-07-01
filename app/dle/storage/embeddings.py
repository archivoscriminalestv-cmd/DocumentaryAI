"""Embedding determinista de un documental (sin ML).

Vector de características numérico de longitud fija que resume el documental para poder
COMPARARLO con otros más adelante. No usa modelos ni aleatoriedad: deriva de las
estadísticas ya calculadas. (En el futuro podrá sustituirse por embeddings reales.)
"""

from app.dle.models import ShotAnalysis

# Orden FIJO de las dimensiones del embedding (estable entre documentales).
LIGHTING_KEYS = ("low-key", "balanced", "high-key")
TEMP_KEYS = ("warm", "neutral", "cool")
MOVE_KEYS = ("static", "subtle", "moderate", "dynamic")


def _fractions(values: list[str], keys: tuple) -> list[float]:
    total = len(values) or 1
    return [round(sum(1 for v in values if v == k) / total, 4) for k in keys]


def build_embedding(shots: list[ShotAnalysis], avg_shot_length: float,
                    cuts_per_minute: float) -> list[float]:
    if not shots:
        return [0.0] * (2 + len(LIGHTING_KEYS) + len(TEMP_KEYS) + len(MOVE_KEYS) + 2)
    brightness = sum(s.brightness for s in shots) / len(shots)
    contrast = sum(s.contrast for s in shots) / len(shots)
    vec = [
        round(min(1.0, avg_shot_length / 10.0), 4),     # ritmo (normalizado)
        round(min(1.0, cuts_per_minute / 60.0), 4),
        *_fractions([s.lighting for s in shots], LIGHTING_KEYS),
        *_fractions([s.color_temperature for s in shots], TEMP_KEYS),
        *_fractions([s.movement for s in shots], MOVE_KEYS),
        round(brightness / 255.0, 4),
        round(min(1.0, contrast / 128.0), 4),
    ]
    return vec
