"""FfmpegVideoProvider — generación REAL de vídeo (.mp4) local vía FFmpeg (Fase C-video).

Provider de ``media_type="video"`` que produce un clip .mp4 REAL a partir del
prompt, sin APIs externas ni claves: renderiza un fotograma (Pillow) y lo
ensambla en un vídeo H.264 con el ffmpeg que ya trae ``imageio-ffmpeg``
(dependencia existente). Es el fallback "FFmpeg-based" — verificable end-to-end
ahora — frente a Pika/Haiper (que requieren credenciales).

Degradación: ante cualquier fallo lanza ``ProviderUnavailable`` (el orquestador
decide). El ejecutor de ffmpeg es inyectable (``runner``) para tests sin coste.
NO toca el FfmpegVideoComposer ni el MediaNormalizer del pipeline de vídeo final.
"""

import os
import subprocess
import tempfile
import time
from typing import Callable
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from app.media.providers.base import BaseProvider, ProviderUnavailable
from app.media.store.models import Asset

_BG = (18, 20, 28)
_ACCENT = (120, 170, 255)
_FG = (230, 232, 238)


def _font(size: int):
    for name in ("arial.ttf", "DejaVuSans.ttf", "segoeui.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _default_runner(cmd: list[str]) -> int:
    result = subprocess.run(cmd, capture_output=True, timeout=180)
    return result.returncode


class FfmpegVideoProvider(BaseProvider):
    name = "ffmpeg-video"

    def __init__(
        self,
        output_dir: str = os.path.join("output", "media_assets"),
        *,
        duration: float = 4.0,
        width: int = 1280,
        height: int = 720,
        fps: int = 25,
        ffmpeg_exe: str | None = None,
        runner: Callable[[list[str]], int] | None = None,
    ) -> None:
        self._dir = output_dir
        os.makedirs(self._dir, exist_ok=True)
        self._duration = duration
        self._width = width
        self._height = height
        self._fps = fps
        self._runner = runner or _default_runner
        if ffmpeg_exe is not None:
            self._ffmpeg = ffmpeg_exe
        else:
            import imageio_ffmpeg
            self._ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    def generate_image(self, prompt: str) -> Asset:
        raise ProviderUnavailable(f"{self.name}: proveedor de vídeo, no de imagen.")

    def generate_video(self, prompt: str) -> Asset:
        prompt = (prompt or "").strip()
        if not prompt:
            raise ProviderUnavailable(f"{self.name}: prompt vacío.")

        asset_id = uuid4().hex
        out_path = os.path.join(self._dir, f"{asset_id}.mp4")
        try:
            with tempfile.TemporaryDirectory() as tmp:
                frame = os.path.join(tmp, "frame.png")
                self._render_frame(prompt, frame)
                cmd = [
                    self._ffmpeg, "-y",
                    "-loop", "1",
                    "-t", f"{self._duration:.3f}",
                    "-i", frame,
                    "-vf", f"scale={self._width}:{self._height},format=yuv420p",
                    "-r", str(self._fps),
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-t", f"{self._duration:.3f}",
                    out_path,
                ]
                code = self._runner(cmd)
        except Exception as exc:
            raise ProviderUnavailable(f"{self.name}: fallo de ffmpeg: {exc}") from exc

        if code != 0 or not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            raise ProviderUnavailable(f"{self.name}: ffmpeg no produjo un .mp4 válido.")

        return Asset(
            asset_id=asset_id,
            type="video",
            prompt=prompt,
            provider=self.name,
            path=out_path,
            timestamp=time.time(),
        )

    def _render_frame(self, prompt: str, path: str) -> None:
        image = Image.new("RGB", (self._width, self._height), _BG)
        draw = ImageDraw.Draw(image)
        draw.text((48, 48), "DOCUMENTARY", font=_font(40), fill=_ACCENT)
        wrapped = (prompt[:110] + "…") if len(prompt) > 110 else prompt
        draw.text((48, 130), wrapped, font=_font(30), fill=_FG)
        image.save(path, "PNG")
