"""Provider Router — selección AUTOMÁTICA de proveedor con prioridad y fallback.

DocumentaryAI no elige el proveedor manualmente: el router prueba los proveedores en
orden de prioridad y, ante un fallo (error, imagen vacía o corrupta), pasa
automáticamente al siguiente. Nunca detiene el render mientras quede un proveedor.

Diferencias con ``ProviderChain`` (VPL-003):
- **Orden de prioridad fijo** del sprint VPL-004 (Imagen > OpenAI > HF > Replicate).
- **Validación de calidad**: la imagen devuelta se verifica (no vacía, no corrupta);
  si no pasa, se regenera con el siguiente proveedor.
- **Circuit-breaker**: si un proveedor falla de forma permanente (auth, facturación,
  modelo no disponible), se deshabilita para el resto del render (no se reintenta en
  cada plano), pero los demás siguen disponibles.
- **Sin mock**: el router solo enruta a proveedores reales (objetivo: imágenes reales).

El asset resultante anota en metadata qué proveedores se intentaron y cuál ganó.
"""

import io
import logging
import threading

from app.vpl.models import GeneratedAsset
from app.vpl.provider import ProviderError

# Orden de prioridad del Provider Router (VPL-004).
PRIORITY = ["imagen", "openai", "huggingface", "replicate"]

# Palabras que indican un fallo NO recuperable aunque el HTTP sea 429/5xx
# (p.ej. límite de facturación): se trata como permanente para el circuit-breaker.
_HARD_FAILURE_HINTS = ("billing", "quota", "insufficient", "credit", "payment",
                       "exceeded your current", "hard limit")


def validate_image(asset: GeneratedAsset) -> None:
    """Valida que el asset trae una imagen real (no vacía, no corrupta).

    Lanza ``ProviderError`` (transient) si la imagen no es válida, para que el router
    regenere con el siguiente proveedor.
    """
    data = asset.image_bytes or b""
    if len(data) < 100:
        raise ProviderError(f"imagen vacía/insuficiente ({len(data)} bytes)", transient=True)
    try:
        from PIL import Image  # import diferido (Pillow ya es dependencia del proyecto)

        with Image.open(io.BytesIO(data)) as img:
            img.verify()
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"imagen corrupta: {exc}", transient=True) from exc


def _is_hard_failure(exc: Exception) -> bool:
    if not getattr(exc, "transient", False):
        return True  # permanente (4xx/auth/etc.)
    msg = str(exc).lower()
    return any(hint in msg for hint in _HARD_FAILURE_HINTS)


class ProviderRouter:
    def __init__(self, providers: list, *, validate=validate_image, logger=None) -> None:
        if not providers:
            raise ProviderError("ProviderRouter requiere al menos un proveedor", transient=False)
        self._providers = providers
        self._validate = validate
        self._log = logger or logging.getLogger("vpl.router")
        self._disabled: set[str] = set()
        self._lock = threading.Lock()
        self.name = "router:" + ">".join(p.name for p in providers)
        self.model = getattr(providers[0], "model", "")

    @property
    def providers(self) -> list:
        return list(self._providers)

    def is_available(self) -> bool:
        return any(getattr(p, "is_available", lambda: True)() for p in self._providers)

    def capabilities(self):
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
            with self._lock:
                if name in self._disabled:
                    attempted.append(f"{name}:disabled")
                    continue
            if not getattr(provider, "is_available", lambda: True)():
                attempted.append(f"{name}:unavailable")
                last_error = ProviderError(f"{name} no configurado", transient=False)
                continue
            try:
                asset = provider.generate(request)
                self._validate(asset)
            except ProviderError as exc:
                tag = "invalid_image" if "imagen" in str(exc).lower() else "error"
                attempted.append(f"{name}:{tag}")
                last_error = exc
                if _is_hard_failure(exc):
                    with self._lock:
                        self._disabled.add(name)
                    self._log.warning("router: '%s' deshabilitado (fallo duro: %s)", name, exc)
                else:
                    self._log.warning("router: '%s' falló (%s) -> siguiente", name, exc)
                continue
            except Exception as exc:  # noqa: BLE001
                attempted.append(f"{name}:error")
                last_error = ProviderError(str(exc), transient=False)
                with self._lock:
                    self._disabled.add(name)
                self._log.warning("router: '%s' error inesperado, deshabilitado (%s)", name, exc)
                continue

            meta = asset.metadata if isinstance(asset.metadata, dict) else {}
            meta["router_attempted"] = attempted + [f"{name}:ok"]
            meta["router_winner"] = name
            meta["chain_winner"] = name  # compat con telemetría VPL-003
            meta["router_fallback"] = bool(attempted)
            asset.metadata = meta
            if attempted:
                self._log.info("router: '%s' generó shot=%s tras %s",
                               name, getattr(request, "shot_id", "?"), attempted)
            return asset

        raise ProviderError(
            f"router: todos los proveedores fallaron ({attempted})",
            transient=bool(getattr(last_error, "transient", False)),
        ) from last_error


def build_router(valid_names: list, *, logger=None) -> ProviderRouter:
    """Construye el router en ORDEN DE PRIORIDAD, solo con proveedores válidos.

    ``valid_names`` son los proveedores que pasaron el preflight; se ordenan según
    ``PRIORITY`` (los no presentes se omiten). No incluye mock.
    """
    from app.vpl.config import make_provider

    ordered = [n for n in PRIORITY if n in valid_names]
    # Cualquier válido fuera de la lista de prioridad (por si se amplía) va al final.
    ordered += [n for n in valid_names if n not in ordered and n != "mock"]
    if not ordered:
        raise ProviderError("No hay proveedores reales válidos para el router", transient=False)
    return ProviderRouter([make_provider(n) for n in ordered], logger=logger)
