"""FfmpegFrameExtractor — muestrea fotogramas y calcula sus rasgos (RDA).

Usa el ffmpeg que ya trae ``imageio-ffmpeg`` para muestrear N fotogramas/segundo a
baja resolución en un directorio TEMPORAL, calcula rasgos numéricos por fotograma
con Pillow y BORRA los fotogramas (no se retiene contenido del vídeo original;
solo estadísticas). No transcribe, no reconoce objetos: solo gramática visual.
"""

import glob
import os
import re
import subprocess
import tempfile

from app.rda.models import FrameFeatures

_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)")
_RES_RE = re.compile(r"Video:.*?(\d{2,5})x(\d{2,5})")
_FPS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*fps")


class FfmpegFrameExtractor:
    def __init__(
        self,
        *,
        sample_fps: float = 4.0,
        width: int = 48,
        height: int = 27,
        ffmpeg_exe: str | None = None,
    ) -> None:
        self.sample_fps = sample_fps
        self._width = width
        self._height = height
        if ffmpeg_exe is not None:
            self._ffmpeg = ffmpeg_exe
        else:
            import imageio_ffmpeg
            self._ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    def probe(self, path: str) -> dict:
        result = subprocess.run([self._ffmpeg, "-i", path], capture_output=True, text=True, timeout=120)
        err = result.stderr or ""
        meta: dict = {"duration": 0.0, "width": 0, "height": 0, "fps": 0.0}
        m = _DURATION_RE.search(err)
        if m:
            h, mi, s = m.groups()
            meta["duration"] = int(h) * 3600 + int(mi) * 60 + float(s)
        r = _RES_RE.search(err)
        if r:
            meta["width"], meta["height"] = int(r.group(1)), int(r.group(2))
        f = _FPS_RE.search(err)
        if f:
            meta["fps"] = float(f.group(1))
        return meta

    def extract(self, path: str) -> list[FrameFeatures]:
        from PIL import Image

        frames: list[FrameFeatures] = []
        with tempfile.TemporaryDirectory() as tmp:
            pattern = os.path.join(tmp, "f_%06d.png")
            cmd = [
                self._ffmpeg, "-y", "-i", path,
                "-vf", f"fps={self.sample_fps},scale={self._width}:{self._height}",
                "-an", pattern,
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=900)
            if result.returncode != 0:
                stderr = (result.stderr or b"").decode("utf-8", "replace")
                raise RuntimeError(f"ffmpeg frame extraction failed: {stderr[-500:]}")

            files = sorted(glob.glob(os.path.join(tmp, "f_*.png")))
            interval = 1.0 / self.sample_fps if self.sample_fps else 0.0
            for index, file in enumerate(files):
                with Image.open(file) as img:
                    frames.append(self._features(img, index * interval))
        return frames  # los PNG se borran al cerrar el TemporaryDirectory

    @staticmethod
    def _features(img, t: float) -> FrameFeatures:
        rgb = img.convert("RGB")
        data = rgb.tobytes()  # R,G,B por píxel; evita getdata() (deprecado)
        n = (len(data) // 3) or 1

        sr = sg = sb = 0.0
        lumas: list[float] = []
        rg: list[float] = []
        yb: list[float] = []
        for i in range(0, len(data), 3):
            r, g, b = data[i], data[i + 1], data[i + 2]
            sr += r; sg += g; sb += b
            lumas.append(0.299 * r + 0.587 * g + 0.114 * b)
            rg.append(r - g)
            yb.append(0.5 * (r + g) - b)

        mr, mg, mb = sr / n, sg / n, sb / n
        b_mean = sum(lumas) / n
        b_std = (sum((x - b_mean) ** 2 for x in lumas) / n) ** 0.5
        rg_mean, yb_mean = sum(rg) / n, sum(yb) / n
        rg_std = (sum((x - rg_mean) ** 2 for x in rg) / n) ** 0.5
        yb_std = (sum((x - yb_mean) ** 2 for x in yb) / n) ** 0.5
        colorfulness = (rg_std ** 2 + yb_std ** 2) ** 0.5 + 0.3 * ((rg_mean ** 2 + yb_mean ** 2) ** 0.5)

        signature = tuple(float(v) for v in rgb.resize((8, 8)).convert("L").tobytes())
        return FrameFeatures(
            t=round(t, 3),
            brightness=b_mean,
            contrast=b_std,
            warmth=mr - mb,
            colorfulness=colorfulness,
            signature=signature,
        )
