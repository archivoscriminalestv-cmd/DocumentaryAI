"""MediaNormalizer — capa de normalización de medios (refactor determinista).

Garantiza que TODO clip tenga parámetros idénticos ANTES de cualquier composición
FFmpeg, de modo que el compositor (xfade/acrossfade/concat) trabaje sobre entradas
perfectamente uniformes y el resultado sea determinista:

- vídeo:  H.264, ``yuv420p``, fps global fijo
- audio:  44100 Hz, estéreo, ``pcm_s16le``
- contenedor intermedio: Matroska (.mkv), que admite H.264 + PCM

Política FAIL-FAST: si FFmpeg falla, se registra el stderr completo y se lanza
una excepción inmediata. No hay retries, ni heurísticas, ni inferencia de
formatos, ni auto-fix.
"""

import os
import subprocess

import imageio_ffmpeg

# Especificación global de normalización (fuente única de verdad).
FPS = 25
WIDTH = 1280
HEIGHT = 720
PIX_FMT = "yuv420p"
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "pcm_s16le"
SAMPLE_RATE = 44100
CHANNELS = 2
CLIP_EXT = ".mkv"


def _run(cmd: list[str]) -> None:
    """Ejecuta FFmpeg con política fail-fast (sin retry, stderr completo)."""
    result = subprocess.run(cmd, capture_output=True, timeout=600)
    if result.returncode != 0:
        stderr = (result.stderr or b"").decode("utf-8", "replace")
        raise RuntimeError(
            "FFmpeg normalization failed (rc="
            f"{result.returncode}): {' '.join(cmd)}\n{stderr}"
        )


class MediaNormalizer:
    def __init__(self, fps: int = FPS, width: int = WIDTH, height: int = HEIGHT) -> None:
        self._ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        self._fps = fps
        self._width = width
        self._height = height

    def scene_clip(
        self, image_path: str, audio_path: str | None, duration: float, out_clip: str
    ) -> str:
        """Imagen fija (+ audio o silencio) -> clip normalizado. Devuelve out_clip."""
        has_audio = bool(audio_path) and os.path.exists(audio_path or "")
        cmd = [self._ffmpeg, "-y", "-loop", "1", "-i", image_path]
        if has_audio:
            cmd += ["-i", audio_path]
        else:
            cmd += [
                "-f", "lavfi",
                "-i", f"anullsrc=channel_layout=stereo:sample_rate={SAMPLE_RATE}",
            ]
        cmd += [
            "-vf", f"scale={self._width}:{self._height},format={PIX_FMT}",
            "-r", str(self._fps),
            "-c:v", VIDEO_CODEC,
            "-c:a", AUDIO_CODEC, "-ar", str(SAMPLE_RATE), "-ac", str(CHANNELS),
        ]
        cmd += ["-shortest"] if has_audio else ["-t", f"{max(1.0, float(duration)):.3f}"]
        cmd += [out_clip]
        _run(cmd)
        return out_clip

    def intro_clip(self, intro_path: str, out_clip: str) -> str:
        """Vídeo de intro -> clip normalizado (mismos parámetros). Devuelve out_clip."""
        cmd = [
            self._ffmpeg, "-y", "-i", intro_path,
            "-vf", f"scale={self._width}:{self._height},format={PIX_FMT}",
            "-r", str(self._fps),
            "-c:v", VIDEO_CODEC,
            "-c:a", AUDIO_CODEC, "-ar", str(SAMPLE_RATE), "-ac", str(CHANNELS),
            out_clip,
        ]
        _run(cmd)
        return out_clip
