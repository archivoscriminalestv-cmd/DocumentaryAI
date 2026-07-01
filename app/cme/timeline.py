"""MotionTimeline — línea temporal del documental (planificación, no render).

Acumula los planos con start/end/duration y transiciones. Determinista; no interpola
ni renderiza, solo coloca cada plano en el tiempo.
"""

from app.cme.models import MotionShot

_DEFAULT_TRANSITION = 0.5
_EDGE_TRANSITION = 1.0  # entrada del primer plano / salida del último


class MotionTimeline:
    def __init__(self) -> None:
        self._shots: list[MotionShot] = []
        self._cursor = 0.0

    def add(self, shot: MotionShot) -> MotionShot:
        first = len(self._shots) == 0
        shot.transition_in = _EDGE_TRANSITION if first else _DEFAULT_TRANSITION
        shot.transition_out = _DEFAULT_TRANSITION
        shot.start = round(self._cursor, 3)
        shot.end = round(self._cursor + shot.duration, 3)
        self._cursor = shot.end
        self._shots.append(shot)
        return shot

    def finalize(self) -> None:
        if self._shots:
            self._shots[-1].transition_out = _EDGE_TRANSITION

    @property
    def total_duration(self) -> float:
        return round(self._cursor, 3)

    @property
    def shots(self) -> list[MotionShot]:
        return list(self._shots)
