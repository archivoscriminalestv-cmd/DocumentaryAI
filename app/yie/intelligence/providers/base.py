"""Interfaz de proveedor de enriquecimiento (YIE-002).

Un ``EnrichmentProvider`` aporta campos PÚBLICOS adicionales sobre el vídeo/canal
(p.ej. totales del canal, fecha de creación, pinned comment). Es independiente y
opcional: si no está disponible, ``available()`` es False y ``fetch`` devuelve ``{}``.
Nunca debe automatizar navegadores ni depender de HTML, y nunca debe romper el pipeline.
"""

from typing import Protocol


class EnrichmentProvider(Protocol):
    name: str

    def available(self) -> bool: ...

    def fetch(self, video_id: str, raw: dict) -> dict:
        """Devuelve un dict de campos públicos (claves canónicas) o ``{}`` si no hay datos."""
        ...
