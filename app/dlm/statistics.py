"""Cálculos de rendimiento del dashboard (deterministas, reloj inyectable).

ThroughputCalculator (vídeos/hora, planos/min, escenas/min, MB conocimiento/hora),
ETAEstimator (ETA de vídeo y de cola), SpeedEstimator (media e instantánea).
"""


# Mínimo de tiempo para reportar tasas (evita transitorios absurdos al inicio).
_MIN_ELAPSED = 1.0


class ThroughputCalculator:
    @staticmethod
    def per_hour(count: float, elapsed_seconds: float) -> float:
        if elapsed_seconds < _MIN_ELAPSED:
            return 0.0
        return round(count / (elapsed_seconds / 3600.0), 3)

    @staticmethod
    def per_minute(count: float, elapsed_seconds: float) -> float:
        if elapsed_seconds < _MIN_ELAPSED:
            return 0.0
        return round(count / (elapsed_seconds / 60.0), 3)

    @staticmethod
    def mb_per_hour(bytes_count: float, elapsed_seconds: float) -> float:
        if elapsed_seconds < _MIN_ELAPSED:
            return 0.0
        return round((bytes_count / (1024 * 1024)) / (elapsed_seconds / 3600.0), 3)


class ETAEstimator:
    @staticmethod
    def remaining(elapsed: float, percent: float) -> float:
        """ETA por regla de tres sobre el porcentaje completado (0..1)."""
        if percent <= 0.0 or percent >= 1.0:
            return 0.0
        return round(elapsed * (1.0 - percent) / percent, 3)

    @staticmethod
    def queue_eta(elapsed: float, completed: int, total: int) -> float:
        if completed <= 0 or total <= 0 or completed >= total:
            return 0.0
        per_item = elapsed / completed
        return round(per_item * (total - completed), 3)


class SpeedEstimator:
    """Velocidad media (sobre todo el run) e instantánea (último vídeo)."""

    def __init__(self) -> None:
        self._last_completion_time: float | None = None
        self.last_item_seconds: float = 0.0

    def record_completion(self, now: float) -> None:
        if self._last_completion_time is not None:
            self.last_item_seconds = round(now - self._last_completion_time, 3)
        self._last_completion_time = now

    @staticmethod
    def average_item_seconds(elapsed: float, completed: int) -> float:
        return round(elapsed / completed, 3) if completed > 0 else 0.0
