"""Abstracción de proveedor visual (provider-neutral) + mock + caching.

``VisualProvider`` es la interfaz que adaptadores reales (Imagen, Flux, SDXL,
Runway, Veo, Pika…) implementarán en el PRÓXIMO sprint. El VSC NO se ata a ninguno.
Aquí solo:
- ``VisualProvider`` (Protocol),
- ``MockVisualProvider`` (placeholder determinista, sin red, sin píxeles reales),
- ``CachingVisualProvider`` (reutiliza por ``reuse_key`` vía ``AssetCache``).
"""

from typing import Protocol

from app.vsc.cache import AssetCache
from app.vsc.models import GeneratedAsset, VisualGenerationRequest


class VisualProvider(Protocol):
    name: str

    def generate(self, request: VisualGenerationRequest) -> GeneratedAsset: ...


class MockVisualProvider:
    """Placeholder: devuelve un asset determinista (URI simulada). No genera píxeles."""

    name = "mock"

    def __init__(self) -> None:
        self.calls = 0

    def generate(self, request: VisualGenerationRequest) -> GeneratedAsset:
        self.calls += 1
        return GeneratedAsset(
            shot_id=request.shot_id,
            reuse_key=request.reuse_key,
            provider=self.name,
            uri=f"mock://{request.scene_id}/{request.shot_id}",
            prompt=request.prompt,
            cached=False,
        )


class CachingVisualProvider:
    """Decora un VisualProvider: reutiliza por ``reuse_key`` antes de generar."""

    def __init__(self, inner: VisualProvider, cache: AssetCache | None = None) -> None:
        self._inner = inner
        self._cache = cache or AssetCache()

    @property
    def name(self) -> str:
        return f"caching:{getattr(self._inner, 'name', 'provider')}"

    @property
    def cache(self) -> AssetCache:
        return self._cache

    def generate(self, request: VisualGenerationRequest) -> GeneratedAsset:
        cached = self._cache.get(request.reuse_key)
        if cached is not None:
            return GeneratedAsset(
                shot_id=request.shot_id, reuse_key=request.reuse_key,
                provider=cached.provider, uri=cached.uri, prompt=cached.prompt, cached=True,
            )
        asset = self._inner.generate(request)
        self._cache.put(asset)
        return asset
