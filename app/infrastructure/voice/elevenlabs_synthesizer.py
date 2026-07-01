"""ElevenLabsSpeechSynthesizer — TTS por ElevenLabs (Sprint C-10).

Implementa el puerto ``SpeechSynthesizer`` (synthesize(text, out_path) -> bool).
Encapsula la dependencia externa: el dominio/aplicación no la conocen
(ARCH-0002 AP-006).

Consistencia de voz (regla crítica C-10): voice_id, model, stability,
similarity_boost y style se fijan en el constructor y son GLOBALES para todo el
vídeo; NO varían por escena.

Degrada con elegancia: si no hay API key o falla la red, devuelve False y el
caller continúa (el caché/render produce igualmente su informe).
"""

import os

import requests


class ElevenLabsSpeechSynthesizer:
    def __init__(
        self,
        voice_id: str,
        model: str = "eleven_multilingual_v2",
        *,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.voice_id = voice_id
        self.model = model
        self._settings = {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
        }
        self._api_key = api_key or os.environ.get("ELEVENLABS_API_KEY", "")
        self._timeout = timeout

    def synthesize(self, text: str, out_path: str) -> bool:
        text = (text or "").strip()
        if not text or not self._api_key:
            return False
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            headers = {
                "xi-api-key": self._api_key,
                "accept": "audio/mpeg",
                "content-type": "application/json",
            }
            payload = {
                "text": text,
                "model_id": self.model,
                "voice_settings": self._settings,
            }
            response = requests.post(
                url, headers=headers, json=payload, timeout=self._timeout
            )
            if response.status_code != 200 or not response.content:
                return False
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            with open(out_path, "wb") as handle:
                handle.write(response.content)
            return os.path.getsize(out_path) > 0
        except Exception:
            return False
