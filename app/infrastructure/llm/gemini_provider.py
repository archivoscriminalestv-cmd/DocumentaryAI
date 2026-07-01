"""GeminiProvider — stub de proveedor (Sprint B-06.1).

Preparado para el futuro: implementa la forma del puerto ``LLMProvider`` pero
NO contiene lógica real (no importa el SDK de Gemini ni hace llamadas). Si se
selecciona vía ``config.AI_PROVIDER`` y se invoca, lanza ``NotImplementedError``
y la etapa LLM degrada al guion determinista (fallback).
"""


class GeminiProvider:
    def __init__(self, model: str = "", api_key: str | None = None) -> None:
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    def complete(self, system: str, user: str) -> str:
        raise NotImplementedError("GeminiProvider aún no está implementado.")
