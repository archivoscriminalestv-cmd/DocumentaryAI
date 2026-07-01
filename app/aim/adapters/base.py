"""Adaptador base de proveedor (AIM-002) — contrato común, sin lógica duplicada.

Implementa: health() / capabilities() / authenticate() / execute() / cost() / limits() /
provider_name() / version(), más la gestión común de errores (clasificados), reintentos
exponenciales acotados, circuit breaker y métricas objetivas. Los adaptadores concretos solo
definen ``_auth_headers``, ``_health_request`` y ``_execute``. NUNCA imprime/persiste claves,
NUNCA inventa: si una API falla → ``UNKNOWN`` con su clase de error.
"""

import time

from app.aim import UNKNOWN
from app.aim.errors import AIMError, ErrorClass, classify, to_health_state
from app.aim.metrics import MetricsRecorder
from app.aim.models import (
    ExecutionResult,
    HealthState,
    HealthStatus,
    ProviderMetric,
    ProviderStatus,
)
from app.aim.retry import CircuitBreaker, RetryPolicy


class AdapterBase:
    def __init__(self, spec, secrets, *, http=None, recorder=None, breaker=None,
                 policy=None, sleep=time.sleep) -> None:
        self.spec = spec
        self._secrets = secrets
        self._http = http
        self._recorder = recorder or MetricsRecorder()
        self._breaker = breaker or CircuitBreaker()
        self._policy = policy or RetryPolicy()
        self._sleep = sleep

    # ------------------------------------------------------------------ contrato
    @property
    def name(self) -> str:
        return self.spec.name

    def provider_name(self) -> str:
        return self.spec.name

    def version(self) -> str:
        return self.spec.version

    def capabilities(self) -> list[str]:
        return list(self.spec.capabilities)

    def cost(self) -> str:
        return self.spec.cost

    def limits(self) -> dict:
        return dict(self.spec.known_limits)

    def authenticate(self) -> dict:
        """Estado de autenticación SIN exponer la credencial."""
        if not self.spec.requires_api_key:
            return {"required": False, "configured": True, "status": "not_required"}
        configured = bool(self._key())
        return {"required": True, "configured": configured,
                "status": "yes" if configured else "no"}

    def usable(self) -> bool:
        if self.spec.status == ProviderStatus.DISABLED:
            return False
        return (not self.spec.requires_api_key) or bool(self._key())

    # ------------------------------------------------------------------ health
    def health(self, *, probe: bool = False) -> HealthStatus:
        status = HealthStatus(provider=self.name, available=self.spec.status == ProviderStatus.AVAILABLE)
        status.authenticated = self.authenticate()["status"]
        if self.spec.status == ProviderStatus.DISABLED:
            status.state = HealthState.DISABLED
            return status
        if self.spec.requires_api_key and not self._key():
            status.state = HealthState.NO_CREDENTIALS
            return status
        if not probe:
            status.state = HealthState.CONFIGURED
            return status
        start = time.perf_counter()
        try:
            self._health_probe()
            status.latency_ms = round((time.perf_counter() - start) * 1000.0, 1)
            status.reachable = "yes"
            status.state = HealthState.READY
        except AIMError as exc:
            status.latency_ms = round((time.perf_counter() - start) * 1000.0, 1)
            status.reachable = "no"
            status.errors.append(exc.error_class)
            status.state = to_health_state(exc.error_class)
        return status

    # ------------------------------------------------------------------ execute
    def execute(self, operation: str, **kwargs) -> ExecutionResult:
        if self.spec.status == ProviderStatus.DISABLED:
            return ExecutionResult(self.name, operation, "unavailable", UNKNOWN, ErrorClass.UNAVAILABLE)
        if not self.usable():
            ec = ErrorClass.AUTH if self.spec.requires_api_key else ErrorClass.UNAVAILABLE
            return ExecutionResult(self.name, operation, "unavailable", UNKNOWN, ec,
                                   note="no_credentials")
        if self._breaker.is_open(self.name):
            return ExecutionResult(self.name, operation, "unavailable", UNKNOWN,
                                   ErrorClass.SERVICE_DOWN, note="circuit_open")
        attempt = 0
        while True:
            start = time.perf_counter()
            try:
                value = self._execute(operation, **kwargs)
            except AIMError as exc:
                latency = round((time.perf_counter() - start) * 1000.0, 1)
                if self._policy.is_retriable(exc.error_class, attempt):
                    self._sleep(self._policy.delay(attempt))
                    attempt += 1
                    continue
                self._breaker.record_failure(self.name)
                self._recorder.record(ProviderMetric(self.name, operation, False, latency,
                                                      attempt, exc.error_class, self.cost()))
                return ExecutionResult(self.name, operation, "error", UNKNOWN, exc.error_class,
                                       attempt, latency)
            latency = round((time.perf_counter() - start) * 1000.0, 1)
            self._breaker.record_success(self.name)
            self._recorder.record(ProviderMetric(self.name, operation, True, latency, attempt,
                                                  ErrorClass.NONE, self.cost()))
            return ExecutionResult(self.name, operation, "ok", value, ErrorClass.NONE, attempt, latency)

    # ------------------------------------------------------------------ helpers
    def _key(self):
        return self._secrets.get(self.spec.api_key_env) if self.spec.requires_api_key else None

    def _client(self):
        if self._http is None:
            from app.aim.http import RealHttpClient
            self._http = RealHttpClient()
        return self._http

    def _auth_headers(self) -> dict:
        return {}

    def _get(self, url, params=None):
        try:
            resp = self._client().get(url, params=params, headers=self._auth_headers(),
                                      timeout=self.spec.timeout)
        except Exception as exc:  # noqa: BLE001
            raise AIMError(classify(exc=exc))
        if not resp.ok:
            raise AIMError(classify(status_code=resp.status_code), f"status {resp.status_code}")
        try:
            return resp.json()
        except Exception:
            raise AIMError(ErrorClass.INVALID_RESPONSE)

    def _post(self, url, payload=None):
        try:
            resp = self._client().post(url, json=payload, headers=self._auth_headers(),
                                       timeout=self.spec.timeout)
        except Exception as exc:  # noqa: BLE001
            raise AIMError(classify(exc=exc))
        if not resp.ok:
            raise AIMError(classify(status_code=resp.status_code), f"status {resp.status_code}")
        try:
            return resp.json()
        except Exception:
            raise AIMError(ErrorClass.INVALID_RESPONSE)

    # --- a implementar por cada adaptador --------------------------------
    def _health_probe(self) -> None:
        url, params = self._health_request()
        self._get(url, params=params)

    def _health_request(self):
        raise NotImplementedError

    def _execute(self, operation: str, **kwargs):
        raise NotImplementedError(f"{self.name}: operación '{operation}' no soportada")
