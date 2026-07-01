"""ExecutorService — transforma un ResearchPlan en SearchTasks (Sprint C-02).

Orquestación pura de aplicación: entra ``ResearchPlan``, sale ``list[SearchTask]``.
Decide QUÉ buscar de forma determinista (misma entrada -> misma salida). NO
busca, NO accede a la red, NO usa IA. Cada tarea queda justificada (``reason``)
y priorizada (``priority``) a partir de los campos del plan.
"""

from app.domain.research_plan import ResearchPlan
from app.domain.search import SearchPriority, SearchTask, SearchType


def _first(items: list[str], fallback: str) -> str:
    return items[0] if items else fallback


class ExecutorService:
    def execute(self, plan: ResearchPlan) -> list[SearchTask]:
        topic = (plan.topic or "").strip()
        if not topic:
            raise ValueError("El ResearchPlan no tiene topic; no se pueden planificar búsquedas.")

        # (type, priority, query, reason) en orden determinista.
        specs: list[tuple[SearchType, SearchPriority, str, str]] = [
            (
                SearchType.WIKIPEDIA,
                SearchPriority.HIGH,
                topic,
                "Establish an encyclopedic overview and baseline facts before deeper research.",
            ),
            (
                SearchType.NEWS,
                SearchPriority.HIGH,
                f"{topic} news coverage",
                _first(plan.secondary_sources, "Reputable contemporary news coverage."),
            ),
            (
                SearchType.GOVERNMENT,
                SearchPriority.HIGH,
                f"{topic} official report",
                _first(plan.primary_sources, "Official records and primary documentation."),
            ),
            (
                SearchType.ACADEMIC,
                SearchPriority.MEDIUM,
                f"{topic} academic analysis",
                "Scholarly and peer-reviewed analysis of the topic.",
            ),
            (
                SearchType.SCIENTIFIC_PAPERS,
                SearchPriority.MEDIUM,
                f"{topic} scientific study",
                _first(plan.scientific_concepts, "Technical and scientific literature relevant to the topic."),
            ),
            (
                SearchType.BOOKS,
                SearchPriority.MEDIUM,
                f"{topic} book",
                "In-depth books and long-form treatments of the topic.",
            ),
            (
                SearchType.ARCHIVES,
                SearchPriority.MEDIUM,
                f"{topic} primary documents archive",
                "Firsthand accounts, transcripts and archival materials.",
            ),
            (
                SearchType.YOUTUBE,
                SearchPriority.LOW,
                f"{topic} documentary",
                "Existing video documentaries, footage and recorded testimony.",
            ),
        ]

        # Profundización por subtema: una tarea académica por cada subtema del plan.
        for subtopic in plan.subtopics:
            specs.append(
                (
                    SearchType.ACADEMIC,
                    SearchPriority.MEDIUM,
                    subtopic,
                    f"Investigate subtopic: {subtopic}.",
                )
            )

        tasks: list[SearchTask] = []
        for index, (search_type, priority, query, reason) in enumerate(specs, start=1):
            tasks.append(
                SearchTask(
                    id=f"task-{index:02d}",
                    type=search_type,
                    query=query,
                    priority=priority,
                    reason=reason,
                )
            )
        return tasks
