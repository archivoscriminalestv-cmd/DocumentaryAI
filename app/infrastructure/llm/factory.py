"""Factory de proveedores LLM (Sprint B-06.1).

Selecciona la implementación de ``LLMProvider`` según ``config.AI_PROVIDER`` y
``config.AI_MODEL``. Cambiar de proveedor se hace SOLO en config; ningún otro
módulo necesita cambios.

Devuelve ``None`` cuando el proveedor seleccionado no está disponible (p. ej.
``anthropic`` sin ``ANTHROPIC_API_KEY``, o un nombre desconocido); la capa CLI
interpreta ``None`` como "sin proveedor" y degrada al guion determinista
(fallback, requisito 9).
"""

import os

from app.application.llm_provider import LLMProvider
from app.infrastructure.llm.anthropic_provider import AnthropicProvider
from app.infrastructure.llm.gemini_provider import GeminiProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider
from config.settings import AI_MODEL, AI_PROVIDER


def create_llm_provider() -> LLMProvider | None:
    provider = (AI_PROVIDER or "").strip().lower()

    if provider == "anthropic":
        # La clave se lee del entorno; sin ella no hay proveedor -> fallback.
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return None
        return AnthropicProvider(model=AI_MODEL)

    if provider == "openai":
        return OpenAIProvider(model=AI_MODEL)

    if provider == "gemini":
        return GeminiProvider(model=AI_MODEL)

    return None  # proveedor desconocido -> fallback
