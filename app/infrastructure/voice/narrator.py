"""Narrator factory — construye el sintetizador con la identidad de canal (C-11).

Centraliza la creación del ``ElevenLabsSpeechSynthesizer`` con el contrato de voz
GLOBAL e INMUTABLE de ``CHANNEL_IDENTITY``. Ningún módulo debe construir la voz
con otros parámetros.

C-11.5 añade ``build_speech_synthesizer`` y ``runtime_status``: seleccionan voz
según los secretos (ElevenLabs si hay clave; SAPI como fallback en DEV; fallo duro
en PROD). No se modifica la lógica de ElevenLabs: solo se inyecta la clave.
"""

from app.application.channel_identity import CHANNEL_IDENTITY
from app.infrastructure.config.runtime_secrets import SecretsManager
from app.infrastructure.voice.elevenlabs_synthesizer import ElevenLabsSpeechSynthesizer


def build_elevenlabs_narrator(api_key: str | None = None) -> ElevenLabsSpeechSynthesizer:
    return ElevenLabsSpeechSynthesizer(
        voice_id=CHANNEL_IDENTITY.voice_id,
        model=CHANNEL_IDENTITY.model,
        stability=CHANNEL_IDENTITY.stability,
        similarity_boost=CHANNEL_IDENTITY.similarity_boost,
        style=CHANNEL_IDENTITY.style,
        api_key=api_key,
    )


def build_speech_synthesizer(secrets: SecretsManager):
    """Selecciona el sintetizador según los secretos/entorno (C-11.5).

    - Hay ELEVENLABS_API_KEY  → ElevenLabs (identidad de canal).
    - Sin clave y PROD        → fallo duro (``require`` lanza RuntimeError).
    - Sin clave y DEV         → fallback a SAPI (el pipeline siempre corre).
    """
    if secrets.get("ELEVENLABS_API_KEY"):
        return build_elevenlabs_narrator(api_key=secrets.require("ELEVENLABS_API_KEY"))
    if secrets.is_production():
        secrets.require("ELEVENLABS_API_KEY")  # PROD: clave obligatoria -> RuntimeError
    from app.infrastructure.voice.sapi_synthesizer import SapiSpeechSynthesizer

    return SapiSpeechSynthesizer()


def runtime_status(secrets: SecretsManager) -> dict:
    """Estado de runtime (contrato de salida C-11.5)."""
    elevenlabs_available = secrets.get("ELEVENLABS_API_KEY") is not None
    mode = secrets.runtime_mode()
    return {
        "runtime_mode": mode,
        "secrets_loaded": secrets.loaded,
        "elevenlabs_available": elevenlabs_available,
        # SAPI solo sustituye en DEV cuando no hay clave; en PROD sería fallo duro.
        "fallback_active": (not elevenlabs_available) and (mode != "production"),
    }
