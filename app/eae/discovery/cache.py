"""Cache determinista de descubrimiento (EAE-004).

Evita repetir búsquedas iguales. Clave = proveedor + categoría + target + términos
(ordenados) + idioma + filtros (ordenados). TTL configurable. **Nunca cachea errores**
(solo el llamador guarda resultados correctos). Reloj inyectable para tests.
"""

import time
from typing import Any


def cache_key(provider: str, *, category: str, target: str, terms: list[str],
              language: str, filters: list[str]) -> str:
    return "|".join([
        provider, category or "", target or "",
        "+".join(sorted(terms or [])),
        language or "",
        "+".join(sorted(filters or [])),
    ])


class DiscoveryCache:
    def __init__(self, ttl_seconds: float = 3600.0, clock=time.monotonic) -> None:
        self.ttl = ttl_seconds
        self._clock = clock
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            return None
        stored_at, value = entry
        if self.ttl and (self._clock() - stored_at) > self.ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (self._clock(), value)
