"""MockImageProvider — proveedor local de imágenes (Fase 1 MGL).

Genera una imagen placeholder real (Pillow, sin red ni IA externa) para que el
sistema funcione offline y de forma determinista. Actúa como fallback cuando los
proveedores externos no están disponibles. NO hace scraping ni IA propia.
"""

import os
import time
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from app.media.providers.base import BaseProvider, ProviderUnavailable
from app.media.store.models import Asset

_W, _H = 1280, 720
_BG = (20, 22, 30)
_ACCENT = (120, 170, 255)
_FG = (230, 232, 238)


def _font(size: int):
    for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


class MockImageProvider(BaseProvider):
    name = "mock-image"

    def __init__(self, output_dir: str = os.path.join("output", "media_assets")) -> None:
        self._dir = output_dir
        os.makedirs(self._dir, exist_ok=True)

    def generate_image(self, prompt: str) -> Asset:
        asset_id = uuid4().hex
        path = os.path.join(self._dir, f"{asset_id}.png")
        self._draw(path, prompt)
        return Asset(
            asset_id=asset_id,
            type="image",
            prompt=prompt,
            provider=self.name,
            path=path,
            timestamp=time.time(),
        )

    def generate_video(self, prompt: str) -> Asset:
        raise ProviderUnavailable("MockImageProvider no genera vídeo.")

    def _draw(self, path: str, prompt: str) -> None:
        image = Image.new("RGB", (_W, _H), _BG)
        draw = ImageDraw.Draw(image)
        draw.text((48, 48), "MOCK ASSET", font=_font(40), fill=_ACCENT)
        wrapped = (prompt[:90] + "…") if len(prompt) > 90 else prompt
        draw.text((48, 120), wrapped, font=_font(28), fill=_FG)
        image.save(path, "PNG")
