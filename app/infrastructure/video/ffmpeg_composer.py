"""FfmpegVideoComposer — ensambla clips YA NORMALIZADOS (refactor determinista).

El compositor NO normaliza nada: asume que todos los clips de entrada vienen del
``MediaNormalizer`` (mismos parámetros de vídeo/audio). Su única responsabilidad
es la COMPOSICIÓN:

- ``xfade`` (vídeo) + ``acrossfade`` (audio) en la transición intro -> escena 1,
- ``concat`` (copia de vídeo) para el resto.

Política FAIL-FAST: si FFmpeg falla, se registra el stderr completo y se lanza una
excepción inmediata. Sin retries, sin heurísticas, sin inferencia de formatos.
"""

import os
import re
import subprocess
import tempfile

import imageio_ffmpeg

from app.infrastructure.video.media_normalizer import (
    AUDIO_CODEC,
    CHANNELS,
    FPS,
    PIX_FMT,
    SAMPLE_RATE,
    VIDEO_CODEC,
)

_XFADE_SECONDS = 0.5  # duración del crossfade intro -> escena 1 (rango 0.3-0.6)
_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)")


class FfmpegVideoComposer:
    def __init__(self) -> None:
        self._ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    def compose(
        self,
        clips: list[str],
        out_path: str,
        intro_clip: str | None = None,
    ) -> None:
        """Ensambla clips normalizados en ``out_path``. Lanza excepción si falla.

        ``clips`` son rutas a clips YA normalizados (MediaNormalizer). ``intro_clip``
        (opcional) es un clip de intro normalizado que se funde con ``clips[0]``.
        """
        if not clips:
            raise ValueError("compose() requiere al menos un clip normalizado.")
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

        with tempfile.TemporaryDirectory() as tmp:
            if intro_clip:
                merged = os.path.join(tmp, "intro_xfade.mkv")
                self._crossfade(intro_clip, clips[0], merged)
                concat_clips = [merged] + clips[1:]
            else:
                concat_clips = list(clips)

            self._concat(concat_clips, tmp, out_path)

    def _crossfade(self, first: str, second: str, out_clip: str) -> None:
        d_first = self._duration(first)
        d_second = self._duration(second)
        if d_first <= 0 or d_second <= 0:
            raise RuntimeError(
                f"No se pudo leer la duración para el crossfade ({first}, {second})."
            )
        d = min(_XFADE_SECONDS, d_first * 0.5, d_second * 0.5)
        offset = max(0.0, d_first - d)
        filtergraph = (
            f"[0:v][1:v]xfade=transition=fade:duration={d:.3f}:offset={offset:.3f}[v];"
            f"[0:a][1:a]acrossfade=d={d:.3f}[a]"
        )
        cmd = [
            self._ffmpeg, "-y",
            "-i", first,
            "-i", second,
            "-filter_complex", filtergraph,
            "-map", "[v]", "-map", "[a]",
            "-c:v", VIDEO_CODEC, "-pix_fmt", PIX_FMT, "-r", str(FPS),
            "-c:a", AUDIO_CODEC, "-ar", str(SAMPLE_RATE), "-ac", str(CHANNELS),
            out_clip,
        ]
        self._run(cmd)

    def _concat(self, clips: list[str], tmp: str, out_path: str) -> None:
        list_path = os.path.join(tmp, "concat.txt")
        with open(list_path, "w", encoding="utf-8") as handle:
            for path in clips:
                safe = path.replace("\\", "/").replace("'", "'\\''")
                handle.write(f"file '{safe}'\n")

        # Entradas ya normalizadas: el vídeo se copia (determinista); el audio se
        # codifica a AAC solo para la entrega MP4 (PCM no es válido en MP4).
        cmd = [
            self._ffmpeg, "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            out_path,
        ]
        self._run(cmd)
        if not (os.path.exists(out_path) and os.path.getsize(out_path) > 0):
            raise RuntimeError(f"concat no produjo salida en {out_path}.")

    def _duration(self, path: str) -> float:
        result = subprocess.run(
            [self._ffmpeg, "-i", path], capture_output=True, text=True, timeout=60
        )
        match = _DURATION_RE.search(result.stderr or "")
        if not match:
            return 0.0
        hours, minutes, seconds = match.groups()
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    def _run(self, cmd: list[str]) -> None:
        """FAIL-FAST: sin retry. Lanza excepción con stderr completo si falla."""
        result = subprocess.run(cmd, capture_output=True, timeout=600)
        if result.returncode != 0:
            stderr = (result.stderr or b"").decode("utf-8", "replace")
            raise RuntimeError(
                f"FFmpeg failed (rc={result.returncode}): {' '.join(cmd)}\n{stderr}"
            )
