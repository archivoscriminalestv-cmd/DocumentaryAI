"""AnthropicProvider — implementación de ``LLMProvider`` con Claude.

Encapsula el SDK de Anthropic en un único adaptador (ARCH-0002 AP-006). Es la
implementación actual movida íntegra desde el antiguo ``anthropic_client.py``;
su comportamiento es idéntico (mismo modelo, mismos parámetros, mismas trazas
``last_system``/``last_user``/``last_response`` para persistir prompt y respuesta).
El modelo se toma de ``config.settings.AI_MODEL``. La clave se lee del entorno
(``ANTHROPIC_API_KEY``); el dominio y la aplicación no conocen el SDK ni la clave.
"""

from typing import Any

import anthropic

from config.settings import AI_MODEL


class AnthropicProvider:
    def __init__(
        self,
        model: str = AI_MODEL,
        max_tokens: int = 16000,
        api_key: str | None = None,
    ) -> None:
        self._model = model
        self._max_tokens = max_tokens
        # Sin api_key explícita, el SDK resuelve ANTHROPIC_API_KEY del entorno.
        self._client = (
            anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        )
        # Trazas de la última generación (para persistencia en la capa CLI).
        self.last_system: str | None = None
        self.last_user: str | None = None
        self.last_response: dict[str, Any] | None = None

    @property
    def model(self) -> str:
        return self._model

    def complete(self, system: str, user: str) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        self.last_system = system
        self.last_user = user
        self.last_response = response.to_dict()
        return "".join(
            block.text for block in response.content if block.type == "text"
        )
