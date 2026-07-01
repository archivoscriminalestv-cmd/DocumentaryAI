"""Cliente HTTP inyectable del AIM (común a los adaptadores).

Aísla la red; ``verify=False`` tolera proxies/sandbox. NUNCA registra cabeceras ni cuerpos
(pueden contener credenciales). En tests se inyecta ``MappingHttpClient``/``SequenceHttpClient``
para reproducibilidad sin red.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Response:
    status_code: int = 0
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


class HttpClient(Protocol):
    def get(self, url: str, params: dict | None = None, headers: dict | None = None,
            timeout: float = 20.0) -> Response: ...
    def post(self, url: str, json: dict | None = None, headers: dict | None = None,
             timeout: float = 30.0) -> Response: ...


class RealHttpClient:
    def __init__(self, user_agent: str | None = None) -> None:
        self._ua = user_agent or "DocumentaryAI-AIM/0.1"
        self._session = None

    def _s(self):
        if self._session is None:
            import requests
            s = requests.Session()
            s.verify = False
            s.headers.update({"User-Agent": self._ua})
            self._session = s
        return self._session

    def get(self, url, params=None, headers=None, timeout=20.0) -> Response:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = self._s().get(url, params=params, headers=headers or {}, timeout=timeout)
        return Response(status_code=r.status_code, text=r.text)

    def post(self, url, json=None, headers=None, timeout=30.0) -> Response:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = self._s().post(url, json=json, headers=headers or {}, timeout=timeout)
        return Response(status_code=r.status_code, text=r.text)


class MappingHttpClient:
    """Cliente FALSO determinista: enruta por subcadena de URL. Sin red."""

    def __init__(self, routes: list[tuple[str, Any]] | None = None,
                 status_routes: list[tuple[str, int]] | None = None) -> None:
        self._routes = list(routes or [])
        self._status = list(status_routes or [])
        self.calls: list[str] = []

    def _resp(self, url) -> Response:
        self.calls.append(url)
        for sub, code in self._status:
            if sub in url:
                return Response(status_code=code, _payload={"error": code})
        for sub, payload in self._routes:
            if sub in url:
                return Response(status_code=200, _payload=payload)
        return Response(status_code=404, _payload=None)

    def get(self, url, params=None, headers=None, timeout=20.0) -> Response:
        return self._resp(url)

    def post(self, url, json=None, headers=None, timeout=30.0) -> Response:
        return self._resp(url)


class SequenceHttpClient:
    """Devuelve respuestas en secuencia (para tests de retry/circuit breaker)."""

    def __init__(self, responses: list) -> None:
        self._responses = list(responses)
        self.calls = 0

    def _next(self) -> Response:
        self.calls += 1
        item = self._responses[min(self.calls - 1, len(self._responses) - 1)]
        if isinstance(item, Exception):
            raise item
        if isinstance(item, int):
            return Response(status_code=item, _payload={"error": item})
        if isinstance(item, tuple):
            return Response(status_code=item[0], _payload=item[1])
        return Response(status_code=200, _payload=item)

    def get(self, url, params=None, headers=None, timeout=20.0) -> Response:
        return self._next()

    def post(self, url, json=None, headers=None, timeout=30.0) -> Response:
        return self._next()
