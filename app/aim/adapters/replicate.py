"""Adaptador (preparado) de Replicate (imagen/vídeo). Requiere API Key; si no existe → UNKNOWN.

Health = consultar la cuenta (endpoint ligero). La generación crea una predicción; nunca
descarga binarios aquí.
"""

from app.aim.adapters.base import AdapterBase
from app.aim.errors import AIMError, ErrorClass


class ReplicateAdapter(AdapterBase):
    _BASE = "https://api.replicate.com/v1"

    def _auth_headers(self) -> dict:
        key = self._key()
        return {"Authorization": f"Token {key}"} if key else {}

    def _health_request(self):
        return f"{self._BASE}/account", None        # cuenta: ligero, auth-check

    def _execute(self, operation: str, **kwargs):
        if operation in ("generate_image", "image", "generate_video", "video"):
            data = self._post(f"{self._BASE}/predictions", {
                "version": kwargs.get("version", ""),
                "input": {"prompt": kwargs.get("prompt", "")}})
            return {"prediction_id": data.get("id", "UNKNOWN"),
                    "status": data.get("status", "UNKNOWN")} if isinstance(data, dict) else "UNKNOWN"
        raise AIMError(ErrorClass.INVALID_RESPONSE, f"op {operation}")
