"""MockVisualProvider — proveedor placeholder DETERMINISTA (siempre disponible).

Genera un PNG real (Pillow) con shot id, prompt, camera, lens, lighting, seed y
reuse_key. Sin red. Usado por los tests y por la demo offline. Nunca se elimina.
"""

import io

from PIL import Image, ImageDraw, ImageFont

from app.vpl.models import GeneratedAsset, ProviderCapabilities

_BG = (18, 20, 28)
_FG = (228, 230, 236)
_ACCENT = (120, 170, 255)


def _font(size: int):
    for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(text: str, width: int = 64) -> list[str]:
    import textwrap
    return textwrap.wrap(text, width=width)[:8]


class MockVisualProvider:
    name = "mock"
    model = "mock-1"

    def is_available(self) -> bool:
        return True

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            name=self.name, model=self.model, cost_per_image=0.0,
            native_negative_prompt=False, native_seed=True,
            max_width=4096, max_height=4096,
            aspect_ratios=["1:1", "16:9", "9:16", "4:3", "3:4"],
            async_polling=False, self_hostable=True, requires_api_key="",
            available=True,
        )

    def generate(self, request) -> GeneratedAsset:
        constraints = getattr(request, "provider_constraints", {}) or {}
        width = int(constraints.get("width", 1280))
        height = int(constraints.get("height", 720))

        image = Image.new("RGB", (width, height), _BG)
        draw = ImageDraw.Draw(image)
        draw.text((40, 30), f"SHOT {request.shot_id}", font=_font(34), fill=_ACCENT)
        lines = [
            f"camera: {request.camera}   lens: {request.lens}",
            f"lighting: {request.lighting}",
            f"seed: {request.seed}   reuse_key: {request.reuse_key or '-'}",
            f"motion: {request.motion_hint}",
            "prompt:",
        ]
        y = 90
        for line in lines:
            draw.text((40, y), line, font=_font(24), fill=_FG)
            y += 34
        for line in _wrap(request.prompt):
            draw.text((60, y), line, font=_font(20), fill=_FG)
            y += 28

        buffer = io.BytesIO()
        image.save(buffer, "PNG")

        return GeneratedAsset(
            shot_id=request.shot_id, scene_id=request.scene_id, provider=self.name, model=self.model,
            prompt=request.prompt, negative_prompt=request.negative_prompt, seed=request.seed,
            width=width, height=height, generation_time=0.0, cost=0.0, reuse_key=request.reuse_key,
            metadata={"camera": request.camera, "lens": request.lens, "lighting": request.lighting,
                      "motion_hint": request.motion_hint},
            image_bytes=buffer.getvalue(),
        )
