"""Adapters de proveedores del VPL (única ubicación de lógica provider-specific)."""

from app.vpl.adapters.flux import FluxProvider
from app.vpl.adapters.google_imagen import GoogleImagenProvider
from app.vpl.adapters.huggingface import HuggingFaceProvider
from app.vpl.adapters.mock import MockVisualProvider
from app.vpl.adapters.openai import OpenAIVisualProvider
from app.vpl.adapters.replicate import ReplicateProvider

__all__ = [
    "MockVisualProvider",
    "OpenAIVisualProvider",
    "GoogleImagenProvider",
    "FluxProvider",
    "HuggingFaceProvider",
    "ReplicateProvider",
]
