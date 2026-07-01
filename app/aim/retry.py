"""Política de reintentos y circuit breaker del AIM (común a todos los adaptadores).

Reintentos exponenciales acotados (NUNCA infinitos), solo para errores transitorios; circuit
breaker simple por proveedor para no machacar un servicio caído. Reloj/sleep inyectables.
"""

import time
from dataclasses import dataclass, field

from app.aim.errors import ErrorClass


@dataclass
class RetryPolicy:
    max_retries: int = 2
    base_delay: float = 0.5            # segundos; espera = base * 2**intento
    retriable: tuple = ErrorClass.RETRIABLE

    def delay(self, attempt: int) -> float:
        return self.base_delay * (2 ** attempt)

    def is_retriable(self, error_class: str, attempt: int) -> bool:
        return error_class in self.retriable and attempt < self.max_retries


@dataclass
class CircuitBreaker:
    threshold: int = 3                 # fallos consecutivos para abrir el circuito
    _failures: dict = field(default_factory=dict)
    _open: set = field(default_factory=set)

    def is_open(self, provider: str) -> bool:
        return provider in self._open

    def record_failure(self, provider: str) -> None:
        n = self._failures.get(provider, 0) + 1
        self._failures[provider] = n
        if n >= self.threshold:
            self._open.add(provider)

    def record_success(self, provider: str) -> None:
        self._failures[provider] = 0
        self._open.discard(provider)

    def reset(self, provider: str) -> None:
        self.record_success(provider)
