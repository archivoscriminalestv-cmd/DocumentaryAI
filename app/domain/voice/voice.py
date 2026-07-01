"""Voice — locución generada a partir de la Narrative.

Segunda capa de producción: cada escena del guion se convierte en un clip de
audio. ``Voiceover`` agrupa los clips de una Narrative conservando el
``segment_id`` de origen (trazabilidad guion → audio).
"""

from dataclasses import dataclass, field


@dataclass
class VoiceClip:
    segment_id: str
    kind: str  # intro | body | outro (heredado del segmento)
    audio_path: str
    synthesized: bool  # True si hay audio real; False si solo texto (degradación)


@dataclass
class Voiceover:
    id: str
    narrative_id: str
    clips: list[VoiceClip] = field(default_factory=list)

    @property
    def audio_paths(self) -> list[str]:
        return [clip.audio_path for clip in self.clips]
