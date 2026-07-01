"""Narrative — guion documental derivado del Knowledge de una Research.

Es la primera capa de "producción" del pipeline: transforma el conocimiento
(hechos sostenidos por evidencia) en un guion narrado y segmentado, apto para
ser convertido en voz e imágenes.

Provenance (ARCH-0002 AP-004): cada ``NarrativeSegment`` conserva los
``fact_ids`` de los que procede, de modo que toda afirmación narrada sigue
siendo trazable hasta su evidencia y su fuente.
"""

from dataclasses import dataclass, field


@dataclass
class NarrativeSegment:
    """Un fragmento narrable del guion (escena)."""

    id: str
    kind: str  # "intro" | "body" | "outro"
    text: str
    fact_ids: list[str] = field(default_factory=list)


@dataclass
class Narrative:
    id: str
    research_id: str
    knowledge_id: str
    title: str
    segments: list[NarrativeSegment] = field(default_factory=list)

    @property
    def script(self) -> str:
        """Guion completo concatenando los segmentos en orden."""
        return "\n\n".join(segment.text for segment in self.segments)
