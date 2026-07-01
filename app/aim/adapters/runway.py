"""Adaptador (preparado) de Runway (vídeo). Requiere API Key; si no existe → UNKNOWN.

Health = comprobación de autenticación ligera. La generación de vídeo se prepara (crea la
tarea); nunca descarga vídeo aquí.
"""

from app.aim.adapters.base import AdapterBase
from app.aim.errors import AIMError, ErrorClass


class RunwayAdapter(AdapterBase):
    _BASE = "https://api.dev.runwayml.com/v1"

    def _auth_headers(self) -> dict:
        key = self._key()
        return {"Authorization": f"Bearer {key}", "X-Runway-Version": "2024-11-06"} if key else {}

    def _health_request(self):
        return f"{self._BASE}/organization", None      # auth-check ligero

    def _execute(self, operation: str, **kwargs):
        if operation in ("generate_video", "video"):
            data = self._post(f"{self._BASE}/image_to_video", {
                "promptText": kwargs.get("prompt", ""), "model": kwargs.get("model", "gen3a_turbo")})
            return {"task_id": data.get("id", "UNKNOWN"), "status": data.get("status", "UNKNOWN")} \
                if isinstance(data, dict) else "UNKNOWN"
        raise AIMError(ErrorClass.INVALID_RESPONSE, f"op {operation}")
