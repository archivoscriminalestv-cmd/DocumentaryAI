"""YouTubeMetadataFetcher — obtiene metadatos públicos de un vídeo de YouTube.

Solo biblioteca estándar (sin dependencias nuevas, sin IA, sin persistencia):
- título y canal vía el endpoint oEmbed de YouTube,
- descripción desde el HTML de la página del vídeo (campo ``shortDescription``).

Degrada con elegancia: si un dato no está disponible (p. ej. sin red), devuelve
ese campo vacío para que el pipeline pueda continuar igualmente.
"""

import json
import re
import ssl
import urllib.parse
import urllib.request

_OEMBED_ENDPOINT = "https://www.youtube.com/oembed"
_USER_AGENT = "Mozilla/5.0 (compatible; DocumentaryAI/0.1)"
_SHORT_DESCRIPTION = re.compile(r'"shortDescription":"((?:\\.|[^"\\])*)"')


class YouTubeMetadataFetcher:
    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout
        self._ssl_context = ssl._create_unverified_context()

    def fetch(self, url: str) -> dict[str, str]:
        """Devuelve {url, title, channel, description}; campos vacíos si fallan."""
        title, channel = "", ""
        description = ""
        try:
            title, channel = self._fetch_oembed(url)
        except Exception:
            pass
        try:
            description = self._fetch_description(url)
        except Exception:
            pass
        return {
            "url": url,
            "title": title,
            "channel": channel,
            "description": description,
        }

    def _fetch_oembed(self, url: str) -> tuple[str, str]:
        query = urllib.parse.urlencode({"url": url, "format": "json"})
        request = urllib.request.Request(
            f"{_OEMBED_ENDPOINT}?{query}", headers={"User-Agent": _USER_AGENT}
        )
        with urllib.request.urlopen(
            request, timeout=self._timeout, context=self._ssl_context
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("title", ""), data.get("author_name", "")

    def _fetch_description(self, url: str) -> str:
        request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(
            request, timeout=self._timeout, context=self._ssl_context
        ) as response:
            html = response.read().decode("utf-8", errors="replace")
        match = _SHORT_DESCRIPTION.search(html)
        if match is None:
            return ""
        # El valor está escapado como cadena JSON; lo decodificamos.
        return json.loads(f'"{match.group(1)}"')
