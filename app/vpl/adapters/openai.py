"""OpenAIVisualProvider — adapter REAL (OpenAI Images API, modelo gpt-image-1).

Ejecuta EXACTAMENTE el prompt compilado por el VSC (los negativos se funden como
cláusula "Avoid:" porque la API de imágenes de OpenAI no tiene negative_prompt
nativo). API key vía ``OPENAI_API_KEY``. HTTP inyectable (tests sin red).
"""

import base64
import logging
import os
import time

from app.vpl.adapters._common import constraints_size, openai_size, with_avoid
from app.vpl.http import post_json
from app.vpl.models import GeneratedAsset, ProviderCapabilities
from app.vpl.provider import ProviderError

logger = logging.getLogger("vpl.openai")

_ENDPOINT = "https://api.openai.com/v1/images/generations"
_COST_PER_IMAGE = 0.04  # orientativo (USD), solo para el manifest


class OpenAIVisualProvider:
    name = "openai"

    def __init__(self, model: str = "gpt-image-1", timeout: float = 120.0, http_post=None) -> None:
        self.model = model
        self._timeout = timeout
        self._http_post = http_post or post_json

    def is_available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name, model=self.model, cost_per_image=_COST_PER_IMAGE,
            native_negative_prompt=False, native_seed=False,
            max_width=1536, max_height=1536,
            aspect_ratios=["1:1", "16:9", "9:16"],
            async_polling=False, self_hostable=False, requires_api_key="OPENAI_API_KEY",
            available=self.is_available(),
        )

    def _build(self, request, api_key: str):
        width, height = constraints_size(request)
        size = openai_size(width, height)
        body = {
            "model": self.model,
            "prompt": with_avoid(request.prompt, request.negative_prompt),
            "size": size,
            "n": 1,
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        return _ENDPOINT, body, headers, size

    @staticmethod
    def _parse(response: dict) -> bytes:
        try:
            return base64.b64decode(response["data"][0]["b64_json"])
        except Exception as exc:
            raise ProviderError(f"respuesta OpenAI inesperada: {exc}", transient=False) from exc

    def generate(self, request) -> GeneratedAsset:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OPENAI_API_KEY no definida", transient=False)

        url, body, headers, size = self._build(request, api_key)
        started = time.perf_counter()
        logger.info("OpenAI generate shot=%s model=%s size=%s", request.shot_id, self.model, size)
        response = self._http_post(url, body, headers, self._timeout)
        image_bytes = self._parse(response)

        width, height = (int(x) for x in size.split("x"))
        return GeneratedAsset(
            shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=self.model,
            prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
            width=width, height=height, generation_time=round(time.perf_counter() - started, 3),
            cost=_COST_PER_IMAGE, reuse_key=request.reuse_key,
            metadata={"size": size, "endpoint": url}, image_bytes=image_bytes,
        )
