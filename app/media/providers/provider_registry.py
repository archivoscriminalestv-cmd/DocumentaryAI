"""ProviderRegistry — orquestación multi-provider declarativa (Fase B).

Fuente de verdad de todos los providers. Cada provider se registra junto a su
``ProviderMetadata`` (capacidades declarativas) y un ``ProviderHealth`` (estado
runtime). La selección es DETERMINISTA y se basa SOLO en metadata + salud:

  1. filtrar por compatibilidad (media_type + capacidades requeridas),
  2. eliminar offline / temporalmente deshabilitados por fallos,
  3. ordenar por prioridad (desc),
  4. devolver el mejor (con fallback al siguiente si falla).

No hay IA, ni heurísticas complejas, ni lógica específica de ningún proveedor
aquí. Health-check pasivo: sin llamadas continuas; tras N fallos un provider se
deshabilita un tiempo (cooldown) y luego vuelve a ser elegible (recuperación).
"""

import time
from dataclasses import dataclass, field
from typing import Callable

from app.media.providers.base import BaseProvider, ProviderUnavailable


@dataclass
class ProviderMetadata:
    name: str
    media_type: str = "image"      # "image" | "video"
    priority: int = 100
    cost: str = "free"             # "free" | "paid"
    supports_style: bool = True
    supports_hd: bool = False
    supports_video: bool = False
    status: str = "online"         # "online" | "offline" (declarativo)
    max_resolution: str = ""       # p.ej. "1280x720"


@dataclass
class ProviderHealth:
    failure_count: int = 0
    last_error: str = ""
    last_success_ts: float = 0.0
    disabled_until: float = 0.0    # 0 = no deshabilitado


@dataclass
class _Entry:
    provider: BaseProvider
    metadata: ProviderMetadata
    health: ProviderHealth = field(default_factory=ProviderHealth)


class ProviderRegistry:
    def __init__(
        self,
        *,
        max_failures: int = 3,
        cooldown_seconds: float = 60.0,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._entries: dict[str, _Entry] = {}
        self._max_failures = max_failures
        self._cooldown = cooldown_seconds
        self._clock = clock or time.time

    # --- registro -----------------------------------------------------------

    def register(self, provider: BaseProvider, metadata: ProviderMetadata) -> None:
        self._entries[metadata.name] = _Entry(provider=provider, metadata=metadata)

    def unregister(self, name: str) -> None:
        self._entries.pop(name, None)

    def all_metadata(self) -> list[ProviderMetadata]:
        return [e.metadata for e in self._entries.values()]

    def health_of(self, name: str) -> ProviderHealth | None:
        entry = self._entries.get(name)
        return entry.health if entry else None

    # --- disponibilidad / salud --------------------------------------------

    def _is_available(self, entry: _Entry, now: float) -> bool:
        if entry.metadata.status != "online":
            return False
        return entry.health.disabled_until == 0.0 or now >= entry.health.disabled_until

    def _record_success(self, entry: _Entry, now: float) -> None:
        entry.health.failure_count = 0
        entry.health.last_error = ""
        entry.health.last_success_ts = now
        entry.health.disabled_until = 0.0

    def _record_failure(self, entry: _Entry, error: str, now: float) -> None:
        entry.health.failure_count += 1
        entry.health.last_error = error
        if entry.health.failure_count >= self._max_failures:
            entry.health.disabled_until = now + self._cooldown

    # --- selección ----------------------------------------------------------

    def select(
        self,
        media_type: str = "image",
        *,
        require_hd: bool = False,
        require_style: bool = False,
        require_free: bool = False,
    ) -> list[BaseProvider]:
        entries = self._select_entries(
            media_type, require_hd=require_hd, require_style=require_style,
            require_free=require_free, now=self._clock(),
        )
        return [e.provider for e in entries]

    # --- generación con fallback + health ----------------------------------

    def generate(
        self,
        prompt: str,
        media_type: str = "image",
        *,
        require_hd: bool = False,
        require_style: bool = False,
        require_free: bool = False,
    ):
        now = self._clock()
        entries = self._select_entries(
            media_type, require_hd=require_hd, require_style=require_style,
            require_free=require_free, now=now,
        )
        if not entries:
            raise ProviderUnavailable(
                f"No hay providers compatibles/disponibles para '{media_type}'."
            )

        errors: list[str] = []
        for entry in entries:
            try:
                if media_type == "image":
                    asset = entry.provider.generate_image(prompt)
                else:
                    asset = entry.provider.generate_video(prompt)
                self._record_success(entry, now)
                return asset
            except Exception as exc:  # un provider roto no tumba la orquestación
                self._record_failure(entry, f"{type(exc).__name__}: {exc}", now)
                errors.append(f"{entry.metadata.name}: {exc}")
        raise ProviderUnavailable("Todos los providers fallaron -> " + " | ".join(errors))

    def _select_entries(self, media_type, *, require_hd, require_style, require_free, now) -> list[_Entry]:
        candidates: list[_Entry] = []
        for entry in self._entries.values():
            m = entry.metadata
            if media_type == "image" and m.media_type != "image":
                continue
            if media_type == "video" and not (m.media_type == "video" or m.supports_video):
                continue
            if require_hd and not m.supports_hd:
                continue
            if require_style and not m.supports_style:
                continue
            if require_free and m.cost != "free":
                continue
            if not self._is_available(entry, now):
                continue
            candidates.append(entry)
        candidates.sort(key=lambda e: (-e.metadata.priority, e.metadata.name))
        return candidates
