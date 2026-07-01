"""Puertos (interfaces) de persistencia del primer vertical.

Definidos como Protocols para invertir la dependencia: el núcleo declara qué
necesita; la infraestructura lo implementa (ARCH-0002 AP-006: las capacidades
perduran, las implementaciones evolucionan). El dominio/aplicación nunca
depende de una implementación concreta.
"""

from typing import Protocol

from app.domain.claim import Claim
from app.domain.evidence import Evidence
from app.domain.fact import Fact
from app.domain.knowledge import Knowledge
from app.domain.narrative import Narrative
from app.domain.research import Research
from app.domain.source import Source
from app.domain.workspace import Workspace


class WorkspaceRepository(Protocol):
    def add(self, workspace: Workspace) -> None: ...
    def get(self, workspace_id: str) -> Workspace | None: ...


class ResearchRepository(Protocol):
    def add(self, research: Research) -> None: ...
    def get(self, research_id: str) -> Research | None: ...


class SourceRepository(Protocol):
    def add(self, source: Source) -> None: ...
    def get(self, source_id: str) -> Source | None: ...
    def list_by_research(self, research_id: str) -> list[Source]: ...


class EvidenceRepository(Protocol):
    def add(self, evidence: Evidence) -> None: ...
    def list_by_research(self, research_id: str) -> list[Evidence]: ...


class FactRepository(Protocol):
    def add(self, fact: Fact) -> None: ...
    def list_by_evidence_ids(self, evidence_ids: list[str]) -> list[Fact]: ...
    def list_by_ids(self, fact_ids: list[str]) -> list[Fact]: ...


class ClaimRepository(Protocol):
    def add(self, claim: Claim) -> None: ...
    def list_by_research(self, research_id: str) -> list[Claim]: ...


class KnowledgeRepository(Protocol):
    def add(self, knowledge: Knowledge) -> None: ...
    def list_by_research(self, research_id: str) -> list[Knowledge]: ...


class NarrativeRepository(Protocol):
    def add(self, narrative: Narrative) -> None: ...
    def get(self, narrative_id: str) -> Narrative | None: ...
    def list_by_research(self, research_id: str) -> list[Narrative]: ...


class SpeechSynthesizer(Protocol):
    """Convierte texto en un fichero de audio (seam para TTS local o por IA)."""

    def synthesize(self, text: str, out_path: str) -> bool:
        """Escribe el audio de ``text`` en ``out_path``.

        Devuelve True si generó audio real; False si no fue posible (el caller
        decide cómo degradar sin romper el pipeline).
        """
        ...


class ImageRenderer(Protocol):
    """Genera una imagen para una escena (seam para render local o por IA)."""

    def render(self, text: str, out_path: str, *, subtitle: str = "") -> bool:
        """Escribe una imagen en ``out_path``. Devuelve True si tuvo éxito."""
        ...


class VideoComposer(Protocol):
    """Ensambla clips YA NORMALIZADOS en un único vídeo (no normaliza nada)."""

    def compose(
        self,
        clips: list[str],
        out_path: str,
        intro_clip: str | None = None,
    ) -> None:
        """Escribe el vídeo en ``out_path``. FAIL-FAST: lanza excepción si falla.

        ``clips`` son rutas a clips ya normalizados (MediaNormalizer). ``intro_clip``
        (opcional) es un clip de intro normalizado que se funde con ``clips[0]``.
        """
        ...
