"""Visual Intelligence System (slice de integración real).

VIS-1 (`build_visual_plan`): CinematicProfile (RDA) + Scene -> VisualPlan.
VIS-2 (`compile_execution`): VisualPlan -> ExecutionPlan (requests al MGL).
"""

from app.vis.executor import compile_execution
from app.vis.models import ExecutionPlan, PlannedShot, ShotRequest, VisualPlan
from app.vis.planner import build_visual_plan

__all__ = [
    "build_visual_plan",
    "compile_execution",
    "VisualPlan",
    "PlannedShot",
    "ExecutionPlan",
    "ShotRequest",
]
