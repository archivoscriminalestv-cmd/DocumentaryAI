"""Channel identity — identidad de narrador GLOBAL e INMUTABLE (Sprint C-11).

Fuente única de verdad de la "DocumentaryAI narrator identity". Toda la narración
del pipeline DEBE usar este contrato de voz; no se permite variación por escena ni
override por módulo. Es un objeto inmutable (``frozen``).
"""

from dataclasses import dataclass

# Contrato de voz (C-11): valores fijos para todo el pipeline.
VOICE_ID = "5egO01tkUjEzu7xSSE8M"
VOICE_MODEL = "eleven_multilingual_v2"
VOICE_STABILITY = 0.5
VOICE_SIMILARITY_BOOST = 0.75
VOICE_STYLE = 0.2
VOICE_PROVIDER = "elevenlabs"


@dataclass(frozen=True)
class ChannelIdentity:
    voice_id: str = VOICE_ID
    model: str = VOICE_MODEL
    stability: float = VOICE_STABILITY
    similarity_boost: float = VOICE_SIMILARITY_BOOST
    style: float = VOICE_STYLE
    provider: str = VOICE_PROVIDER

    def voice_profile(self) -> dict[str, str]:
        """Resumen para el informe (voice_id + provider)."""
        return {"voice_id": self.voice_id, "provider": self.provider}


# Instancia única, inmutable, compartida por todo el sistema.
CHANNEL_IDENTITY = ChannelIdentity()
