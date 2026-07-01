"""Catálogo de beats narrativos (NAR-001) — la semántica objetiva de cada función narrativa.

Cada estructura ordena BEATS (vocabulary.NarrativeBeat). Pero un beat tiene un significado
profesional estable, independiente de la estructura que lo use: un ``REVELATION`` siempre
busca impacto y se sostiene; un ``SETUP`` siempre establece contexto y respira. Aquí se fija
ese significado como DATO (no como ``if`` repartidos por el motor). Los diseñadores (emoción,
ritmo, evidencias) leen este catálogo y lo refinan con el contexto del caso.

Determinista. Sin texto libre: solo símbolos del vocabulario.
"""

from dataclasses import dataclass, field

from app.nar.vocabulary import (
    Emotion,
    EvidenceUse,
    NarrationIntent,
    NarrationMode,
    NarrativeBeat,
    PacingIntent,
    SegmentPurpose,
    TensionLevel,
)


@dataclass(frozen=True)
class BeatProfile:
    """Perfil por defecto de un beat. El contexto del caso puede ajustar emoción/tensión."""

    beat: str
    purpose: str
    emotion: str
    tension: str
    narration_mode: str
    narration_intent: str
    pacing: str
    base_duration_seconds: float
    emphasis: str = "NORMAL"
    preferred_evidence_uses: tuple = field(default_factory=tuple)


