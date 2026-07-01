"""Configuración del VPL + factory de proveedor (selección por entorno).

Cambiar de proveedor es SOLO configuración (``VISUAL_PROVIDER``), sin tocar código:
``mock`` | ``openai`` | ``imagen`` | ``flux``.

VPL-003 añade orquestación con fallback automático: ``VPL_PROVIDER_CHAIN`` define un
orden de prioridad (p.ej. ``openai,imagen,flux,mock``) y ``VPL_FALLBACK=1`` activa la
cadena. Si no se define cadena explícita, la cadena por defecto es
``[VISUAL_PROVIDER, mock]`` (mock como red de seguridad final, siempre disponible).
"""

import os
from dataclasses import dataclass, field

from app.vpl.adapters import (
    FluxProvider,
    GoogleImagenProvider,
    HuggingFaceProvider,
    MockVisualProvider,
    OpenAIVisualProvider,
    ReplicateProvider,
)
from app.vpl.models import ProviderCapabilities
from app.vpl.provider import ProviderError, VisualProvider

# Modelos por defecto por proveedor (una sola fuente de verdad).
_DEFAULT_MODELS = {
    "mock": "mock-1",
    "openai": "gpt-image-1",
    "imagen": "imagen-3.0-generate-002",
    "flux": "flux-pro-1.1",
    "huggingface": "black-forest-labs/FLUX.1-dev",
    "replicate": "black-forest-labs/flux-dev",
}

# Variable de entorno opcional de modelo por proveedor (ver .env.example).
_MODEL_ENV = {
    "openai": "OPENAI_IMAGE_MODEL",
    "imagen": "GOOGLE_IMAGE_MODEL",
    "flux": "FLUX_IMAGE_MODEL",
    "huggingface": "HF_IMAGE_MODEL",
    "replicate": "REPLICATE_IMAGE_MODEL",
}

PROVIDER_NAMES = tuple(_DEFAULT_MODELS.keys())


def _resolve_model(name: str, model: str) -> str:
    """Modelo efectivo: explícito > env por proveedor > por defecto."""
    if model:
        return model
    env_model = os.environ.get(_MODEL_ENV.get(name, ""), "").strip()
    return env_model or _DEFAULT_MODELS.get(name, "")


@dataclass
class VPLConfig:
    provider: str = "mock"
    model: str = ""
    workers: int = 4
    max_retries: int = 2
    base_delay: float = 0.5
    cache_dir: str = os.path.join("output", ".vpl_cache")
    fallback: bool = False
    provider_chain: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "VPLConfig":
        chain_raw = os.environ.get("VPL_PROVIDER_CHAIN", "").strip()
        chain = [p.strip().lower() for p in chain_raw.split(",") if p.strip()]
        return cls(
            provider=os.environ.get("VISUAL_PROVIDER", "mock").strip().lower(),
            model=os.environ.get("VISUAL_MODEL", "").strip(),
            workers=int(os.environ.get("VPL_WORKERS", "4")),
            max_retries=int(os.environ.get("VPL_MAX_RETRIES", "2")),
            base_delay=float(os.environ.get("VPL_BASE_DELAY", "0.5")),
            cache_dir=os.environ.get("VPL_CACHE_DIR", os.path.join("output", ".vpl_cache")),
            fallback=os.environ.get("VPL_FALLBACK", "0").strip().lower() in ("1", "true", "yes", "on"),
            provider_chain=chain,
        )


def make_provider(name: str, model: str = "") -> VisualProvider:
    """Construye un único adapter por nombre (única ubicación del mapeo)."""
    name = (name or "mock").lower()
    chosen = _resolve_model(name, model)
    if name == "mock":
        return MockVisualProvider()
    if name == "openai":
        return OpenAIVisualProvider(model=chosen)
    if name == "imagen":
        return GoogleImagenProvider(model=chosen)
    if name == "flux":
        return FluxProvider(model=chosen)
    if name == "huggingface":
        return HuggingFaceProvider(model=chosen)
    if name == "replicate":
        return ReplicateProvider(model=chosen)
    raise ProviderError(f"Proveedor desconocido: {name}", transient=False)


def build_provider(config: VPLConfig) -> VisualProvider:
    """Proveedor efectivo del orquestador.

    Si ``fallback`` está activo o hay una cadena explícita, devuelve una
    ``ProviderChain`` (Primary -> Secondary -> ... -> Mock); si no, un único adapter
    (comportamiento histórico, sin cambios).
    """
    if config.fallback or config.provider_chain:
        # Import diferido: strategy importa config (evita ciclo en import-time).
        from app.vpl.strategy import build_chain

        return build_chain(config)
    return make_provider(config.provider, config.model)


def available_providers() -> dict[str, bool]:
    """Qué proveedores están listos (clave/credenciales presentes). Mock siempre."""
    status = {}
    for name in PROVIDER_NAMES:
        try:
            provider = make_provider(name)
            status[name] = bool(getattr(provider, "is_available", lambda: True)())
        except Exception:
            status[name] = False
    return status


def provider_capabilities() -> dict[str, ProviderCapabilities]:
    """Registro de capacidades de cada proveedor (incluye disponibilidad runtime)."""
    registry = {}
    for name in PROVIDER_NAMES:
        try:
            provider = make_provider(name)
            caps = getattr(provider, "capabilities", None)
            if callable(caps):
                registry[name] = caps()
        except Exception:
            continue
    return registry
