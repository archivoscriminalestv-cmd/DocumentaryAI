"""Repositorios en memoria que implementan los puertos de ``application.ports``.

Persistencia provisional para el primer vertical. No hay base de datos: los
objetos viven en diccionarios en memoria. Implementa los Protocols definidos
en el núcleo, de modo que éste no depende de este detalle (ARCH-0002 AP-006).
"""

from app.domain.claim import Claim
from app.domain.evidence import Evidence
from app.domain.fact import Fact
from app.domain.knowledge import Knowledge
from app.domain.narrative import Narrative
from app.domain.research import Research
from app.domain.source import Source
from app.domain.workspace import Workspace


class InMemoryWorkspaceRepository:
    def __init__(self) -> None:
        self._items: dict[str, Workspace] = {}

    def add(self, workspace: Workspace) -> None:
        self._items[workspace.id] = workspace

    def get(self, workspace_id: str) -> Workspace | None:
        return self._items.get(workspace_id)


class InMemoryResearchRepository:
    def __init__(self) -> None:
        self._items: dict[str, Research] = {}

    def add(self, research: Research) -> None:
        self._items[research.id] = research

    def get(self, research_id: str) -> Research | None:
        return self._items.get(research_id)


class InMemorySourceRepository:
    def __init__(self) -> None:
        self._items: dict[str, Source] = {}

    def add(self, source: Source) -> None:
        self._items[source.id] = source

    def get(self, source_id: str) -> Source | None:
        return self._items.get(source_id)

    def list_by_research(self, research_id: str) -> list[Source]:
        return [s for s in self._items.values() if s.research_id == research_id]


class InMemoryEvidenceRepository:
    def __init__(self) -> None:
        self._items: dict[str, Evidence] = {}

    def add(self, evidence: Evidence) -> None:
        self._items[evidence.id] = evidence

    def list_by_research(self, research_id: str) -> list[Evidence]:
        return [e for e in self._items.values() if e.research_id == research_id]


class InMemoryFactRepository:
    def __init__(self) -> None:
        self._items: dict[str, Fact] = {}

    def add(self, fact: Fact) -> None:
        self._items[fact.id] = fact

    def list_by_evidence_ids(self, evidence_ids: list[str]) -> list[Fact]:
        evidence_id_set = set(evidence_ids)
        return [f for f in self._items.values() if f.evidence_id in evidence_id_set]

    def list_by_ids(self, fact_ids: list[str]) -> list[Fact]:
        # Preserva el orden solicitado (importante para el guion narrativo).
        return [self._items[fid] for fid in fact_ids if fid in self._items]


class InMemoryClaimRepository:
    def __init__(self) -> None:
        self._items: dict[str, Claim] = {}

    def add(self, claim: Claim) -> None:
        self._items[claim.id] = claim

    def list_by_research(self, research_id: str) -> list[Claim]:
        return [c for c in self._items.values() if c.research_id == research_id]


class InMemoryKnowledgeRepository:
    def __init__(self) -> None:
        self._items: dict[str, Knowledge] = {}

    def add(self, knowledge: Knowledge) -> None:
        self._items[knowledge.id] = knowledge

    def list_by_research(self, research_id: str) -> list[Knowledge]:
        return [k for k in self._items.values() if k.research_id == research_id]


class InMemoryNarrativeRepository:
    def __init__(self) -> None:
        self._items: dict[str, Narrative] = {}

    def add(self, narrative: Narrative) -> None:
        self._items[narrative.id] = narrative

    def get(self, narrative_id: str) -> Narrative | None:
        return self._items.get(narrative_id)

    def list_by_research(self, research_id: str) -> list[Narrative]:
        return [n for n in self._items.values() if n.research_id == research_id]
