"""Verifica que el provider se selecciona SOLO por configuración + fallback."""

import pytest

from app.infrastructure.llm import (
    AnthropicProvider,
    GeminiProvider,
    OpenAIProvider,
    create_llm_provider,
)
from app.infrastructure.llm import factory


def test_anthropic_selected_when_configured_with_key(monkeypatch):
    monkeypatch.setattr(factory, "AI_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    provider = create_llm_provider()

    assert isinstance(provider, AnthropicProvider)


def test_anthropic_without_key_falls_back_to_none(monkeypatch):
    monkeypatch.setattr(factory, "AI_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    assert create_llm_provider() is None


def test_provider_switch_is_config_only(monkeypatch):
    monkeypatch.setattr(factory, "AI_PROVIDER", "openai")
    assert isinstance(create_llm_provider(), OpenAIProvider)

    monkeypatch.setattr(factory, "AI_PROVIDER", "gemini")
    assert isinstance(create_llm_provider(), GeminiProvider)


def test_unknown_provider_returns_none(monkeypatch):
    monkeypatch.setattr(factory, "AI_PROVIDER", "does-not-exist")
    assert create_llm_provider() is None


def test_stub_providers_are_not_implemented():
    for stub in (OpenAIProvider(), GeminiProvider()):
        with pytest.raises(NotImplementedError):
            stub.complete("system", "user")
