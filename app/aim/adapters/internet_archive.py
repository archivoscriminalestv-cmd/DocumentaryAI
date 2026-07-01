"""Adaptador real de Internet Archive (búsqueda). Público; NO descarga contenido."""

from app.aim.adapters.base import AdapterBase
from app.aim.errors import AIMError, ErrorClass


class InternetArchiveAdapter(AdapterBase):
    def _api(self) -> str:
        return "https://archive.org/advancedsearch.php"

    def _health_request(self):
        return self._api(), {"q": "test", "rows": 1, "output": "json", "fl[]": "identifier"}

    def _execute(self, operation: str, **kwargs):
        if operation != "search":
            raise AIMError(ErrorClass.INVALID_RESPONSE, f"op {operation}")
        data = self._get(self._api(), params={
            "q": kwargs.get("query", ""), "rows": int(kwargs.get("limit", 5)),
            "output": "json", "fl[]": ["identifier", "title", "mediatype"]})
        docs = data.get("response", {}).get("docs", []) if isinstance(data, dict) else []
        return [{"identifier": d.get("identifier"), "title": d.get("title"),
                 "mediatype": d.get("mediatype")} for d in docs]
