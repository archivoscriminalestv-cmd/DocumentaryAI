"""Planner — puerto del planificador de investigación (Sprint C-01).

El sistema depende de esta interfaz, no de una implementación concreta. Hoy
existe ``DeterministicPlanner`` (sin LLM); más adelante un planificador por IA
implementará el mismo puerto usando la abstracción ``LLMProvider`` ya existente,
sin que el resto del sistema cambie (ARCH-0002 AP-006).
"""

from typing import Protocol

from app.domain.research_plan import ResearchPlan


class Planner(Protocol):
    def create_plan(self, topic: str) -> ResearchPlan: ...
