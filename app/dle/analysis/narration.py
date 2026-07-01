"""Presencia de narración por plano a partir de la transcripción (determinista).

Si hay transcripción, un plano cuyo intervalo solapa un segmento de habla tiene
narración. Sin transcripción no se puede afirmar → UNKNOWN (nunca inventar).
"""

from app.dle import UNKNOWN
from app.dle.models import Transcript


def narration_present(start: float, end: float, transcript: Transcript) -> str:
    if not transcript or not transcript.available:
        return UNKNOWN
    for seg in transcript.segments:
        if seg.end > start and seg.start < end and seg.text.strip():
            return "true"
    return "false"
