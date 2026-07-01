"""Diseñador de ritmo (NAR-001).

Decide la DURACIÓN SUGERIDA y la intención de ritmo de cada segmento. Es INTENCIÓN narrativa,
no cortes: VIS/Composer deciden los planos y los cortes reales (ver contracts.NAR_DELEGATES).
Usa el pacing del corpus (KBG) cuando existe; si es UNKNOWN, cae a la duración base del
catálogo y lo declara (nunca inventa un valor de corpus).
"""

from app.nar.beats import beat_profile
from app.nar.models import NarrativeContext, NarrativeSegment
from app.nar.vocabulary import UNKNOWN

# Factor de escala según el pacing del corpus (objetivo, acotado).
_CORPUS_FACTOR = {"fast": 0.85, "moderate": 1.0, "slow": 1.15}


class PacingDesigner:
    def plan(self, context: NarrativeContext,
             segment: NarrativeSegment) -> tuple[float, str, str]:
        profile = beat_profile(segment.beat)
        base = profile.base_duration_seconds
        pacing_value, conf = context.knowledge_value("storytelling", "pacing")

        if pacing_value != UNKNOWN and pacing_value in _CORPUS_FACTOR:
            factor = _CORPUS_FACTOR[pacing_value]
            basis = (f"base {base:.0f}s (beat {segment.beat}) × {factor} "
                     f"por pacing de corpus '{pacing_value}' (conf {conf:.2f}, DKS)")
        else:
            factor = 1.0
            basis = (f"base {base:.0f}s (beat {segment.beat}); "
                     f"pacing de corpus UNKNOWN → sin ajuste")

        duration = round(base * factor, 1)
        return duration, basis, profile.pacing
