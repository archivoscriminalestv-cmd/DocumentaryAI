"""HTTP de bajo nivel del VPL (stdlib, inyectable en adapters).

Clasifica errores en transitorios (timeout/conexión/429/5xx) vs permanentes
(4xx/auth) lanzando ``ProviderError`` para que la política de reintentos actúe.
"""

import json
import ssl
import urllib.error
import urllib.request

from app.vpl.provider import ProviderError

_CTX = ssl._create_unverified_context()


def _transient_status(status: int) -> bool:
    return status == 429 or 500 <= status < 600


def post_json(url: str, body: dict, headers: dict, timeout: float) -> dict:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={**headers, "Content-Type": "application/json"}, method="POST"
    )
    return _read_json(request, timeout)


def get_json(url: str, headers: dict, timeout: float) -> dict:
    request = urllib.request.Request(url, headers=headers, method="GET")
    return _read_json(request, timeout)


def post_bytes(url: str, body: dict, headers: dict, timeout: float) -> tuple[bytes, str]:
    """POST JSON y devuelve (bytes_crudos, content_type). Para APIs que responden
    con la imagen binaria directamente (p.ej. HF Inference text-to-image)."""
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={**headers, "Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=_CTX) as response:
            return response.read(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300] if hasattr(exc, "read") else ""
        raise ProviderError(f"HTTP {exc.code}: {detail}", transient=_transient_status(exc.code)) from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"network error POST {url}: {exc}", transient=True) from exc


def get_bytes(url: str, headers: dict, timeout: float) -> bytes:
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=_CTX) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise ProviderError(f"HTTP {exc.code} GET {url}", transient=_transient_status(exc.code)) from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"network error GET {url}: {exc}", transient=True) from exc


def _read_json(request, timeout: float) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=_CTX) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300] if hasattr(exc, "read") else ""
        raise ProviderError(f"HTTP {exc.code}: {detail}", transient=_transient_status(exc.code)) from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"network error: {exc}", transient=True) from exc
