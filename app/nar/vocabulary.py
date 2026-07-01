"""Vocabulario narrativo del NAR — la GRAMÁTICA objetiva del motor (NAR-001).

Este módulo NO contiene lógica: define el conjunto cerrado de términos con los que el
Narrative Intelligence Engine piensa. Igual que un director documental dispone de un léxico
profesional (acto, gancho, revelación, tensión…), el NAR solo puede usar estos valores. No
hay texto libre, no hay prosa, no hay opiniones: solo símbolos objetivos y enumerables.

Convención del proyecto: clases con constantes string + tupla ``ALL`` (y ``RANK`` cuando el
orden importa). Sin Enum para mantener serialización trivial y determinista.
"""


class StructureType:
    """Estructuras narrativas REALES (no inventadas). Cada una es una estrategia independiente."""

    LINEAR = "LINEAR"
    THREE_ACT = "THREE_ACT"
    FIVE_ACT = "FIVE_ACT"
    HERO_JOURNEY = "HERO_JOURNEY"
    MYSTERY_INVESTIGATION = "MYSTERY_INVESTIGATION"
    INVESTIGATION_DRIVEN = "INVESTIGATION_DRIVEN"
    EVIDENCE_DRIVEN = "EVIDENCE_DRIVEN"
    INTERVIEW_DRIVEN = "INTERVIEW_DRIVEN"
    REVERSE_CHRONOLOGY = "REVERSE_CHRONOLOGY"
    NON_LINEAR = "NON_LINEAR"
    ALL = (LINEAR, THREE_ACT, FIVE_ACT, HERO_JOURNEY, MYSTERY_INVESTIGATION,
           INVESTIGATION_DRIVEN, EVIDENCE_DRIVEN, INTERVIEW_DRIVEN, REVERSE_CHRONOLOGY,
           NON_LINEAR)


class DeviceType:
    """Dispositivos narrativos: técnicas que se aplican SOBRE una estructura (composables)."""

    COLD_OPEN = "COLD_OPEN"
    FLASHBACK = "FLASHBACK"
    FLASHFORWARD = "FLASHFORWARD"
    DOCUMENTARY_REVEAL = "DOCUMENTARY_REVEAL"
    PARALLEL_NARRATIVES = "PARALLEL_NARRATIVES"
    ALL = (COLD_OPEN, FLASHBACK, FLASHFORWARD, DOCUMENTARY_REVEAL, PARALLEL_NARRATIVES)


class NarrativeBeat:
    """Funciones narrativas atómicas (los "ladrillos" que ordenan las estructuras)."""

    HOOK = "HOOK"
    SETUP = "SETUP"
    INTRODUCE_SUBJECT = "INTRODUCE_SUBJECT"
    BACKGROUND = "BACKGROUND"
    INCITING_INCIDENT = "INCITING_INCIDENT"
    RISING_ACTION = "RISING_ACTION"
    INVESTIGATION = "INVESTIGATION"
    CLUE = "CLUE"
    COMPLICATION = "COMPLICATION"
    MIDPOINT = "MIDPOINT"
    RED_HERRING = "RED_HERRING"
    TURNING_POINT = "TURNING_POINT"
    REVELATION = "REVELATION"
    CLIMAX = "CLIMAX"
    FALLING_ACTION = "FALLING_ACTION"
    AFTERMATH = "AFTERMATH"
    RESOLUTION = "RESOLUTION"
    REFLECTION = "REFLECTION"
    OPEN_QUESTION = "OPEN_QUESTION"
    # Beats propios del viaje del héroe / biografía
    CALL_TO_ADVENTURE = "CALL_TO_ADVENTURE"
    THRESHOLD = "THRESHOLD"
    ORDEAL = "ORDEAL"
    REWARD = "REWARD"
    RETURN = "RETURN"
    ALL = (HOOK, SETUP, INTRODUCE_SUBJECT, BACKGROUND, INCITING_INCIDENT, RISING_ACTION,
           INVESTIGATION, CLUE, COMPLICATION, MIDPOINT, RED_HERRING, TURNING_POINT,
           REVELATION, CLIMAX, FALLING_ACTION, AFTERMATH, RESOLUTION, REFLECTION,
           OPEN_QUESTION, CALL_TO_ADVENTURE, THRESHOLD, ORDEAL, REWARD, RETURN)


class SegmentPurpose:
    """El PROPÓSITO objetivo de un segmento (qué hace, no qué dice)."""

    ESTABLISH = "ESTABLISH"
    INTRODUCE = "INTRODUCE"
    PRESENT_INCIDENT = "PRESENT_INCIDENT"
    BUILD_CONTEXT = "BUILD_CONTEXT"
    INVESTIGATE = "INVESTIGATE"
    REVEAL = "REVEAL"
    COMPLICATE = "COMPLICATE"
    CONFRONT = "CONFRONT"
    ESCALATE = "ESCALATE"
    RELEASE = "RELEASE"
    REFLECT = "REFLECT"
    POSE_QUESTION = "POSE_QUESTION"
    CLOSE = "CLOSE"
    ALL = (ESTABLISH, INTRODUCE, PRESENT_INCIDENT, BUILD_CONTEXT, INVESTIGATE, REVEAL,
           COMPLICATE, CONFRONT, ESCALATE, RELEASE, REFLECT, POSE_QUESTION, CLOSE)


