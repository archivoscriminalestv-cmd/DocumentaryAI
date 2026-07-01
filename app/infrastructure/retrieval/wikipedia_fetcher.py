"""WikipediaFetcher — recuperación REAL vía la REST API de Wikipedia (C-03).

Usa el endpoint de búsqueda ``/w/rest.php/v1/search/page`` (solo biblioteca
estándar, sin dependencias nuevas). El acceso HTTP se inyecta (``http_get``) para
poder testear el parseo de forma determinista sin red. Degradación: ante
cualquier fallo (red, JSON, etc.) devuelve ``[]`` y nunca lanza.
"""

import json
import re
import ssl
import urllib.parse
import urllib.request
from typing import Callable

from app.domain.search import SearchTask, SearchType
from app.domain.source.retrieved_source import RetrievedSource

_ENDPOINT = "https://en.wikipedia.org/w/rest.php/v1/search/page"
_USER_AGENT = "Mozilla/5.0 (compatible; DocumentaryAI/0.1)"
_PAGE_URL = "https://en.wikipedia.org/wiki/"
_TAG = re.compile(r"<[^>]+>")


def _default_http_get(url: str, timeout: float) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


class WikipediaFetcher:
    def __init__(
        self,
        http_get: Callable[[str, float], str] | None = None,
        limit: int = 5,
        timeout: float = 10.0,
    ) -> None:
        self._http_get = http_get or _default_http_get
        self._limit = limit
        self._timeout = timeout

    def handles(self, search_type: SearchType) -> bool:
        return search_type == SearchType.WIKIPEDIA

    def fetch(self, task: SearchTask) -> list[RetrievedSource]:
        try:
            query = (task.query or "").strip()
            if not query:
                return []
            params = urllib.parse.urlencode({"q": query, "limit": self._limit})
            raw = self._http_get(f"{_ENDPOINT}?{params}", self._timeout)
            data = json.loads(raw)

            sources: list[RetrievedSource] = []
            for page in data.get("pages", [])[: self._limit]:
                title = str(page.get("title", "")).strip()
                key = str(page.get("key", "")).strip()
                if not title or not key:
                    continue
                snippet = str(page.get("description") or "").strip()
                if not snippet:
                    snippet = _TAG.sub("", str(page.get("excerpt") or "")).strip()
                sources.append(
                    RetrievedSource(
                        id="",
                        type=SearchType.WIKIPEDIA,
                        title=title,
                        url=_PAGE_URL + urllib.parse.quote(key),
                        snippet=snippet,
                        query=query,
                    )
                )
            return sources
        except Exception:
            return []  # degradación elegante: nunca rompe la recuperación
