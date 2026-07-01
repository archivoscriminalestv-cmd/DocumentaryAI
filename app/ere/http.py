"""Cliente HTTP JSON mínimo e inyectable para los proveedores reales del ERE.

Independiente de CRE (el ERE no debe depender de otros subsistemas). Aísla la red
tras ``get_json``; en los tests se inyecta un cliente falso → cero llamadas reales.
``verify=False`` tolera entornos con intercepción TLS (proxies / sandbox).
"""

from typing import Any, Protocol


class HttpClient(Protocol):
    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        ...


class JsonHttpClient:
    def __init__(self, timeout: float = 10.0, user_agent: str | None = None) -> None:
        self._timeout = timeout
        self._user_agent = user_agent or "DocumentaryAI-ERE/0.1 (research; contact: local)"
        self._session = None

    def _get_session(self):
        if self._session is None:
            import requests  # import perezoso: los tests no necesitan requests

            session = requests.Session()
            session.verify = False
            session.headers.update({"User-Agent": self._user_agent})
            self._session = session
        return self._session

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        import warnings

        session = self._get_session()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = session.get(url, params=params, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
