"""Cliente HTTP JSON mínimo e inyectable para los proveedores reales del CRE.

Aísla la dependencia de red detrás de un único método ``get_json``. Los
proveedores reciben un objeto con esa firma; en los tests se inyecta un cliente
falso (sin red), de modo que toda llamada externa es completamente mockeable y el
sistema sigue siendo determinista.

Nota de entorno: la sesión usa ``verify=False`` para tolerar entornos con
intercepción TLS (proxies corporativos / sandbox). En producción el comportamiento
es el mismo; solo se omite la verificación del certificado del proxy.
"""

from typing import Any, Protocol


class HttpClient(Protocol):
    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        ...


class JsonHttpClient:
    """Implementación real basada en ``requests`` (importado de forma perezosa)."""

    def __init__(self, timeout: float = 10.0, user_agent: str | None = None) -> None:
        self._timeout = timeout
        self._user_agent = user_agent or "DocumentaryAI-CRE/0.2 (research; contact: local)"
        self._session = None

    def _get_session(self):
        if self._session is None:
            import requests  # import perezoso: el CRE no depende de requests para los tests

            session = requests.Session()
            session.verify = False  # tolera intercepción TLS (ver docstring del módulo)
            session.headers.update({"User-Agent": self._user_agent})
            self._session = session
        return self._session

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        import warnings

        session = self._get_session()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # silencia InsecureRequestWarning
            response = session.get(url, params=params, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
