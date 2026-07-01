"""Métricas objetivas del AIM. Nunca registra prompts, datos ni credenciales."""

from app.aim.models import ProviderMetric


class MetricsRecorder:
    def __init__(self) -> None:
        self._metrics: list[ProviderMetric] = []

    def record(self, metric: ProviderMetric) -> None:
        self._metrics.append(metric)

    def all(self) -> list[ProviderMetric]:
        return list(self._metrics)

    def summary(self) -> dict:
        by_provider: dict[str, dict] = {}
        for m in self._metrics:
            agg = by_provider.setdefault(m.provider, {"calls": 0, "errors": 0, "retries": 0})
            agg["calls"] += 1
            agg["errors"] += 0 if m.success else 1
            agg["retries"] += m.retries
        return {
            "total_calls": len(self._metrics),
            "errors": sum(1 for m in self._metrics if not m.success),
            "by_provider": {k: by_provider[k] for k in sorted(by_provider)},
        }

    def to_list(self) -> list[dict]:
        return [m.to_dict() for m in self._metrics]
