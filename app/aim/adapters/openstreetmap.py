"""Adaptador real de OpenStreetMap / Nominatim (geocoding). Público; consulta sencilla."""

from app.aim.adapters.base import AdapterBase
from app.aim.errors import AIMError, ErrorClass


class OpenStreetMapAdapter(AdapterBase):
    def _api(self) -> str:
        return "https://nominatim.openstreetmap.org/search"

    def _health_request(self):
        return self._api(), {"q": "Paris", "format": "jsonv2", "limit": 1}

    def _execute(self, operation: str, **kwargs):
        if operation not in ("geocode", "search"):
            raise AIMError(ErrorClass.INVALID_RESPONSE, f"op {operation}")
        data = self._get(self._api(), params={
            "q": kwargs.get("place") or kwargs.get("query", ""), "format": "jsonv2",
            "limit": int(kwargs.get("limit", 1))})
        places = data if isinstance(data, list) else []
        return [{"display_name": p.get("display_name"), "lat": p.get("lat"),
                 "lon": p.get("lon"), "osm_id": p.get("osm_id")} for p in places]
