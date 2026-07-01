"""RealImageProvider — generación REAL de imágenes vía API externa (Fase 2).

Convierte el sistema de "pipeline simulado" a generador real: hace una petición
HTTP real a un servicio de texto→imagen por IA (Pollinations.ai, gratuito y sin
clave) y DESCARGA la imagen generada al Asset Store. No es mock ni stub.

- Entrada: ``prompt`` (desde el MGL).
- Salida: ``Asset`` real con ``path`` (fichero descargado), ``url`` (petición) y
  ``provider`` != mock.
- Degradación: ante cualquier fallo (red, respuesta no-imagen) lanza
  ``ProviderUnavailable`` para que el Router caiga al fallback local (Mock) sin
  romper el sistema. El acceso HTTP se inyecta (``http_get``) para test sin red.

NO toca el pipeline FFmpeg ni el reuse engine.
"""

import os
import ssl
import time
import urllib.parse
import urllib.request
from typing import Callable
from uuid import uuid4

from app.media.providers.base import BaseProvider, ProviderUnavailable
from app.media.store.models import Asset

_ENDPOINT = "https://image.pollinations.ai/prompt/"
_USER_AGENT = "Mozilla/5.0 (compatible; DocumentaryAI/0.1)"

# firmas mágicas -> extensión, para validar que la respuesta es una imagen real.
_IMAGE_MAGIC = (
    (b"\xff\xd8\xff", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"GIF8", "gif"),
)


def _default_http_get(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return response.read()


def _image_extension(data: bytes) -> str | None:
    for magic, ext in _IMAGE_MAGIC:
        if data.startswith(magic):
            return ext
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


class RealImageProvider(BaseProvider):
    name = "pollinations.ai"

    def __init__(
        self,
        output_dir: str = os.path.join("output", "media_assets"),
        http_get: Callable[[str, float], bytes] | None = None,
        *,
        model: str = "flux",
        width: int = 1280,
        height: int = 720,
        timeout: float = 90.0,
        seed: int | None = None,
    ) -> None:
        self._dir = output_dir
        os.makedirs(self._dir, exist_ok=True)
        self._http_get = http_get or _default_http_get
        self._model = model
        self._width = width
        self._height = height
        self._timeout = timeout
        self._seed = seed

    def build_url(self, prompt: str) -> str:
        params = {
            "width": self._width,
            "height": self._height,
            "model": self._model,
            "nologo": "true",
        }
        if self._seed is not None:
            params["seed"] = self._seed
        return _ENDPOINT + urllib.parse.quote(prompt, safe="") + "?" + urllib.parse.urlencode(params)

    def generate_image(self, prompt: str) -> Asset:
        prompt = (prompt or "").strip()
        if not prompt:
            raise ProviderUnavailable(f"{self.name}: prompt vacío.")

        url = self.build_url(prompt)
        try:
            data = self._http_get(url, self._timeout)
        except Exception as exc:  # red caída, timeout, etc. -> fallback
            raise ProviderUnavailable(f"{self.name}: fallo de red: {exc}") from exc

        ext = _image_extension(data or b"")
        if not data or ext is None:
            raise ProviderUnavailable(f"{self.name}: la respuesta no es una imagen.")

        asset_id = uuid4().hex
        path = os.path.join(self._dir, f"{asset_id}.{ext}")
        with open(path, "wb") as handle:
            handle.write(data)

        return Asset(
            asset_id=asset_id,
            type="image",
            prompt=prompt,
            provider=self.name,
            path=path,
            url=url,
            timestamp=time.time(),
        )

    def generate_video(self, prompt: str) -> Asset:
        raise ProviderUnavailable(f"{self.name}: proveedor de imagen, no de vídeo.")