# Catálogo canónico. Las duraciones son INTENCIÓN narrativa (segundos sugeridos), no cortes:
# VIS/VAI deciden los planos reales dentro de cada segmento.
_CATALOG = {
    NarrativeBeat.HOOK: BeatProfile(
        NarrativeBeat.HOOK, SegmentPurpose.ESTABLISH, Emotion.CURIOSITY, TensionLevel.MEDIUM,
        NarrationMode.NARRATOR, NarrationIntent.QUESTION, PacingIntent.MODERATE, 20.0, "HIGH",
        (EvidenceUse.REVEAL, EvidenceUse.ESTABLISH)),
    NarrativeBeat.SETUP: BeatProfile(
        NarrativeBeat.SETUP, SegmentPurpose.ESTABLISH, Emotion.NEUTRAL, TensionLevel.LOW,
        NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE, PacingIntent.SLOW, 45.0, "NORMAL",
        (EvidenceUse.ESTABLISH, EvidenceUse.LOCATE)),
    NarrativeBeat.INTRODUCE_SUBJECT: BeatProfile(
        NarrativeBeat.INTRODUCE_SUBJECT, SegmentPurpose.INTRODUCE, Emotion.EMPATHY,
        TensionLevel.LOW, NarrationMode.NARRATOR, NarrationIntent.WITNESS, PacingIntent.SLOW,
        40.0, "NORMAL", (EvidenceUse.INTRODUCE, EvidenceUse.ILLUSTRATE)),
    NarrativeBeat.BACKGROUND: BeatProfile(
        NarrativeBeat.BACKGROUND, SegmentPurpose.BUILD_CONTEXT, Emotion.NEUTRAL,
        TensionLevel.LOW, NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE,
        PacingIntent.MODERATE, 50.0, "NORMAL", (EvidenceUse.SUPPORT, EvidenceUse.CHRONICLE)),
    NarrativeBeat.INCITING_INCIDENT: BeatProfile(
        NarrativeBeat.INCITING_INCIDENT, SegmentPurpose.PRESENT_INCIDENT, Emotion.SHOCK,
        TensionLevel.HIGH, NarrationMode.NARRATOR, NarrationIntent.REVEAL, PacingIntent.FAST,
        35.0, "HIGH", (EvidenceUse.REVEAL, EvidenceUse.CHRONICLE)),
    NarrativeBeat.RISING_ACTION: BeatProfile(
        NarrativeBeat.RISING_ACTION, SegmentPurpose.ESCALATE, Emotion.SUSPENSE,
        TensionLevel.MEDIUM, NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE,
        PacingIntent.MODERATE, 45.0, "NORMAL", (EvidenceUse.SUPPORT, EvidenceUse.CORROBORATE)),
    NarrativeBeat.INVESTIGATION: BeatProfile(
        NarrativeBeat.INVESTIGATION, SegmentPurpose.INVESTIGATE, Emotion.CURIOSITY,
        TensionLevel.MEDIUM, NarrationMode.NARRATOR, NarrationIntent.QUESTION,
        PacingIntent.MODERATE, 55.0, "NORMAL", (EvidenceUse.SUPPORT, EvidenceUse.LOCATE)),
    NarrativeBeat.CLUE: BeatProfile(
        NarrativeBeat.CLUE, SegmentPurpose.INVESTIGATE, Emotion.SUSPENSE, TensionLevel.MEDIUM,
        NarrationMode.NARRATOR, NarrationIntent.EMPHASIZE, PacingIntent.MODERATE, 30.0, "HIGH",
        (EvidenceUse.REVEAL, EvidenceUse.CORROBORATE)),
    NarrativeBeat.COMPLICATION: BeatProfile(
        NarrativeBeat.COMPLICATION, SegmentPurpose.COMPLICATE, Emotion.UNEASE,
        TensionLevel.HIGH, NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE,
        PacingIntent.MODERATE, 40.0, "NORMAL", (EvidenceUse.CONTRAST, EvidenceUse.SUPPORT)),
    NarrativeBeat.MIDPOINT: BeatProfile(
        NarrativeBeat.MIDPOINT, SegmentPurpose.REVEAL, Emotion.TENSION, TensionLevel.HIGH,
        NarrationMode.NARRATOR, NarrationIntent.REVEAL, PacingIntent.MODERATE, 40.0, "HIGH",
        (EvidenceUse.REVEAL, EvidenceUse.CONTRAST)),
    NarrativeBeat.RED_HERRING: BeatProfile(
        NarrativeBeat.RED_HERRING, SegmentPurpose.COMPLICATE, Emotion.UNEASE,
        TensionLevel.MEDIUM, NarrationMode.NARRATOR, NarrationIntent.QUESTION,
        PacingIntent.MODERATE, 35.0, "NORMAL", (EvidenceUse.CONTRAST,)),
    NarrativeBeat.TURNING_POINT: BeatProfile(
        NarrativeBeat.TURNING_POINT, SegmentPurpose.CONFRONT, Emotion.TENSION,
        TensionLevel.HIGH, NarrationMode.NARRATOR, NarrationIntent.REVEAL, PacingIntent.FAST,
        30.0, "HIGH", (EvidenceUse.REVEAL, EvidenceUse.CONTRAST)),
    NarrativeBeat.REVELATION: BeatProfile(
        NarrativeBeat.REVELATION, SegmentPurpose.REVEAL, Emotion.SHOCK, TensionLevel.PEAK,
        NarrationMode.SILENCE, NarrationIntent.LET_BREATHE, PacingIntent.HOLD, 25.0, "HIGH",
        (EvidenceUse.REVEAL, EvidenceUse.CORROBORATE)),
    NarrativeBeat.CLIMAX: BeatProfile(
        NarrativeBeat.CLIMAX, SegmentPurpose.CONFRONT, Emotion.DREAD, TensionLevel.PEAK,
        NarrationMode.NARRATOR, NarrationIntent.EMPHASIZE, PacingIntent.FAST, 35.0, "HIGH",
        (EvidenceUse.REVEAL, EvidenceUse.CONTRAST)),
    NarrativeBeat.FALLING_ACTION: BeatProfile(
        NarrativeBeat.FALLING_ACTION, SegmentPurpose.RELEASE, Emotion.MELANCHOLY,
        TensionLevel.MEDIUM, NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE,
        PacingIntent.SLOW, 40.0, "NORMAL", (EvidenceUse.SUPPORT, EvidenceUse.CHRONICLE)),
    NarrativeBeat.AFTERMATH: BeatProfile(
        NarrativeBeat.AFTERMATH, SegmentPurpose.REFLECT, Emotion.GRIEF, TensionLevel.LOW,
        NarrationMode.NARRATOR, NarrationIntent.WITNESS, PacingIntent.SLOW, 45.0, "NORMAL",
        (EvidenceUse.CHRONICLE, EvidenceUse.ILLUSTRATE)),
    NarrativeBeat.RESOLUTION: BeatProfile(
        NarrativeBeat.RESOLUTION, SegmentPurpose.CLOSE, Emotion.RELIEF, TensionLevel.LOW,
        NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE, PacingIntent.SLOW, 40.0,
        "NORMAL", (EvidenceUse.CHRONICLE,)),
    NarrativeBeat.REFLECTION: BeatProfile(
        NarrativeBeat.REFLECTION, SegmentPurpose.REFLECT, Emotion.MELANCHOLY,
        TensionLevel.LOW, NarrationMode.NARRATOR, NarrationIntent.WITNESS, PacingIntent.SLOW,
        40.0, "NORMAL", (EvidenceUse.ILLUSTRATE,)),
    NarrativeBeat.OPEN_QUESTION: BeatProfile(
        NarrativeBeat.OPEN_QUESTION, SegmentPurpose.POSE_QUESTION, Emotion.UNEASE,
        TensionLevel.MEDIUM, NarrationMode.SILENCE, NarrationIntent.QUESTION,
        PacingIntent.HOLD, 25.0, "HIGH", (EvidenceUse.REVEAL,)),
    # Viaje del héroe / biografía
    NarrativeBeat.CALL_TO_ADVENTURE: BeatProfile(
        NarrativeBeat.CALL_TO_ADVENTURE, SegmentPurpose.PRESENT_INCIDENT, Emotion.HOPE,
        TensionLevel.MEDIUM, NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE,
        PacingIntent.MODERATE, 40.0, "NORMAL", (EvidenceUse.INTRODUCE,)),
    NarrativeBeat.THRESHOLD: BeatProfile(
        NarrativeBeat.THRESHOLD, SegmentPurpose.ESCALATE, Emotion.SUSPENSE, TensionLevel.MEDIUM,
        NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE, PacingIntent.MODERATE, 40.0,
        "NORMAL", (EvidenceUse.SUPPORT,)),
    NarrativeBeat.ORDEAL: BeatProfile(
        NarrativeBeat.ORDEAL, SegmentPurpose.CONFRONT, Emotion.FEAR, TensionLevel.HIGH,
        NarrationMode.NARRATOR, NarrationIntent.EMPHASIZE, PacingIntent.FAST, 40.0, "HIGH",
        (EvidenceUse.SUPPORT, EvidenceUse.CONTRAST)),
    NarrativeBeat.REWARD: BeatProfile(
        NarrativeBeat.REWARD, SegmentPurpose.RELEASE, Emotion.RELIEF, TensionLevel.LOW,
        NarrationMode.NARRATOR, NarrationIntent.WITNESS, PacingIntent.SLOW, 35.0, "NORMAL",
        (EvidenceUse.ILLUSTRATE,)),
    NarrativeBeat.RETURN: BeatProfile(
        NarrativeBeat.RETURN, SegmentPurpose.CLOSE, Emotion.HOPE, TensionLevel.LOW,
        NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE, PacingIntent.SLOW, 40.0,
        "NORMAL", (EvidenceUse.CHRONICLE,)),
}


def beat_profile(beat: str) -> BeatProfile:
    """Devuelve el perfil canónico de un beat. Beats desconocidos caen a un perfil neutro."""
    if beat in _CATALOG:
        return _CATALOG[beat]
    return BeatProfile(beat, SegmentPurpose.BUILD_CONTEXT, Emotion.NEUTRAL, TensionLevel.LOW,
                       NarrationMode.NARRATOR, NarrationIntent.CONTEXTUALIZE,
                       PacingIntent.MODERATE, 40.0)


def all_profiles() -> dict:
    return dict(_CATALOG)
