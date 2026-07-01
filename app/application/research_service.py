"""ResearchService: use cases for the first functional vertical."""

from uuid import uuid4

from app.application.ports import (
    ClaimRepository,
    EvidenceRepository,
    FactRepository,
    KnowledgeRepository,
    ResearchRepository,
    SourceRepository,
    WorkspaceRepository,
)
from app.domain.evidence import Evidence
from app.domain.fact import Fact
from app.domain.knowledge import Knowledge
from app.domain.research import Research
from app.domain.source import Source
from app.domain.workspace import Workspace


def _new_id() -> str:
    return uuid4().hex[:12]


class ResearchService:
    def __init__(
        self,
        workspaces: WorkspaceRepository,
        researches: ResearchRepository,
        sources: SourceRepository,
        evidences: EvidenceRepository,
        facts: FactRepository,
        claims: ClaimRepository,
        knowledge: KnowledgeRepository,
    ) -> None:
        self._workspaces = workspaces
        self._researches = researches
        self._sources = sources
        self._evidences = evidences
        self._facts = facts
        self._claims = claims
        self._knowledge = knowledge

    def create_workspace(self, name: str) -> Workspace:
        workspace = Workspace(id=_new_id(), name=name)
        self._workspaces.add(workspace)
        return workspace

    def create_research(self, title: str, workspace_id: str | None = None) -> Research:
        research = Research(id=_new_id(), title=title, workspace_id=workspace_id)
        self._researches.add(research)
        if workspace_id is not None:
            workspace = self._workspaces.get(workspace_id)
            if workspace is not None:
                workspace.add_research(research.id)
        return research

    def register_source(
        self, research_id: str, reference: str, content: str
    ) -> Source:
        source = Source(
            id=_new_id(),
            research_id=research_id,
            reference=reference,
            content=content,
        )
        self._sources.add(source)
        return source

    def analyze_source(self, source_id: str) -> list[str]:
        source = self._sources.get(source_id)
        if source is None:
            return []
        return [line.strip() for line in source.content.splitlines() if line.strip()]

    def extract_evidence(self, source_id: str) -> list[Evidence]:
        source = self._sources.get(source_id)
        if source is None:
            return []
        observations = self.analyze_source(source_id)
        extracted: list[Evidence] = []
        for observation in observations:
            evidence = Evidence(
                id=_new_id(),
                research_id=source.research_id,
                source_id=source.id,
                content=observation,
            )
            self._evidences.add(evidence)
            extracted.append(evidence)
        return extracted

    def generate_knowledge(self, research_id: str) -> Knowledge:
        evidences = self._evidences.list_by_research(research_id)
        for evidence in evidences:
            fact = Fact(
                id=_new_id(),
                evidence_id=evidence.id,
                text=evidence.content,
            )
            self._facts.add(fact)

        facts = self._facts.list_by_evidence_ids([e.id for e in evidences])
        knowledge = Knowledge(
            id=_new_id(),
            research_id=research_id,
            content=(
                f"Conocimiento generado a partir de {len(facts)} hecho(s) "
                f"sostenido(s) por {len(evidences)} evidencia(s)."
            ),
            fact_ids=[fact.id for fact in facts],
        )
        self._knowledge.add(knowledge)
        return knowledge
