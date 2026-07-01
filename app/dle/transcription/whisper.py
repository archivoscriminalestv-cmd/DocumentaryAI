"""Transcripción por Whisper (opcional) + NullTranscriber.

``Transcriber`` es la interfaz. ``WhisperTranscriber`` usa openai-whisper si está
instalado; si no, degrada a no disponible (transcript vacío, sin inventar texto).
``NullTranscriber`` es el fallback explícito y el que usan los tests por defecto.
"""

from typing import Protocol

from app.dle import UNKNOWN
from app.dle.models import Transcript, TranscriptSegment


class Transcriber(Protocol):
    name: str

    def transcribe(self, audio_or_video_path: str) -> Transcript:
        ...


class NullTranscriber:
    name = "none"

    def transcribe(self, audio_or_video_path: str) -> Transcript:
        return Transcript(provider=self.name, language=UNKNOWN, available=False, segments=[])


class WhisperTranscriber:
    name = "whisper"

    def __init__(self, model: str = "base", loader=None) -> None:
        self._model = model
        self._loader = loader   # inyectable: () -> objeto con .transcribe(path) -> dict

    def _backend(self):
        if self._loader is not None:
            return self._loader()
        try:
            import whisper  # type: ignore
            return whisper.load_model(self._model)
        except Exception:
            return None

    def transcribe(self, audio_or_video_path: str) -> Transcript:
        backend = self._backend()
        if backend is None:
            return Transcript(provider=self.name, language=UNKNOWN, available=False, segments=[])
        try:
            result = backend.transcribe(audio_or_video_path)
        except Exception:
            return Transcript(provider=self.name, language=UNKNOWN, available=False, segments=[])
        segs = [TranscriptSegment(start=round(float(s.get("start", 0.0)), 3),
                                  end=round(float(s.get("end", 0.0)), 3),
                                  text=str(s.get("text", "")).strip())
                for s in (result.get("segments") or [])]
        return Transcript(provider=self.name, language=str(result.get("language", UNKNOWN)),
                          available=bool(segs), segments=segs)
