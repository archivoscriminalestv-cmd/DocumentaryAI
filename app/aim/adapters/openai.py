"""Adaptador real de OpenAI (LLM / embeddings / images). Requiere API Key.

Health = listar modelos (endpoint ligero, sin consumir generación). La clave nunca se
imprime ni se persiste: solo se usa en la cabecera Authorization en el momento de la llamada.
"""

from app.aim.adapters.base import AdapterBase
from app.aim.errors import AIMError, ErrorClass


class OpenAIAdapter(AdapterBase):
    _BASE = "https://api.openai.com/v1"

    def _auth_headers(self) -> dict:
        key = self._key()
        return {"Authorization": f"Bearer {key}"} if key else {}

    def _health_request(self):
        return f"{self._BASE}/models", None        # lista modelos: ligero, no genera

    def _execute(self, operation: str, **kwargs):
        if operation in ("complete", "llm"):
            data = self._post(f"{self._BASE}/chat/completions", {
                "model": kwargs.get("model", "gpt-4o-mini"),
                "messages": [{"role": "system", "content": kwargs.get("system", "")},
                             {"role": "user", "content": kwargs.get("user", "")}]})
            choices = data.get("choices", []) if isinstance(data, dict) else []
            return choices[0]["message"]["content"] if choices else "UNKNOWN"
        if operation in ("embed", "embeddings"):
            data = self._post(f"{self._BASE}/embeddings", {
                "model": kwargs.get("model", "text-embedding-3-small"),
                "input": kwargs.get("text", "")})
            items = data.get("data", []) if isinstance(data, dict) else []
            return items[0].get("embedding") if items else "UNKNOWN"
        if operation in ("image", "generate_image"):
            data = self._post(f"{self._BASE}/images/generations", {
                "model": kwargs.get("model", "gpt-image-1"),
                "prompt": kwargs.get("prompt", "")})
            items = data.get("data", []) if isinstance(data, dict) else []
            return items[0].get("url") or items[0].get("b64_json", "UNKNOWN") if items else "UNKNOWN"
        raise AIMError(ErrorClass.INVALID_RESPONSE, f"op {operation}")
