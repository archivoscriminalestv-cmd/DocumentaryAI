"""Asset — registro de un activo de media generado (Fase 1 MGL).

``embedding`` es un placeholder: se reserva para la futura recuperación por
embeddings sin necesidad de refactor (la estructura ya lo contempla).
"""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Asset:
    asset_id: str
    type: str  # "image" | "video"
    prompt: str
    scene_id: str = ""
    provider: str = ""
    path: str = ""
    url: str = ""
    embedding: list[float] | None = None  # placeholder para embeddings futuros
    style_tags: list[str] = field(default_factory=list)
    timestamp: float = 0.0
    reuse_count: int = 0
    reused_scene_ids: list[str] = field(default_factory=list)  # escenas que lo reutilizan

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Asset":
        # Solo claves presentes -> las ausentes usan sus defaults (compatibilidad
        # con índices antiguos sin campos nuevos como ``reused_scene_ids``).
        known = {k: data[k] for k in cls.__dataclass_fields__ if k in data}
        return cls(**known)
