"""Capa HTTP inyectable del Discovery (EAE-004).

``HttpClient`` (Protocol) + ``Response`` + política de reintentos / rate limit / timeout /
backoff. Los proveedores NUNCA importan ``requests`` ni llaman directamente: reciben un
``HttpClient``. En los tests se inyecta ``MappingHttpClient`` (sin red, determinista).
"""

import time
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Response:
    status_code: int = 0
    url: str = ""
    _payload: Any = None
    text: str = ""

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> Any:
        if self._payload is not None:
            return self._payload
        import json
        return json.loads(self.text or "null")


@dataclass
class RetryPolicy:
    max_retries: int = 2
    backoff_base: float = 0.5          # segundos; espera = base * 2**intento
    retry_on: tuple = (429, 500, 502, 503, 504)


@dataclass
class RateLimiter:
    """Limita la frecuencia de peticiones (intervalo mínimo entre llamadas)."""
    min_interval: float = 0.0
    _last: float = field(default=0.0, repr=False)
    _clock: Any = field(default=time.monotonic, repr=False)
    _sleep: Any = field(default=time.sleep, repr=False)

    def wait(self) -> None:
        if self.min_interval <= 0:
            return
        now = self._clock()
        elapsed = now - self._last
        if elapsed < self.min_interval:
            self._sleep(self.min_interval - elapsed)
        self._last = self._clock()


class HttpClient(Protocol):
    def get(self, url: str, params: dict | None = None,
            headers: dict | None = None) -> Response: ...


class RealHttpClient:
    """Cliente real (requests, import perezoso, ``verify=False`` para entornos con proxy).

    Aplica timeout, rate limit, reintentos y backoff. Nunca scraping ni HTML: solo
    peticiones a endpoints JSON oficiales.
    """

    def __init__(self, *, timeout: float = 20.0, retry: RetryPolicy | None = None,
                 rate_limiter: RateLimiter | None = None, user_agent: str | None = None) -> None:
        self._timeout = timeout
        self._retry = retry or RetryPolicy()
        self._rate = rate_limiter or RateLimiter()
        self._ua = user_agent or "DocumentaryAI-EAE/0.1 (discovery; contact: local)"
        self._session = None
        self._sleep = time.sleep

    def _get_session(self):
        if self._session is None:
            import requests
            s = requests.Session()
            s.verify = False
            s.headers.update({"User-Agent": self._ua, "Accept": "application/json"})
            self._session = s
        return self._session

    def get(self, url: str, params: dict | None = None, headers: dict | None = None) -> Response:
        import warnings
        session = self._get_session()
        attempt = 0
        while True:
            self._rate.wait()
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    r = session.get(url, params=params, headers=headers, timeout=self._timeout)
            except Exception:
                if attempt >= self._retry.max_retries:
                    raise
                self._sleep(self._retry.backoff_base * (2 ** attempt))
                attempt += 1
                continue
            if r.status_code in self._retry.retry_on and attempt < self._retry.max_retries:
                self._sleep(self._retry.backoff_base * (2 ** attempt))
                attempt += 1
                continue
            return Response(status_code=r.status_code, url=url, text=r.text)


class MappingHttpClient:
    """Cliente FALSO determinista para tests/demos: enruta por subcadena de URL.

    ``routes``: lista de ``(substring, payload)``; la primera coincidencia gana. Sin red.
    """

    def __init__(self, routes: list[tuple[str, Any]] | None = None) -> None:
        self._routes = list(routes or [])
        self.calls: list[str] = []

    def add(self, substring: str, payload: Any) -> "MappingHttpClient":
        self._routes.append((substring, payload))
        return self

    def get(self, url: str, params: dict | None = None, headers: dict | None = None) -> Response:
        self.calls.append(url)
        for substring, payload in self._routes:
            if substring in url:
                return Response(status_code=200, url=url, _payload=payload)
        return Response(status_code=404, url=url, _payload=None)
