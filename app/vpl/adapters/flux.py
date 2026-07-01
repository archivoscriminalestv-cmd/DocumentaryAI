"""FluxProvider — adapter REAL (Black Forest Labs API) + self-hosted futuro.

API key vía ``FLUX_API_KEY``. Base URL configurable (``FLUX_API_URL``) para apuntar
a un despliegue self-hosted compatible. Flujo: submit -> poll -> download. HTTP
inyectable (post/get_json/get_bytes) para tests sin red. Sin negative nativo: se
funde como "Avoid:".
"""

import logging
import os
import time

from app.vpl.adapters._common import constraints_size, with_avoid
from app.vpl.http import get_bytes, get_json, post_json
from app.vpl.models import GeneratedAsset, ProviderCapabilities
from app.vpl.provider import ProviderError

logger = logging.getLogger("vpl.flux")

_DEFAULT_BASE = "https://api.bfl.ml/v1"
_COST_PER_IMAGE = 0.05


class FluxProvider:
    name = "flux"

    def __init__(
        self,
        model: str = "flux-pro-1.1",
        timeout: float = 120.0,
        base_url: str | None = None,
        http_post=None,
        http_get_json=None,
        http_get_bytes=None,
        poll_interval: float = 1.0,
        max_polls: int = 60,
        sleep=time.sleep,
    ) -> None:
        self.model = model
        self._timeout = timeout
        self._base = (base_url or os.environ.get("FLUX_API_URL") or _DEFAULT_BASE).rstrip("/")
        self._post = http_post or post_json
        self._get_json = http_get_json or get_json
        self._get_bytes = http_get_bytes or get_bytes
        self._poll_interval = poll_interval
        self._max_polls = max_polls
        self._sleep = sleep

    def is_available(self) -> bool:
        return bool(os.environ.get("FLUX_API_KEY"))

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name, model=self.model, cost_per_image=_COST_PER_IMAGE,
            native_negative_prompt=False, native_seed=True,
            max_width=1440, max_height=1440,
            aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4", "21:9"],
            async_polling=True, self_hostable=True, requires_api_key="FLUX_API_KEY",
            available=self.is_available(),
        )

    def _build(self, request, api_key: str):
        width, height = constraints_size(request)
        body = {
            "prompt": with_avoid(request.prompt, request.negative_prompt),
            "width": width,
            "height": height,
            "seed": int(request.seed),
        }
        headers = {"x-key": api_key, "accept": "application/json"}
        return f"{self._base}/{self.model}", body, headers, (width, height)

    def generate(self, request) -> GeneratedAsset:
        api_key = os.environ.get("FLUX_API_KEY")
        if not api_key:
            raise ProviderError("FLUX_API_KEY no definida", transient=False)

        url, body, headers, (width, height) = self._build(request, api_key)
        started = time.perf_counter()
        logger.info("Flux submit shot=%s model=%s", request.shot_id, self.model)
        submit = self._post(url, body, headers, self._timeout)
        job_id = submit.get("id")
        if not job_id:
            raise ProviderError(f"Flux no devolvió id de trabajo: {submit}", transient=False)

        result_url = submit.get("polling_url") or f"{self._base}/get_result?id={job_id}"
        image_url = self._poll(result_url, headers)
        image_bytes = self._get_bytes(image_url, {}, self._timeout)

        return GeneratedAsset(
            shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=self.model,
            prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
            width=width, height=height, generation_time=round(time.perf_counter() - started, 3),
            cost=_COST_PER_IMAGE, reuse_key=request.reuse_key,
            metadata={"base_url": self._base, "job_id": job_id}, image_bytes=image_bytes,
        )

    def _poll(self, result_url: str, headers: dict) -> str:
        for _ in range(self._max_polls):
            data = self._get_json(result_url, headers, self._timeout)
            status = str(data.get("status", "")).lower()
            if status in ("ready", "succeeded", "completed"):
                result = data.get("result") or {}
                sample = result.get("sample") or data.get("sample")
                if not sample:
                    raise ProviderError(f"Flux Ready sin imagen: {data}", transient=False)
                return sample
            if status in ("error", "failed"):
                raise ProviderError(f"Flux falló: {data}", transient=False)
            self._sleep(self._poll_interval)
        raise ProviderError("Flux: timeout esperando el resultado", transient=True)
