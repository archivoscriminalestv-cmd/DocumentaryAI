"""DeterministicPlanner — planificador de investigación sin IA (Sprint C-01).

Servicio de aplicación que implementa el puerto ``Planner``. Dado un tema,
compone un ``ResearchPlan`` estructurado de forma puramente determinista: misma
entrada -> misma salida, sin LLM, sin red, sin estado. Sirve como base y como
fallback del futuro planificador por IA.

Esto es SOLO planificación: no busca ni descubre fuentes; únicamente sugiere qué
buscar (``suggested_queries``, ``primary_sources``, ``secondary_sources``).
"""

from app.domain.research_plan import ResearchPlan


class DeterministicPlanner:
    def create_plan(self, topic: str) -> ResearchPlan:
        topic = (topic or "").strip()
        if not topic:
            raise ValueError("El tema (topic) no puede estar vacío.")

        return ResearchPlan(
            topic=topic,
            main_research_question=(
                f"What is the complete, evidence-based account of {topic}, "
                "and what do the available facts actually establish?"
            ),
            subtopics=[
                f"Background and origin of {topic}",
                f"Key events and turning points in {topic}",
                f"People and organizations involved in {topic}",
                f"Causes and contributing factors behind {topic}",
                f"Consequences and aftermath of {topic}",
                f"Open questions and unresolved aspects of {topic}",
            ],
            historical_context=[
                f"Historical background and conditions leading up to {topic}",
                f"Earlier related events or precedents relevant to {topic}",
            ],
            timeline=[
                f"Before: context and precursors preceding {topic}",
                f"During: the central events of {topic}",
                f"After: aftermath and ongoing developments related to {topic}",
            ],
            actors=[
                f"Primary individuals central to {topic}",
                f"Organizations, institutions or authorities involved in {topic}",
                f"Witnesses, affected parties and experts connected to {topic}",
            ],
            geographic_areas=[
                f"Primary location(s) where {topic} took place",
                f"Related regions and jurisdictions relevant to {topic}",
            ],
            scientific_concepts=[
                f"Technical or scientific principles needed to understand {topic}",
                f"Methods or data used to analyze {topic}",
            ],
            controversies=[
                f"Competing explanations or disputed claims about {topic}",
                f"Theories, speculation and points of disagreement around {topic}",
            ],
            primary_sources=[
                f"Official records, reports or filings about {topic}",
                f"Firsthand accounts, testimonies and interviews on {topic}",
                f"Original documents, transcripts or datasets for {topic}",
            ],
            secondary_sources=[
                f"Reputable news coverage of {topic}",
                f"Books and documentaries about {topic}",
                f"Academic analyses and expert commentary on {topic}",
            ],
            suggested_queries=[
                topic,
                f"{topic} explained",
                f"{topic} timeline",
                f"{topic} key people",
                f"{topic} causes",
                f"{topic} investigation report",
                f"{topic} controversy theories",
                f"{topic} aftermath consequences",
            ],
        )
