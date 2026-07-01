"""Interfaces (Protocols) del NAR — los contratos internos del motor (NAR-001).

Cada responsabilidad narrativa es un Protocol independiente para que pueda evolucionar sola
y para que añadir una estructura/dispositivo/diseñador NO obligue a tocar el orquestador.
Esta es la base de que el NAR sea "el cerebro narrativo durante años": todo es enchufable.
"""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from app.nar.models import (
    EmotionCurve,
    EvidencePlacement,
    NarrativeContext,
    NarrativeSegment,
    NarrativeState,
    RecreationPlacement,
    ViewerQuestion,
)


@dataclass
class BeatPlan:
    """Producto intermedio de una estructura: un beat asignado a un acto (sin más lógica)."""

    beat: str
    act_key: str
    act_index: int = 0
    emphasis: str = ""                 # override opcional; "" = usar el del catálogo
    purpose: str = ""                  # override opcional


@runtime_checkable
class NarrativeStructure(Protocol):
    """Una estructura narrativa real. Se auto-puntúa y propone su esqueleto de beats."""

    structure_type: str

    def fitness(self, context: NarrativeContext) -> tuple[float, list[str]]:
        """Idoneidad objetiva [0..1] para este caso + razones (trazables). Sin opinión."""
        ...

    def build_skeleton(self, context: NarrativeContext) -> list[BeatPlan]:
        """Orden de beats agrupados en actos. NO asigna emoción/evidencias (eso es de los diseñadores)."""
        ...


@runtime_checkable
class NarrativeDevice(Protocol):
    """Técnica composable que se aplica SOBRE el esqueleto (cold open, flashback…)."""

    device_type: str

    def applies(self, context: NarrativeContext,
                segments: list[NarrativeSegment]) -> tuple[bool, str]:
        ...

    def apply(self, context: NarrativeContext,
              segments: list[NarrativeSegment]) -> list[NarrativeSegment]:
        """Devuelve la lista de segmentos (posiblemente reordenada/anotada). Determinista."""
        ...


@runtime_checkable
class EmotionDesigner(Protocol):
    """Asigna emoción/tensión a cada segmento y construye la curva emocional global."""

    def design(self, context: NarrativeContext,
               segments: list[NarrativeSegment]) -> EmotionCurve:
        ...


@runtime_checkable
class EvidencePlacer(Protocol):
    """Decide qué material aparece en un segmento y por qué (evidencia real prioritaria)."""

    def place(self, context: NarrativeContext, segment: NarrativeSegment
              ) -> tuple[list[EvidencePlacement], list[RecreationPlacement], list[ViewerQuestion]]:
        ...


@runtime_checkable
class PacingDesigner(Protocol):
    """Decide la duración sugerida y la intención de ritmo de un segmento."""

    def plan(self, context: NarrativeContext,
             segment: NarrativeSegment) -> tuple[float, str, str]:
        """Devuelve (suggested_duration_seconds, basis, pacing_intent)."""
        ...


@runtime_checkable
class RevealScheduler(Protocol):
    """Programa mecanismos (hook/foreshadow/reveal/cliffhanger/payoff), preguntas y estados."""

    def schedule(self, context: NarrativeContext,
                 segments: list[NarrativeSegment]) -> "ScheduleResult":
        ...


@dataclass
class ScheduleResult:
    """Resultado del RevealScheduler (agrupado para no acoplar el orquestador a su detalle)."""

    hooks: list = field(default_factory=list)
    foreshadows: list = field(default_factory=list)
    reveals: list = field(default_factory=list)
    cliffhangers: list = field(default_factory=list)
    payoffs: list = field(default_factory=list)
    viewer_questions: list[ViewerQuestion] = field(default_factory=list)
    narrative_states: list[NarrativeState] = field(default_factory=list)
