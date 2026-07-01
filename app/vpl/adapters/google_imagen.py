"""GoogleImagenProvider — adapter REAL (Google Imagen vía Generative Language API).

API key vía ``GOOGLE_API_KEY``. Usa ``negativePrompt`` y ``aspectRatio`` nativos:
ejecuta el lenguaje cinematográfico del VSC sin reinterpretarlo. HTTP inyectable.
"""

import base64
import logging
import os
import time

from app.vpl.adapters._common import constraints_size
from app.vpl.http import post_json
from app.vpl.models import GeneratedAsset, ProviderCapabilities
from app.vpl.provider import ProviderError

logger = logging.getLogger("vpl.imagen")

_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
_COST_PER_IMAGE = 0.04


def _aspect_ratio(width: int, height: int) -> str:
    ratio = width / height if height else 1.0
    for label, value in (("16:9", 1.777), ("4:3", 1.333), ("1:1", 1.0), ("9:16", 0.5625), ("3:4", 0.75)):
        if abs(ratio - value) < 0.08:
            return label
    return "16:9"


class GoogleImagenProvider:
    name = "imagen"

    def __init__(self, model: str = "imagen-3.0-generate-002", timeout: float = 120.0, http_post=None) -> None:
        self.model = model
        self._timeout = timeout
        self._http_post = http_post or post_json

    def is_available(self) -> bool:
        return bool(os.environ.get("GOOGLE_API_KEY"))

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name, model=self.model, cost_per_image=_COST_PER_IMAGE,
            native_negative_prompt=True, native_seed=True,
            max_width=1536, max_height=1536,
            aspect_ratios=["1:1", "16:9", "4:3", "9:16", "3:4"],
            async_polling=False, self_hostable=False, requires_api_key="GOOGLE_API_KEY",
            available=self.is_available(),
        )

    def _build(self, request, api_key: str):
        width, height = constraints_size(request)
        parameters = {"sampleCount": 1, "aspectRatio": _aspect_ratio(width, height)}
        if request.negative_prompt:
            parameters["negativePrompt"] = request.negative_prompt
        if request.seed:
            parameters["seed"] = int(request.seed)
        body = {"instances": [{"prompt": request.prompt}], "parameters": parameters}
        url = _ENDPOINT.format(model=self.model) + f"?key={api_key}"
        headers = {}
        return url, body, headers, (width, height)

    @staticmethod
    def _parse(response: dict) -> bytes:
        try:
            return base64.b64decode(response["predictions"][0]["bytesBase64Encoded"])
        except Exception as exc:
            raise ProviderError(f"respuesta Imagen inesperada: {exc}", transient=False) from exc

    def generate(self, request) -> GeneratedAsset:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ProviderError("GOOGLE_API_KEY no definida", transient=False)

        url, body, headers, (width, height) = self._build(request, api_key)
        started = time.perf_counter()
        logger.info("Imagen generate shot=%s model=%s", request.shot_id, self.model)
        response = self._http_post(url, body, headers, self._timeout)
        image_bytes = self._parse(response)

        return GeneratedAsset(
            shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=self.model,
            prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
            width=width, height=height, generation_time=round(time.perf_counter() - started, 3),
            cost=_COST_PER_IMAGE, reuse_key=request.reuse_key,
            metadata={"aspect_ratio": _aspect_ratio(width, height)}, image_bytes=image_bytes,
        )
