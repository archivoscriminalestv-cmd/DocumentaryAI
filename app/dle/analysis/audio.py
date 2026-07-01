"""Análisis de audio por plano a partir de intervalos de silencio (determinista).

``audio_present`` se deriva de FFmpeg silencedetect. La distinción música/efectos
requiere un clasificador (no disponible) → UNKNOWN. La narración la aporta
``narration.py`` si hay transcripción.
"""

from app.dle import UNKNOWN


def _overlaps_nonsilence(start: float, end: float, silences: list[tuple[float, float]]) -> bool:
    """True si [start,end] tiene algún tramo NO silencioso."""
    cursor = start
    for s0, s1 in silences:
        if s1 <= start or s0 >= end:
            continue
        if s0 > cursor:
            return True            # hay sonido antes del silencio
        cursor = max(cursor, s1)
    return cursor < end            # queda sonido tras el último silencio


def audio_present(start: float, end: float, silences: list[tuple[float, float]],
                  has_audio: bool) -> str:
    if not has_audio:
        return "false"
    if not silences:
        return "true"              # con pista de audio y sin silencios detectados
    return "true" if _overlaps_nonsilence(start, end, silences) else "false"


def music_present() -> str:
    # Sin clasificador de audio: no se puede afirmar -> UNKNOWN (nunca inventar).
    return UNKNOWN


def effects_present() -> str:
    return UNKNOWN
