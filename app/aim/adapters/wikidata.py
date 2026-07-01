"""Adaptador real de Wikidata (búsqueda de entidades). API pública, sin clave."""

from app.aim.adapters.base import AdapterBase
from app.aim.errors import AIMError, ErrorClass


class WikidataAdapter(AdapterBase):
    def _api(self) -> str:
        return "https://www.wikidata.org/w/api.php"

    def _health_request(self):
        return self._api(), {"action": "wbsearchentities", "search": "test",
                             "language": "en", "format": "json", "limit": 1}

    def _execute(self, operation: str, **kwargs):
        if operation not in ("search", "entity_search"):
            raise AIMError(ErrorClass.INVALID_RESPONSE, f"op {operation}")
        lang = kwargs.get("language", "en")
        data = self._get(self._api(), params={
            "action": "wbsearchentities", "search": kwargs.get("query", ""),
            "language": lang, "uselang": lang, "format": "json",
            "limit": int(kwargs.get("limit", 5))})
        items = data.get("search", []) if isinstance(data, dict) else []
        return [{"qid": e.get("id"), "label": e.get("label"),
                 "description": e.get("description")} for e in items]
