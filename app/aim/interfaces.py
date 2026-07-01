"""Interfaces (Protocols) del AIM — independientes del proveedor concreto.

Los motores dependen de estas capacidades, NUNCA de un proveedor concreto. Un adaptador real
(futuro) implementa la Protocol de su categoría + ``health()``. Esto permite añadir/sustituir
proveedores sin tocar ningún motor.
"""

from typing import Any, Protocol


class AIMProvider(Protocol):
    name: str

    def health(self, *, prober=None) -> Any:
        """Comprueba conectividad/credenciales SIN descargar contenido."""
        ...


class LLMProvider(AIMProvider, Protocol):
    def complete(self, system: str, user: str) -> str: ...


class EmbeddingProvider(AIMProvider, Protocol):
    def embed(self, text: str) -> list[float]: ...


class ImageProvider(AIMProvider, Protocol):
    def generate_image(self, prompt: str) -> Any: ...


class VideoProvider(AIMProvider, Protocol):
    def generate_video(self, prompt: str) -> Any: ...


class VoiceProvider(AIMProvider, Protocol):
    def synthesize(self, text: str, voice_id: str) -> Any: ...


class MusicProvider(AIMProvider, Protocol):
    def generate_music(self, prompt: str) -> Any: ...


class OCRProvider(AIMProvider, Protocol):
    def extract_text(self, image_ref: str) -> str: ...


class TranslationProvider(AIMProvider, Protocol):
    def translate(self, text: str, target_language: str) -> str: ...


class EvidenceProvider(AIMProvider, Protocol):
    def search(self, query: str) -> list[Any]: ...


class MapsProvider(AIMProvider, Protocol):
    def lookup(self, place: str) -> Any: ...
