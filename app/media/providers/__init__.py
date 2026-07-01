"""Providers de generación de media (Fase 1 MGL / Fase 2 real / Fase B orquestación)."""

from app.media.providers.provider_registry import (
    ProviderHealth,
    ProviderMetadata,
    ProviderRegistry,
)
from app.media.providers.real_image import RealImageProvider

__all__ = [
    "RealImageProvider",
    "ProviderRegistry",
    "ProviderMetadata",
    "ProviderHealth",
]
