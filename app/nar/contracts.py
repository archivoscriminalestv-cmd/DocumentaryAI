"""Contratos del NAR — la FRONTERA entre el cerebro narrativo y los motores de ejecución.

El Narrative Intelligence Engine decide CÓMO contar la historia, nunca cómo se ve un plano
ni cómo se corta. Este módulo define el único objeto que el NAR entrega aguas abajo —el
``NarrativeDirective``— y documenta de forma explícita qué decisiones pertenecen a otros
motores. Cuando una decisión cae fuera de esta frontera, el NAR NO la toma: la expresa como
intención en el directive y deja la responsabilidad a su motor (regla del sprint).

Flujo:  NAR (NarrativeDirective)  →  VIS  →  VAI  →  Composer

contracts.py solo depende de ``vocabulary`` (sin ciclos): ``models`` lo importa, no al revés.
"""

from dataclasses import asdict, dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Frontera de responsabilidades (documentada como dato, auditable).
# ---------------------------------------------------------------------------

#: Lo que el NAR SÍ decide (intención narrativa).
NAR_DECIDES = (
    "narrative_structure", "act_and_chapter_order", "beat_order", "timeline_order",
    "segment_purpose", "emotion", "tension", "emotion_curve",
    "which_evidence_appears_and_why", "evidence_use", "recreation_justification",
    "reveal_schedule", "hooks_foreshadow_cliffhangers_payoffs", "viewer_questions",
    "narration_mode_and_intent", "where_to_stay_silent", "pacing_intent",
    "suggested_segment_duration",
)

#: Lo que el NAR NO decide (se delega vía contrato al motor correspondiente).
NAR_DELEGATES = {
    "shot_size": "VIS",
    "shot_composition": "VIS",
    "shot_sequence_within_segment": "VIS",
    "camera_movement": "VAI",
    "color_temperature": "VAI",
    "lighting": "VAI",
    "visual_style": "VAI",
    "exact_shot_duration": "VIS/VAI",
    "cut_type": "Composer",
    "transitions_render": "Composer",
    "audio_mix": "Composer",
    "narration_text": "future:NarrationEngine",
    "music_track": "future:MusicEngine",
}


@dataclass
class NarrativeDirective:
    """Contrato NAR → VIS por segmento. Expresa INTENCIÓN narrativa, no ejecución visual.

    VIS/VAI/Composer leen este directive y deciden lo suyo (planos, cámara, color, cortes).
    Todo aquí es enumerable y trazable; nada es prosa.
    """

    segment_id: str
    purpose: str                                   # SegmentPurpose
    emotion: str                                   # Emotion
    tension: str                                   # TensionLevel
    pacing_intent: str                             # PacingIntent
    narration_mode: str                            # NarrationMode
    suggested_duration_seconds: float = 0.0
    emphasis: str = "NORMAL"                        # LOW | NORMAL | HIGH
    evidence_dimensions: list[str] = field(default_factory=list)   # orden de aparición
    viewer_question_ids: list[str] = field(default_factory=list)
    mechanism_ids: list[str] = field(default_factory=list)
    duration_basis: str = ""                       # por qué esa duración (trazabilidad)
    delegated_to: dict[str, str] = field(default_factory=lambda: dict(NAR_DELEGATES))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
