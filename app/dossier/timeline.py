"""Timeline Builder — ordena cronológicamente los eventos del EvidenceGraph.

Motor independiente. Convierte cada ``Event`` del grafo en un ``TimelineEvent`` con su
procedencia y los ordena por fecha. NO resuelve conflictos de fechas: si dos eventos
discrepan, se conservan ambos (la detección la hace el Conflict Engine).
"""

from app.dossier.models import TimelineEvent


def _date_key(date: str) -> tuple:
    """Clave de orden: fechas conocidas primero (ascendente), desconocidas al final."""
    normalized = (date or "").strip()
    return (1, "") if not normalized else (0, normalized)


class TimelineBuilder:
    def build(self, graph) -> list[TimelineEvent]:
        events: list[TimelineEvent] = []
        for event in graph.events:
            src = event.sources[0] if event.sources else None
            events.append(TimelineEvent(
                id=event.id,
                date=event.date,
                time=str(event.__dict__.get("time", "")),  # reservado si el grafo lo trae
                description=event.description,
                location_id=event.location_id,
                entity_ids=list(event.entity_ids),
                confidence=event.confidence,
                provider=getattr(src, "provider", "") if src else "",
                source_url=getattr(src, "url", "") if src else "",
                license=getattr(src, "license", "") if src else "",
            ))
        # orden determinista: por fecha, luego por id (sin fusionar eventos en conflicto)
        events.sort(key=lambda e: (_date_key(e.date), e.id))
        return events
