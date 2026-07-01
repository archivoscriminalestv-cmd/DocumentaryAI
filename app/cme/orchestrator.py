"""CinematicMotionEngine — fachada del CME (VSC → CME → Composer).

Recibe un plano (``CMEContext``: rol + estilo + sugerencia de cámara + duración +
asset_id) y devuelve un ``MotionShot`` con intención y parámetros físicos. Mantiene la
memoria del documental (para continuidad y diversidad) y la línea temporal. No genera
vídeo, no renderiza, no llama a FFmpeg ni a proveedores.
"""

import logging
from dataclasses import dataclass

from app.cme.continuity import assert_identity_safe
from app.cme.director import NarrativeMotionDirector
from app.cme.motion_catalog import CATALOG
from app.cme.models import MotionFingerprint, MotionShot
from app.cme.physics import compute_parameters
from app.cme.planner import MotionPlanner, diversity_against
from app.cme.timeline import MotionTimeline


@dataclass
class CMEContext:
    shot_id: str = ""
    scene_id: str = ""
    asset_id: str = ""
    documentary_style: str = ""
    shot_role: str = ""
    motion_hint: str = ""
    shot_duration: float = 0.0
    identity: str = ""
    character_name: str = ""


class CinematicMotionEngine:
    def __init__(self, *, window: int = 5, logger=None) -> None:
        self._director = NarrativeMotionDirector()
        self._planner = MotionPlanner(window=window)
        self.timeline = MotionTimeline()
        self._shots: list[MotionShot] = []
        self._window = window
        self._log = logger or logging.getLogger("cme")

    # --- interfaz de historial usada por el planner --------------------------
    @property
    def size(self) -> int:
        return len(self._shots)

    def recent_motion_types(self, n: int) -> list[str]:
        return [s.motion_type for s in self._shots[-n:]] if n > 0 else []

    def last_use_index(self, motion_type: str) -> int:
        for i in range(len(self._shots) - 1, -1, -1):
            if self._shots[i].motion_type == motion_type:
                return i
        return -1

    @property
    def shots(self) -> list[MotionShot]:
        return list(self._shots)

    # --- planificación -------------------------------------------------------

    def plan_shot(self, ctx: CMEContext) -> MotionShot:
        scene_class = self._director.scene_class(ctx.documentary_style)
        base, purpose = self._director.base_motion(ctx.documentary_style, ctx.shot_role, ctx.motion_hint)
        final, changes = self._planner.plan(base, scene_class, self)

        d = CATALOG[final]
        duration = ctx.shot_duration if ctx.shot_duration > 0 else d.base_duration
        params = compute_parameters(d.primary, d.direction, duration, d.easing, d.stability,
                                    amplitude=d.amplitude)
        assert_identity_safe(params)  # el movimiento nunca deforma al personaje

        fp = MotionFingerprint(
            motion_type=final, family=d.family, direction=d.direction, speed=params.speed,
            duration=round(duration, 3), ease=d.easing, camera_energy=d.energy,
            camera_stability=d.stability, narrative_purpose=purpose,
        )
        shot = MotionShot(
            shot_id=ctx.shot_id, scene_id=ctx.scene_id, asset_id=ctx.asset_id,
            motion_type=final, family=d.family, direction=d.direction, purpose=purpose,
            narrative_mode=scene_class, parameters=params, fingerprint=fp,
            duration=round(duration, 3),
            justification=[purpose] + [c["reason"] for c in changes],
        )
        self.timeline.add(shot)
        self._shots.append(shot)
        if changes:
            self._log.info("CME shot=%s -> %s (%d ajustes)", ctx.shot_id, final, len(changes))
        return shot

    def finalize(self) -> None:
        self.timeline.finalize()

    # --- métricas / salidas --------------------------------------------------

    def average_diversity(self) -> float:
        fps = [s.fingerprint for s in self._shots]
        if not fps:
            return 0.0
        total = sum(diversity_against(fp, fps[max(0, i - self._window):i])
                    for i, fp in enumerate(fps))
        return round(total / len(fps), 4)

    def distribution(self, attr: str) -> dict:
        out: dict = {}
        for s in self._shots:
            key = getattr(s, attr)
            out[key] = out.get(key, 0) + 1
        return out

    def stats(self) -> dict:
        shots = self._shots
        n = len(shots) or 1
        return {
            "total_shots": len(shots),
            "average_diversity": self.average_diversity(),
            "average_speed": round(sum(s.parameters.speed for s in shots) / n, 4),
            "average_duration": round(sum(s.duration for s in shots) / n, 3),
            "total_duration": self.timeline.total_duration,
            "cinematic_energy": round(sum(s.fingerprint.camera_energy for s in shots) / n, 4),
            "repetitions": sum(1 for s in shots if s.fingerprint and
                               self._is_repeat(s)),
            "by_motion_type": self.distribution("motion_type"),
            "by_family": self.distribution("family"),
            "by_direction": self.distribution("direction"),
        }

    def _is_repeat(self, shot: MotionShot) -> bool:
        idx = self._shots.index(shot)
        prev = [s.fingerprint for s in self._shots[max(0, idx - self._window):idx]]
        return diversity_against(shot.fingerprint, prev) < 0.5

    def manifest(self) -> list[dict]:
        return [{
            "shot": s.shot_id, "scene": s.scene_id, "asset_id": s.asset_id,
            "motion_type": s.motion_type, "speed": s.parameters.speed,
            "duration": s.duration, "curve": s.parameters.easing,
            "parameters": s.parameters.to_dict(), "purpose": s.purpose,
        } for s in self._shots]

    def history(self) -> list[dict]:
        return [s.to_dict() for s in self._shots]
