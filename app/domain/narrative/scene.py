"""Scene — unidad narrativa producida por el Narrative Engine (Sprint B-06).

Capa de storytelling: una Scene reorganiza y reformula hechos verificados en un
guion documental. Conserva ``fact_ids`` para mantener la trazabilidad estricta
hecho → escena (ARCH-0002 AP-004). Es independiente de ``NarrativeSegment``
(guion determinista previo); ambas coexisten — el Narrative Engine es aditivo.
"""

from dataclasses import dataclass, field


@dataclass
class Scene:
    id: str
    title: str
    narration: str
    fact_ids: list[str] = field(default_factory=list)
