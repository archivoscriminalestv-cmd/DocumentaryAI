"""OpenAIProvider — stub de proveedor (Sprint B-06.1).

Preparado para el futuro: implementa la forma del puerto ``LLMProvider`` pero
NO contiene lógica real (no importa el SDK de OpenAI ni hace llamadas). Si se
selecciona vía ``config.AI_PROVIDER`` y se invoca, lanza ``NotImplementedError``
y la etapa LLM degrada al guion determinista (fallback).
"""


class OpenAIProvider:
    def __init__(self, model: str = "", api_key: str | None = None) -> None:
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    def complete(self, system: str, user: str) -> str:
        raise NotImplementedError("OpenAIProvider aún no está implementado.")
