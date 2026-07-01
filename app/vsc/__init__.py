"""Visual Scene Compiler (VSC).

ShotExecutionRequest (VAI) + SceneVisualContext  ->  VisualGenerationRequest
(normalizado, provider-agnóstico, con continuidad de escena). El proveedor real se
conecta en el próximo sprint vía ``VisualProvider``. Ver README.md.
"""

from app.vsc.cache import AssetCache
from app.vsc.compiler import VisualSceneCompiler
from app.vsc.context_adapter import to_vai_context
from app.vsc.models import (
    GeneratedAsset,
    GlobalStyle,
    SceneVisualContext,
    VisualGenerationRequest,
)
from app.vsc.provider import CachingVisualProvider, MockVisualProvider, VisualProvider

__all__ = [
    "VisualSceneCompiler",
    "SceneVisualContext",
    "VisualGenerationRequest",
    "GlobalStyle",
    "GeneratedAsset",
    "AssetCache",
    "VisualProvider",
    "MockVisualProvider",
    "CachingVisualProvider",
    "to_vai_context",
]
