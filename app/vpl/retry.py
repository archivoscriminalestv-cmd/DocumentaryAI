"""Política de reintentos del VPL — backoff exponencial, provider-independiente.

Reintenta solo errores TRANSITORIOS (``ProviderError.transient``). ``sleep`` es
inyectable (tests deterministas sin esperas). Devuelve (resultado, intentos_extra).
"""

import time
from typing import Callable

from app.vpl.provider import ProviderError


def run_with_retry(
    fn: Callable,
    *,
    max_retries: int = 2,
    base_delay: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
    on_retry: Callable[[int, Exception], None] | None = None,
):
    attempt = 0
    while True:
        try:
            return fn(), attempt
        except ProviderError as exc:
            if not exc.transient or attempt >= max_retries:
                raise
            attempt += 1
            if on_retry:
                on_retry(attempt, exc)
            sleep(base_delay * (2 ** (attempt - 1)))
