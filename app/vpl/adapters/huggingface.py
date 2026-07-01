"""HuggingFaceProvider — adapter REAL (HF Inference, text-to-image).

Token vía ``HF_TOKEN``. Prioriza fotografía documental usando el mejor modelo
disponible, con fallback de modelo: FLUX.1-dev -> FLUX.1-schnell -> SDXL.

Fidelidad de prompt: envía EXACTAMENTE el prompt del VSC como ``inputs``; el negative
y el tamaño viajan como parámetros del proveedor (no se reinterpreta el contenido
cinematográfico). HTTP inyectable (devuelve bytes crudos) para tests sin red.
"""

import logging
import os
import time

from app.vpl.adapters._common import constraints_size
from app.vpl.http import post_bytes
from app.vpl.models import GeneratedAsset, ProviderCapabilities
from app.vpl.provider import ProviderError

logger = logging.getLogger("vpl.huggingface")

# HF migró text-to-image al router de Inference Providers (el viejo
# api-inference.huggingface.co ya no resuelve). Provider por defecto: hf-inference.
_BASE = "https://router.huggingface.co/hf-inference/models/{model}"
_COST_PER_IMAGE = 0.0  # HF Inference (incluido en el plan); se reporta 0 estimado.

# Mejores modelos fotográficos servidos por hf-inference, en orden de preferencia.
# FLUX.1-schnell es el modelo FLUX disponible en el provider gratuito; dev/SDXL están
# deprecados ahí (410) y quedan como fallback por si se sirven en otro provider.
_DEFAULT_MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
]


def _clamp_dims(width: int, height: int, max_side: int = 1024) -> tuple[int, int]:
    """Adapta el tamaño al límite del proveedor preservando el ratio (múltiplos de 8)."""
    longest = max(width, height)
    if longest > max_side:
        scale = max_side / longest
        width, height = int(width * scale), int(height * scale)
    width = max(8, (width // 8) * 8)
    height = max(8, (height // 8) * 8)
    return width, height


class HuggingFaceProvider:
    name = "huggingface"

    def __init__(self, model: str = "", models: list | None = None, timeout: float = 180.0,
                 http_post_bytes=None, base: str = "") -> None:
        # Orden de modelos: el explícito/env primero, luego el resto de candidatos.
        primary = model or os.environ.get("HF_IMAGE_MODEL", "").strip()
        candidates = list(models) if models else list(_DEFAULT_MODELS)
        if primary:
            candidates = [primary] + [m for m in candidates if m != primary]
        self._models = candidates
        self.model = self._models[0]
        self._timeout = timeout
        self._post_bytes = http_post_bytes or post_bytes
        # Provider/endpoint configurable (HF_INFERENCE_BASE) para otros providers.
        self._base = base or os.environ.get("HF_INFERENCE_BASE", "").strip() or _BASE

    def is_available(self) -> bool:
        return bool(os.environ.get("HF_TOKEN"))

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name, model=self.model, cost_per_image=_COST_PER_IMAGE,
            native_negative_prompt=True, native_seed=True,
            max_width=1024, max_height=1024,
            aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4"],
            async_polling=False, self_hostable=True, requires_api_key="HF_TOKEN",
            available=self.is_available(),
        )

    def _build_body(self, request, width: int, height: int) -> dict:
        parameters = {"width": width, "height": height}
        if request.negative_prompt:
            parameters["negative_prompt"] = request.negative_prompt
        if request.seed:
            parameters["seed"] = int(request.seed)
        # ``inputs`` = prompt EXACTO del VSC (sin reinterpretar).
        return {"inputs": request.prompt, "parameters": parameters}

    def generate(self, request) -> GeneratedAsset:
        token = os.environ.get("HF_TOKEN")
        if not token:
            raise ProviderError("HF_TOKEN no definida", transient=False)

        w0, h0 = constraints_size(request)
        width, height = _clamp_dims(w0, h0)
        headers = {"Authorization": f"Bearer {token}", "Accept": "image/png"}
        body = self._build_body(request, width, height)

        last_error: Exception | None = None
        for model in self._models:
            url = self._base.format(model=model)
            started = time.perf_counter()
            logger.info("HF generate shot=%s model=%s %dx%d", request.shot_id, model, width, height)
            try:
                data, content_type = self._post_bytes(url, body, headers, self._timeout)
            except ProviderError as exc:
                last_error = exc
                logger.warning("HF modelo '%s' falló (%s) -> siguiente modelo", model, exc)
                continue
            if "image" not in content_type.lower() and len(data) < 1024:
                last_error = ProviderError(
                    f"HF '{model}' no devolvió imagen (content-type={content_type})", transient=True)
                continue
            return GeneratedAsset(
                shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=model,
                prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
                width=width, height=height, generation_time=round(time.perf_counter() - started, 3),
                cost=_COST_PER_IMAGE, reuse_key=request.reuse_key,
                metadata={"endpoint": url, "content_type": content_type}, image_bytes=data,
            )

        raise ProviderError(
            f"HF: ningún modelo disponible ({[m for m in self._models]}): {last_error}",
            transient=bool(getattr(last_error, "transient", False)),
        ) from last_error
