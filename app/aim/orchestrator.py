"""APIIntegrationManager (AIM) — punto central de todas las APIs externas.

Solo coordinación, por composición: registro + secretos + health + matriz de capacidades +
resolución. No acopla proveedores concretos a los motores; estos pedirán una CAPACIDAD y el
AIM resolverá el proveedor (principal → alternativo). Determinista.
"""

from app.aim import UNKNOWN
from app.aim.capability_matrix import build_capability_matrix
from app.aim.health import check_all, summarize
from app.aim.metrics import MetricsRecorder
from app.aim.models import ExecutionResult
from app.aim.readiness import ProductionReadinessChecker
from app.aim.registry import default_registry
from app.aim.secrets import SecretManager


class APIIntegrationManager:
    def __init__(self, *, secrets: SecretManager | None = None, registry=None,
                 root: str = ".", http=None) -> None:
        self.secrets = secrets or SecretManager()
        self.registry = registry or default_registry(self.secrets, http=http)
        self._recorder = getattr(self.registry, "recorder", None) or MetricsRecorder()
        self._root = root

    # ------------------------------------------------------------------ ejecución
    def execute(self, capability: str, operation: str, **kwargs) -> ExecutionResult:
        """Un motor pide una CAPACIDAD; el AIM elige el proveedor (principal → alternativos)."""
        last = None
        for provider in self.registry.resolve(capability):
            if not hasattr(provider, "execute"):       # contrato sin adaptador real
                continue
            result = provider.execute(operation, **kwargs)
            if result.ok:
                return result
            last = result
        return ExecutionResult(provider="aim", operation=operation, status="error",
                               value=UNKNOWN,
                               error_class=last.error_class if last else "UNAVAILABLE",
                               note="all_providers_failed" if last else "no_provider")

    def provider_status(self, *, probe: bool = False) -> list[dict]:
        out = []
        for p in self.registry.all():
            h = p.health(probe=probe)
            out.append({
                "name": p.name, "category": p.spec.category, "state": h.state,
                "authenticated": h.authenticated, "reachable": h.reachable,
                "latency_ms": h.latency_ms, "capabilities": sorted(p.spec.capabilities),
                "alternative": p.spec.alternative or "UNKNOWN", "version": p.spec.version,
                "cost": p.spec.cost, "available": h.available, "errors": h.errors,
            })
        return sorted(out, key=lambda d: d["name"])

    def metrics(self) -> list[dict]:
        return self._recorder.to_list()

    def metrics_summary(self) -> dict:
        return self._recorder.summary()

    # ------------------------------------------------------------------ vistas
    def providers(self) -> list:
        return [p.spec for p in self.registry.all()]

    def resolve(self, capability: str) -> list[str]:
        """Cadena de proveedores (nombres) para una capacidad: principal → alternativos."""
        return [p.name for p in self.registry.resolve(capability)]

    def primary(self, capability: str) -> str | None:
        chain = self.registry.resolve(capability)
        return chain[0].name if chain else None

    def capability_matrix(self) -> dict:
        return build_capability_matrix(self.registry)

    def health_report(self, *, probe: bool = False) -> list:
        return check_all(self.registry, probe=probe)

    def health_summary(self, *, probe: bool = False) -> dict:
        return summarize(self.health_report(probe=probe))

    def readiness(self, *, probe: bool = False):
        return ProductionReadinessChecker(self.registry, root=self._root).check(probe=probe)
