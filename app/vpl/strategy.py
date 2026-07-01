"""Estrategia de proveedores con prioridad y fallback automático (VPL-003).

``ProviderChain`` envuelve una lista ordenada de proveedores (Primary -> Secondary
-> Tertiary -> ... -> Mock) y, ante un fallo o indisponibilidad de uno, pasa
automáticamente al siguiente. Implementa la misma interfaz ``VisualProvider``, por
lo que el orquestador lo usa sin saber que hay una cadena detrás.

Garantía: si ``mock`` está en la cadena (la cadena por defecto siempre lo incluye
como última red de seguridad), el pipeline nunca queda sin imagen.

La cadena registra en ``GeneratedAsset.metadata`` qué proveedores se intentaron y
cuáles fallaron, para trazabilidad en el manifest.
"""

import logging

from app.vpl.models import GeneratedAsset
from app.vpl.provider import ProviderError


class ProviderChain:
    """Cadena de proveedores con fallback en orden de prioridad."""

    def __init__(self, providers: list, logger=None) -> None:
        if not providers:
            raise ProviderError("ProviderChain requiere al menos un proveedor", transient=False)
        self._providers = providers
        self._log = logger or logging.getLogger("vpl.strategy")
        self.name = ">".join(p.name for p in providers)
        # ``model`` del primario (informativo a nivel manifest; el asset trae el real).
        self.model = getattr(providers[0], "model", "")

    @property
    def providers(self) -> list:
        return list(self._providers)

    def is_available(self) -> bool:
        # La cadena está disponible si CUALQUIER eslabón lo está (mock siempre lo está).
        return any(getattr(p, "is_available", lambda: True)() for p in self._providers)

    def capabilities(self):
        # Capacidades del primario disponible (el que mandará en el caso normal).
        for p in self._providers:
            if getattr(p, "is_available", lambda: True)():
                caps = getattr(p, "capabilities", None)
                if callable(caps):
                    return caps()
        return getattr(self._providers[0], "capabilities", lambda: None)()

    def generate(self, request) -> GeneratedAsset:
        attempted: list[str] = []
        last_error: Exception | None = None

        for provider in self._providers:
            name = provider.name
            if not getattr(provider, "is_available", lambda: True)():
                self._log.info("chain: omito '%s' (no configurado)", name)
                attempted.append(f"{name}:unavailable")
                last_error = ProviderError(f"{name} no configurado", transient=False)
                continue
            try:
                asset = provider.generate(request)
                if attempted:  # hubo fallback(s) previos
                    self._log.info("chain: '%s' generó shot=%s tras fallback %s",
                                   name, getattr(request, "shot_id", "?"), attempted)
                meta = asset.metadata if isinstance(asset.metadata, dict) else {}
                meta["chain_attempted"] = attempted + [f"{name}:ok"]
                meta["chain_winner"] = name
                meta["chain_fallback"] = bool(attempted)
                asset.metadata = meta
                return asset
            except ProviderError as exc:
                self._log.warning("chain: '%s' falló (%s) -> siguiente proveedor", name, exc)
                attempted.append(f"{name}:error")
                last_error = exc
            except Exception as exc:  # un adapter mal portado no debe tumbar la cadena
                self._log.warning("chain: '%s' error inesperado (%s) -> siguiente", name, exc)
                attempted.append(f"{name}:error")
                last_error = ProviderError(str(exc), transient=False)

        # Todos fallaron. Propaga conservando transitoriedad (para el retry del orquestador).
        transient = bool(getattr(last_error, "transient", False))
        raise ProviderError(
            f"Todos los proveedores fallaron ({attempted})", transient=transient
        ) from last_error


def resolve_chain_names(config) -> list[str]:
    """Orden de prioridad efectivo. Garantiza ``mock`` como último eslabón."""
    from app.vpl.config import PROVIDER_NAMES

    names = list(config.provider_chain) if config.provider_chain else [config.provider]
    # Normaliza, descarta desconocidos y duplicados preservando el orden.
    seen, ordered = set(), []
    for n in names:
        n = (n or "").lower()
        if n in PROVIDER_NAMES and n not in seen:
            seen.add(n)
            ordered.append(n)
    if not ordered:
        ordered = ["mock"]
    if "mock" not in seen:  # red de seguridad final
        ordered.append("mock")
    return ordered


def build_chain(config, logger=None) -> ProviderChain:
    from app.vpl.config import make_provider

    names = resolve_chain_names(config)
    # El modelo de VISUAL_MODEL solo aplica al primario configurado.
    providers = [
        make_provider(n, config.model if n == config.provider else "")
        for n in names
    ]
    return ProviderChain(providers, logger=logger)
