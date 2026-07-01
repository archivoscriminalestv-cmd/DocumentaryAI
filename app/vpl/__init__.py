"""Visual Provider Layer (VPL).

Frontera de ejecución entre la planificación cinematográfica (VIS/VAI/VSC) y
cualquier tecnología de generación de imágenes. Consume VisualGenerationRequests y
produce GeneratedAssets reales (orquestador + cola + caché + reintentos + manifest),
totalmente provider-agnóstico (lógica específica solo en adapters). Ver README.md.
"""

from app.vpl.benchmark import BenchmarkReport, BenchmarkResult, BenchmarkRunner
from app.vpl.config import (
    VPLConfig,
    available_providers,
    build_provider,
    make_provider,
    provider_capabilities,
)
from app.vpl.models import (
    GeneratedAsset,
    GenerationFailure,
    GenerationManifest,
    ProviderCapabilities,
)
from app.vpl.orchestrator import VisualGenerationOrchestrator
from app.vpl.provider import ProviderError, VisualProvider
from app.vpl.router import ProviderRouter, build_router, validate_image
from app.vpl.strategy import ProviderChain, build_chain

__all__ = [
    "VisualGenerationOrchestrator",
    "VPLConfig",
    "build_provider",
    "make_provider",
    "available_providers",
    "provider_capabilities",
    "VisualProvider",
    "ProviderError",
    "ProviderCapabilities",
    "ProviderChain",
    "build_chain",
    "ProviderRouter",
    "build_router",
    "validate_image",
    "BenchmarkRunner",
    "BenchmarkReport",
    "BenchmarkResult",
    "GeneratedAsset",
    "GenerationManifest",
    "GenerationFailure",
]
