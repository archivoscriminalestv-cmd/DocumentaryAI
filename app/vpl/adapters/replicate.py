"""ReplicateProvider — adapter REAL (Replicate predictions API).

Token vía ``REPLICATE_API_TOKEN``. Flujo: create prediction -> poll -> download.
Prioriza modelos fotográficos FLUX: flux-dev -> flux-schnell (fallback de modelo).

Fidelidad de prompt: envía EXACTAMENTE el prompt del VSC; solo adapta parámetros del
proveedor (aspect_ratio, output_format, seed). HTTP inyectable para tests sin red.
"""

import logging
import os
import time

from app.vpl.adapters._common import constraints_size
from app.vpl.http import get_bytes, get_json, post_json
from app.vpl.models import GeneratedAsset, ProviderCapabilities
from app.vpl.provider import ProviderError

logger = logging.getLogger("vpl.replicate")

_ENDPOINT = "https://api.replicate.com/v1/models/{model}/predictions"
_COST_PER_IMAGE = 0.003  # estimado FLUX schnell/dev en Replicate (orientativo, USD).

_DEFAULT_MODELS = [
    "black-forest-labs/flux-dev",
    "black-forest-labs/flux-schnell",
]


def _aspect_ratio(width: int, height: int) -> str:
    ratio = width / height if height else 1.0
    for label, value in (("16:9", 1.777), ("4:3", 1.333), ("1:1", 1.0), ("9:16", 0.5625), ("3:4", 0.75)):
        if abs(ratio - value) < 0.08:
            return label
    return "16:9"


class ReplicateProvider:
    name = "replicate"

    def __init__(self, model: str = "", models: list | None = None, timeout: float = 180.0,
                 http_post=None, http_get_json=None, http_get_bytes=None,
                 poll_interval: float = 1.5, max_polls: int = 80, sleep=time.sleep) -> None:
        primary = model or os.environ.get("REPLICATE_IMAGE_MODEL", "").strip()
        candidates = list(models) if models else list(_DEFAULT_MODELS)
        if primary:
            candidates = [primary] + [m for m in candidates if m != primary]
        self._models = candidates
        self.model = self._models[0]
        self._timeout = timeout
        self._post = http_post or post_json
        self._get_json = http_get_json or get_json
        self._get_bytes = http_get_bytes or get_bytes
        self._poll_interval = poll_interval
        self._max_polls = max_polls
        self._sleep = sleep

    def is_available(self) -> bool:
        return bool(os.environ.get("REPLICATE_API_TOKEN"))

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name, model=self.model, cost_per_image=_COST_PER_IMAGE,
            native_negative_prompt=False, native_seed=True,
            max_width=1440, max_height=1440,
            aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4", "21:9"],
            async_polling=True, self_hostable=False, requires_api_key="REPLICATE_API_TOKEN",
            available=self.is_available(),
        )

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def generate(self, request) -> GeneratedAsset:
        token = os.environ.get("REPLICATE_API_TOKEN")
        if not token:
            raise ProviderError("REPLICATE_API_TOKEN no definida", transient=False)

        width, height = constraints_size(request)
        headers = self._headers(token)
        inputs = {
            "prompt": request.prompt,                  # EXACTO del VSC
            "aspect_ratio": _aspect_ratio(width, height),
            "output_format": "png",
            "num_outputs": 1,
        }
        if request.seed:
            inputs["seed"] = int(request.seed)

        last_error: Exception | None = None
        for model in self._models:
            url = _ENDPOINT.format(model=model)
            started = time.perf_counter()
            logger.info("Replicate submit shot=%s model=%s", request.shot_id, model)
            try:
                prediction = self._post(url, {"input": inputs}, headers, self._timeout)
                image_url = self._await_output(prediction, headers)
                data = self._get_bytes(image_url, {}, self._timeout)
            except ProviderError as exc:
                last_error = exc
                logger.warning("Replicate modelo '%s' falló (%s) -> siguiente", model, exc)
                continue
            return GeneratedAsset(
                shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=model,
                prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
                width=width, height=height, generation_time=round(time.perf_counter() - started, 3),
                cost=_COST_PER_IMAGE, reuse_key=request.reuse_key,
                metadata={"endpoint": url, "aspect_ratio": inputs["aspect_ratio"]}, image_bytes=data,
            )

        raise ProviderError(
            f"Replicate: ningún modelo disponible ({self._models}): {last_error}",
            transient=bool(getattr(last_error, "transient", False)),
        ) from last_error

    def _await_output(self, prediction: dict, headers: dict) -> str:
        status = str(prediction.get("status", "")).lower()
        get_url = (prediction.get("urls") or {}).get("get")
        for _ in range(self._max_polls):
            if status in ("succeeded",):
                return self._extract_url(prediction)
            if status in ("failed", "canceled"):
                raise ProviderError(f"Replicate {status}: {prediction.get('error')}", transient=False)
            if not get_url:
                raise ProviderError(f"Replicate sin URL de polling: {prediction}", transient=False)
            self._sleep(self._poll_interval)
            prediction = self._get_json(get_url, headers, self._timeout)
            status = str(prediction.get("status", "")).lower()
        raise ProviderError("Replicate: timeout esperando el resultado", transient=True)

    @staticmethod
    def _extract_url(prediction: dict) -> str:
        output = prediction.get("output")
        if isinstance(output, list) and output:
            return str(output[0])
        if isinstance(output, str) and output:
            return output
        raise ProviderError(f"Replicate succeeded sin output: {prediction}", transient=False)
