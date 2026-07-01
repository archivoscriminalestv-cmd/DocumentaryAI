"""Adaptador real de ElevenLabs (voz). Requiere API Key. Health = listar voces (ligero)."""

from app.aim.adapters.base import AdapterBase
from app.aim.errors import AIMError, ErrorClass


class ElevenLabsAdapter(AdapterBase):
    _BASE = "https://api.elevenlabs.io/v1"

    def _auth_headers(self) -> dict:
        key = self._key()
        return {"xi-api-key": key} if key else {}

    def _health_request(self):
        return f"{self._BASE}/voices", None        # lista voces: ligero, no sintetiza audio

    def _execute(self, operation: str, **kwargs):
        if operation in ("voices", "list_voices"):
            data = self._get(f"{self._BASE}/voices")
            voices = data.get("voices", []) if isinstance(data, dict) else []
            return [{"voice_id": v.get("voice_id"), "name": v.get("name")} for v in voices]
        if operation in ("synthesize", "tts"):
            # devuelve la referencia de la operación; NO descarga audio aquí
            voice = kwargs.get("voice_id", "")
            self._post(f"{self._BASE}/text-to-speech/{voice}", {
                "text": kwargs.get("text", ""), "model_id": kwargs.get("model", "eleven_multilingual_v2")})
            return {"voice_id": voice, "status": "requested"}
        raise AIMError(ErrorClass.INVALID_RESPONSE, f"op {operation}")
