"""Modelos mínimos REALES del VIS (slice de integración).

Implementación deliberadamente compacta de los contratos de ARCH-VIS-002/003,
suficiente para conectar RDA → VIS-1 → VIS-2 → MGL de extremo a extremo. Puras
dataclasses, JSON-serializables.
"""

from dataclasses import dataclass, field


@dataclass
class PlannedShot:                 # salida de VIS-1
    id: str
    scene_id: str
    index: int
    shot_type: str
    camera_move: str
    camera_intensity: float
    lighting: str
    duration: float
    asset_type: str                # "image" | "video"
    reuse_key: str = ""            # "" => único; no vacío => motivo reutilizable
    fact_ids: list[str] = field(default_factory=list)


@dataclass
class VisualPlan:                  # salida de VIS-1 (por escena)
    scene_id: str
    style: str
    reference: str                 # qué CinematicProfile (RDA) lo originó
    pacing_tier: str
    movement_tendency: str
    lighting_tendency: str
    grade: str
    shots: list[PlannedShot] = field(default_factory=list)

    @property
    def total_duration(self) -> float:
        return round(sum(s.duration for s in self.shots), 2)


@dataclass
class ShotRequest:                 # contrato con el MGL (VIS-2 → MGL)
    shot_id: str
    scene_id: str
    media_type: str
    prompt: str
    negative_prompt: str
    reuse_key: str
    variation_seed: int
    motion: dict
    lens: str
    angle: str
    composition: str
    fingerprint: str


@dataclass
class ExecutionPlan:              # salida de VIS-2
    scene_id: str
    requests: list[ShotRequest] = field(default_factory=list)