class Emotion:
    """Paleta emocional objetiva (estado emocional que el segmento busca provocar)."""

    NEUTRAL = "NEUTRAL"
    CURIOSITY = "CURIOSITY"
    UNEASE = "UNEASE"
    SUSPENSE = "SUSPENSE"
    TENSION = "TENSION"
    DREAD = "DREAD"
    SHOCK = "SHOCK"
    FEAR = "FEAR"
    GRIEF = "GRIEF"
    MELANCHOLY = "MELANCHOLY"
    EMPATHY = "EMPATHY"
    ANGER = "ANGER"
    HOPE = "HOPE"
    RELIEF = "RELIEF"
    AWE = "AWE"
    ALL = (NEUTRAL, CURIOSITY, UNEASE, SUSPENSE, TENSION, DREAD, SHOCK, FEAR, GRIEF,
           MELANCHOLY, EMPATHY, ANGER, HOPE, RELIEF, AWE)


class TensionLevel:
    """Nivel de tensión dramática. RANK permite medir picos y curvas objetivamente."""

    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    PEAK = "PEAK"
    RANK = {NONE: 0, LOW: 1, MEDIUM: 2, HIGH: 3, PEAK: 4}
    ALL = (NONE, LOW, MEDIUM, HIGH, PEAK)

    @classmethod
    def from_rank(cls, rank: int) -> str:
        rank = max(0, min(4, int(rank)))
        for name, value in cls.RANK.items():
            if value == rank:
                return name
        return cls.NONE


class EvidenceUse:
    """Por QUÉ aparece una evidencia en un segmento (su función narrativa, no su contenido)."""

    ESTABLISH = "ESTABLISH"          # situar (lugar, contexto)
    INTRODUCE = "INTRODUCE"          # presentar a una persona/sujeto
    SUPPORT = "SUPPORT"              # respaldar una afirmación
    REVEAL = "REVEAL"               # mostrar algo nuevo y decisivo
    CONTRAST = "CONTRAST"            # confrontar versiones (conflictos)
    CORROBORATE = "CORROBORATE"      # confirmar con una segunda fuente
    LOCATE = "LOCATE"               # ubicar geográficamente (mapas)
    CHRONICLE = "CHRONICLE"          # ordenar en el tiempo (timeline)
    ILLUSTRATE = "ILLUSTRATE"        # acompañar visualmente
    ALL = (ESTABLISH, INTRODUCE, SUPPORT, REVEAL, CONTRAST, CORROBORATE, LOCATE,
           CHRONICLE, ILLUSTRATE)


class NarrationMode:
    """Cómo se sostiene el segmento en lo sonoro/verbal (NAR decide el MODO, nunca el texto)."""

    NARRATOR = "NARRATOR"
    INTERVIEW = "INTERVIEW"
    AMBIENT = "AMBIENT"
    SILENCE = "SILENCE"
    TEXT_ON_SCREEN = "TEXT_ON_SCREEN"
    ALL = (NARRATOR, INTERVIEW, AMBIENT, SILENCE, TEXT_ON_SCREEN)


class NarrationIntent:
    """La INTENCIÓN de la narración (por qué se habla o se calla)."""

    CONTEXTUALIZE = "CONTEXTUALIZE"
    REVEAL = "REVEAL"
    QUESTION = "QUESTION"
    WITNESS = "WITNESS"
    LET_BREATHE = "LET_BREATHE"   # silencio deliberado
    EMPHASIZE = "EMPHASIZE"
    ALL = (CONTEXTUALIZE, REVEAL, QUESTION, WITNESS, LET_BREATHE, EMPHASIZE)


class QuestionType:
    """Tipo de pregunta abierta para el espectador (estructurada, NO una frase escrita)."""

    WHO = "WHO"
    WHAT = "WHAT"
    WHERE = "WHERE"
    WHEN = "WHEN"
    WHY = "WHY"
    HOW = "HOW"
    WHETHER = "WHETHER"
    ALL = (WHO, WHAT, WHERE, WHEN, WHY, HOW, WHETHER)


class ArcType:
    """Forma global de la curva emocional/tensión del documental."""

    STEADY_BUILD = "STEADY_BUILD"        # subida sostenida hasta el clímax
    RISE_FALL = "RISE_FALL"              # sube y se resuelve
    FALL_RISE = "FALL_RISE"              # arranca grave, encuentra esperanza
    OSCILLATING = "OSCILLATING"          # sube/baja (investigación con giros)
    TRAGIC = "TRAGIC"                    # desciende sin alivio
    FLAT = "FLAT"                        # informativo, sin gran arco
    ALL = (STEADY_BUILD, RISE_FALL, FALL_RISE, OSCILLATING, TRAGIC, FLAT)


class PacingIntent:
    """Intención de ritmo del segmento (NAR sugiere; VIS/Composer ejecutan los cortes)."""

    HOLD = "HOLD"            # sostener, dejar respirar
    SLOW = "SLOW"
    MODERATE = "MODERATE"
    FAST = "FAST"
    ACCELERATE = "ACCELERATE"
    ALL = (HOLD, SLOW, MODERATE, FAST, ACCELERATE)


class MechanismKind:
    """Mecanismos de suspense/estructura que se colocan a lo largo del blueprint."""

    HOOK = "HOOK"
    FORESHADOW = "FORESHADOW"
    REVEAL = "REVEAL"
    CLIFFHANGER = "CLIFFHANGER"
    PAYOFF = "PAYOFF"
    ALL = (HOOK, FORESHADOW, REVEAL, CLIFFHANGER, PAYOFF)


class TimelineOrder:
    """Decisión de ordenación temporal del relato."""

    CHRONOLOGICAL = "CHRONOLOGICAL"
    REVERSE = "REVERSE"
    NON_LINEAR = "NON_LINEAR"
    THEMATIC = "THEMATIC"
    ALL = (CHRONOLOGICAL, REVERSE, NON_LINEAR, THEMATIC)


# Valor reservado: el NAR nunca inventa. Cuando no hay base objetiva, marca UNKNOWN.
UNKNOWN = "UNKNOWN"
