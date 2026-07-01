"""Visual — storyboard de imágenes derivado de la Narrative.

Tercera capa de producción: cada escena del guion recibe una imagen. El
``Storyboard`` agrupa las imágenes conservando el ``segment_id`` de origen
(trazabilidad guion → imagen).
"""

from dataclasses import dataclass, field


@dataclass
class VisualScene:
    segment_id: str
    kind: str  # intro | body | outro
    image_path: str
    rendered: bool  # True si se generó imagen real


@dataclass
class Storyboard:
    id: str
    narrative_id: str
    scenes: list[VisualScene] = field(default_factory=list)

    @property
    def image_paths(self) -> list[str]:
        return [scene.image_path for scene in self.scenes]
