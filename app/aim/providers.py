"""Proveedor base del AIM — implementa ``health()`` de forma genérica y determinista.

Cada proveedor (hoy, un CONTRATO declarativo) implementa ``health()``: comprueba credenciales
e integración SIN descargar contenido. Opcionalmente, un ``prober`` inyectable hace una
comprobación REAL de conectividad (latencia); por defecto no hay red (estado reproducible).
Los adaptadores reales (futuros) heredarán de aquí y añadirán el método de su capacidad.
"""

import time

from app.aim.models import HealthState, HealthStatus, ProviderSpec, ProviderStatus


class ContractProvider:
    def __init__(self, spec: ProviderSpec, secrets) -> None:
        self.spec = spec
        self._secrets = secrets

    @property
    def name(self) -> str:
        return self.spec.name

    def credentials_configured(self) -> bool:
        if not self.spec.requires_api_key:
            return True
        return self._secrets.has(self.spec.api_key_env)

    def health(self, *, probe: bool = False, prober=None) -> HealthStatus:
        spec = self.spec
        status = HealthStatus(provider=spec.name, available=spec.status == ProviderStatus.AVAILABLE)
        status.authenticated = ("not_required" if not spec.requires_api_key
                                else ("yes" if self.credentials_configured() else "no"))

        if spec.status == ProviderStatus.DISABLED:
            status.state = HealthState.DISABLED
            return status
        if spec.requires_api_key and not self.credentials_configured():
            status.state = HealthState.NO_CREDENTIALS
            return status

        # Comprobación real OPCIONAL (solo conectividad; nunca descarga contenido).
        if prober is not None:
            start = time.perf_counter()
            try:
                ok = bool(prober(spec))
            except Exception as exc:  # noqa: BLE001
                status.errors.append(str(exc)[:120])
                ok = False
            status.latency_ms = round((time.perf_counter() - start) * 1000.0, 1)
            status.reachable = "yes" if ok else "no"
            if not ok:
                status.state = HealthState.UNREACHABLE
                return status

        status.state = (HealthState.READY if spec.status == ProviderStatus.AVAILABLE
                        else HealthState.NOT_INTEGRATED)
        return status
