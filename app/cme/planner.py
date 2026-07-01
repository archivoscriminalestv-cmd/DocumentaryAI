"""MotionPlanner — elige el movimiento final de forma DETERMINISTA.

Parte del movimiento base del director, lo limita a la clase de la escena (continuidad)
y, si ese movimiento se repite en los últimos N planos, elige la alternativa MENOS
usada recientemente dentro de la familia compatible (diversidad). Sin ``random``.
"""

from app.cme.continuity import remap_to_scene_class
from app.cme.motion_catalog import CATALOG, CATALOG_ORDER, candidates_for
from app.cme.models import MotionFingerprint

# Peso de cada dimensión del fingerprint para la similitud (suma = 1.0).
_WEIGHTS = {"motion_type": 0.6, "direction": 0.25, "family": 0.15}


def motion_similarity(a: MotionFingerprint, b: MotionFingerprint) -> float:
    score = 0.0
    if a.motion_type == b.motion_type:
        score += _WEIGHTS["motion_type"]
    if a.direction == b.direction:
        score += _WEIGHTS["direction"]
    if a.family == b.family:
        score += _WEIGHTS["family"]
    return round(score, 4)


def diversity_against(fp: MotionFingerprint, recent: list[MotionFingerprint]) -> float:
    if not recent:
        return 1.0
    return round(1.0 - max(motion_similarity(fp, o) for o in recent), 4)


class MotionPlanner:
    def __init__(self, window: int = 5) -> None:
        self.window = window

    def plan(self, base_motion: str, scene_class: str, history) -> tuple[str, list[dict]]:
        changes: list[dict] = []
        motion = remap_to_scene_class(scene_class, base_motion)
        if motion != base_motion:
            changes.append({"from": base_motion, "to": motion,
                            "reason": f"incompatible con la escena '{scene_class}'; reasignado"})

        candidates = candidates_for(scene_class)
        recent = history.recent_motion_types(self.window)

        if motion in recent:  # evitar repetir (p.ej. 26 push-in)
            alt = self._least_recently_used(candidates, motion, recent, history)
            if alt and alt != motion:
                changes.append({"from": motion, "to": alt,
                                "reason": f"'{motion}' repetido en los últimos {self.window} planos; "
                                          f"se elige la alternativa menos usada"})
                motion = alt
        return motion, changes

    def _least_recently_used(self, candidates, current, recent, history):
        def _key(name):
            last = history.last_use_index(name)
            gap = (history.size - last) if last >= 0 else (history.size + 10_000)
            return (-gap, CATALOG_ORDER.index(name))
        fresh = [c for c in candidates if c != current and c not in recent]
        pool = fresh or [c for c in candidates if c != current]
        return min(pool, key=_key) if pool else current
