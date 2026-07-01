"""ResearchPlan — plan de investigación estructurado para un tema (Sprint C-01).

Primera etapa de la Fase C: dado un Topic, el sistema produce un plan ANTES de
buscar fuentes. Es un dataclass puro (sin lógica), serializable a JSON con
``dataclasses.asdict`` + ``json.dumps``. No representa fuentes ni evidencias:
solo la estrategia de investigación.
"""

from dataclasses import dataclass, field


@dataclass
class ResearchPlan:
    topic: str
    main_research_question: str = ""
    subtopics: list[str] = field(default_factory=list)
    historical_context: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    actors: list[str] = field(default_factory=list)
    geographic_areas: list[str] = field(default_factory=list)
    scientific_concepts: list[str] = field(default_factory=list)
    controversies: list[str] = field(default_factory=list)
    primary_sources: list[str] = field(default_factory=list)
    secondary_sources: list[str] = field(default_factory=list)
    suggested_queries: list[str] = field(default_factory=list)
