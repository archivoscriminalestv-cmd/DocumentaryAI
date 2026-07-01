"""Modelos del Composer."""

from dataclasses import asdict, dataclass, field
from typing import Any

from app.composer import SCHEMA_VERSION


@dataclass
class ClipResult:
    index: int
    shot_id: str
    scene_id: str
    asset_id: str
    motion_type: str
    duration: float
    transition_in: str
    transition_out: str
    clip_path: str
    filter_summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ComposerResult:
    project: str
    output_path: str
    schema_version: str = SCHEMA_VERSION
    clips: list[ClipResult] = field(default_factory=list)
    total_duration: float = 0.0
    audio_duration: float = 0.0
    video_duration: float = 0.0
    in_sync: bool = False
    fps: int = 25
    width: int = 1280
    height: int = 720
    bitrate: str = ""
    render_seconds: float = 0.0
    cache_hits: int = 0
    transitions_used: dict = field(default_factory=dict)
    motions_used: dict = field(default_factory=dict)
    assets_used: list[str] = field(default_factory=list)
    narration_provider: str = ""
    music_provider: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["clips"] = [c.to_dict() for c in self.clips]
        return data
