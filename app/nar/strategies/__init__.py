"""Registro de estructuras narrativas (NAR-001).

Añadir una estructura nueva = una clase más aquí. El selector la puntúa automáticamente; el
orquestador no cambia. Sin ``if`` gigantes en ningún sitio.
"""

from app.nar.strategies.base import BaseNarrativeStructure
from app.nar.strategies.evidence_driven import EvidenceDrivenStructure
from app.nar.strategies.five_act import FiveActStructure
from app.nar.strategies.hero_journey import HeroJourneyStructure
from app.nar.strategies.interview_driven import InterviewDrivenStructure
from app.nar.strategies.investigation_driven import InvestigationDrivenStructure
from app.nar.strategies.linear import LinearStructure
from app.nar.strategies.mystery_investigation import MysteryInvestigationStructure
from app.nar.strategies.non_linear import NonLinearStructure
from app.nar.strategies.reverse_chronology import ReverseChronologyStructure
from app.nar.strategies.three_act import ThreeActStructure


def default_structures() -> list[BaseNarrativeStructure]:
    """Todas las estructuras disponibles, en orden estable (desempate determinista)."""
    return [
        ThreeActStructure(),
        FiveActStructure(),
        LinearStructure(),
        MysteryInvestigationStructure(),
        InvestigationDrivenStructure(),
        EvidenceDrivenStructure(),
        InterviewDrivenStructure(),
        HeroJourneyStructure(),
        ReverseChronologyStructure(),
        NonLinearStructure(),
    ]


__all__ = [
    "default_structures",
    "BaseNarrativeStructure",
    "ThreeActStructure",
    "FiveActStructure",
    "LinearStructure",
    "MysteryInvestigationStructure",
    "InvestigationDrivenStructure",
    "EvidenceDrivenStructure",
    "InterviewDrivenStructure",
    "HeroJourneyStructure",
    "ReverseChronologyStructure",
    "NonLinearStructure",
]
