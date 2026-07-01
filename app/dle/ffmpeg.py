"""Utilidades FFmpeg del DLE (deterministas, provider-agnósticas).

Probe de metadatos, detección de cortes (scene), extracción de fotogramas y detección
de silencios. Inyectable: se puede pasar un ``runner`` para tests sin ejecutar FFmpeg.
"""

import os
import re
import subprocess

import imageio_ffmpeg

_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)")
_VIDEO_RE = re.compile(r"Stream.*Video:.*?,\s*(\d+)x(\d+).*?,\s*([\d.]+)\s*fps", re.S)
_RES_RE = re.compile(r"Stream.*Video:.*?(\d{2,5})x(\d{2,5})")
_FPS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*fps")
_AUDIO_RE = re.compile(r"Stream.*Audio:")
_PTS_RE = re.compile(r"pts_time:([0-9.]+)")
_SIL_START_RE = re.compile(r"silence_start:\s*([0-9.]+)")
_SIL_END_RE = re.compile(r"silence_end:\s*([0-9.]+)")


def default_runner(cmd: list[str]) -> tuple[int, str]:
    """Ejecuta FFmpeg y devuelve (returncode, stderr). stderr lleva la info de FFmpeg."""
    result = subprocess.run(cmd, capture_output=True, timeout=900)
    return result.returncode, (result.stderr or b"").decode("utf-8", "replace")


class FFmpegProbe:
    def __init__(self, runner=default_runner, ffmpeg: str | None = None) -> None:
        self._runner = runner
        self._ffmpeg = ffmpeg or imageio_ffmpeg.get_ffmpeg_exe()

    # --- metadatos -----------------------------------------------------------
    def probe(self, path: str) -> dict:
        _rc, err = self._runner([self._ffmpeg, "-i", path])
        return parse_probe(err)

    # --- cortes / planos -----------------------------------------------------
    def detect_cuts(self, path: str, threshold: float = 0.30) -> list[float]:
        _rc, err = self._runner([
            self._ffmpeg, "-i", path,
            "-filter:v", f"select='gt(scene,{threshold})',showinfo",
            "-f", "null", "-",
        ])
        return sorted({round(float(t), 3) for t in _PTS_RE.findall(err)})

    # --- silencios -----------------------------------------------------------
    def silence_intervals(self, path: str, noise_db: int = -35,
                          min_d: float = 0.4) -> list[tuple[float, float]]:
        _rc, err = self._runner([
            self._ffmpeg, "-i", path,
            "-af", f"silencedetect=noise={noise_db}dB:d={min_d}",
            "-f", "null", "-",
        ])
        return parse_silence(err)

    # --- fotogramas ----------------------------------------------------------
    def extract_frame(self, path: str, t: float, out_png: str) -> str | None:
        os.makedirs(os.path.dirname(os.path.abspath(out_png)) or ".", exist_ok=True)
        rc, _err = self._runner([
            self._ffmpeg, "-y", "-ss", f"{max(0.0, t):.3f}", "-i", path,
            "-frames:v", "1", "-q:v", "3", out_png,
        ])
        return out_png if rc == 0 and os.path.exists(out_png) else None


# --- parsers puros (testeables sin FFmpeg) -----------------------------------

def parse_probe(stderr: str) -> dict:
    duration = 0.0
    m = _DURATION_RE.search(stderr or "")
    if m:
        h, mi, s = m.groups()
        duration = int(h) * 3600 + int(mi) * 60 + float(s)
    width = height = 0
    rm = _RES_RE.search(stderr or "")
    if rm:
        width, height = int(rm.group(1)), int(rm.group(2))
    fps = 0.0
    fm = _FPS_RE.search(stderr or "")
    if fm:
        fps = float(fm.group(1))
    has_audio = bool(_AUDIO_RE.search(stderr or ""))
    return {"duration": round(duration, 3), "width": width, "height": height,
            "fps": fps, "has_audio": has_audio}


def parse_silence(stderr: str) -> list[tuple[float, float]]:
    starts = [float(x) for x in _SIL_START_RE.findall(stderr or "")]
    ends = [float(x) for x in _SIL_END_RE.findall(stderr or "")]
    intervals = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else s
        intervals.append((round(s, 3), round(e, 3)))
    return intervals


def cuts_to_shots(cuts: list[float], duration: float) -> list[tuple[float, float]]:
    """Convierte tiempos de corte en segmentos [inicio, fin] de plano."""
    bounds = [0.0] + [c for c in sorted(cuts) if 0.0 < c < duration] + [round(duration, 3)]
    shots = []
    for a, b in zip(bounds, bounds[1:]):
        if b - a >= 0.20:  # descarta micro-segmentos
            shots.append((round(a, 3), round(b, 3)))
    if not shots and duration > 0:
        shots = [(0.0, round(duration, 3))]
    return shots
