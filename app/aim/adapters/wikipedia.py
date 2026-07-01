"""Adaptador real de Wikipedia (búsqueda). API pública, sin clave. No descarga artículos."""

from app.aim.adapters.base import AdapterBase
from app.aim.errors import AIMError, ErrorClass


class WikipediaAdapter(AdapterBase):
    def _api(self) -> str:
        return "https://en.wikipedia.org/w/api.php"

    def _health_request(self):
        return self._api(), {"action": "query", "list": "search", "srsearch": "test",
                             "srlimit": 1, "format": "json"}

    def _execute(self, operation: str, **kwargs):
        if operation != "search":
            raise AIMError(ErrorClass.INVALID_RESPONSE, f"op {operation}")
        data = self._get(self._api(), params={
            "action": "query", "list": "search", "srsearch": kwargs.get("query", ""),
            "srlimit": int(kwargs.get("limit", 5)), "format": "json"})
        hits = data.get("query", {}).get("search", []) if isinstance(data, dict) else []
        return [{"title": h.get("title"), "pageid": h.get("pageid")} for h in hits]
