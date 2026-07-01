"""Proveedor vidIQ (YIE-002) — independiente y OPCIONAL.

DocumentaryAI NO depende de vidIQ. Este proveedor solo consumiría datos PÚBLICOS y
estructurados si existiera una vía oficial (API/exportación), inyectada como ``client``.
Por defecto no hay cliente → ``available()`` es False y ``fetch`` devuelve ``{}`` (los
campos quedan ``UNKNOWN``). Nunca automatiza el navegador, nunca depende del HTML, nunca
rompe el pipeline.

Claves canónicas que podría aportar (cuando haya cliente oficial): total_views,
total_videos, creation_date, channel_keywords, playlist_count, pinned_comment, etc.
"""


class VidIQProvider:
    name = "vidiq"

    def __init__(self, client=None) -> None:
        self._client = client            # cliente oficial inyectable (None = no disponible)

    def available(self) -> bool:
        return self._client is not None

    def fetch(self, video_id: str, raw: dict) -> dict:
        if self._client is None:
            return {}
        try:
            data = self._client.public_stats(video_id)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}
