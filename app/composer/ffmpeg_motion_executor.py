"""FFmpegMotionExecutor — ejecuta el Motion Manifest del CME con FFmpeg (zoompan).

Construye, por plano, un filtro de cámara a partir EXCLUSIVAMENTE de los parámetros del
CME (tipo de movimiento, zoom, pan, tilt, easing, amplitud). Soporta push in/out, pan,
tilt, dolly, parallax, locked, handheld y curvas ease in/out/in-out. No inventa
movimiento: traduce intención + parámetros a expresiones de zoompan.
"""

import os
import subprocess

import imageio_ffmpeg

_SCALE_W = 2560          # pre-escalado para suavizar el zoompan
_SR = 44100


def _ep(p: str, easing: str) -> str:
    if easing == "ease_in":
        return f"({p}*{p})"
    if easing == "ease_out":
        return f"(1-(1-{p})*(1-{p}))"
    if easing == "ease_in_out":
        return f"({p}*{p}*(3-2*{p}))"
    return p  # linear


# motion_type -> (kind, direction_sign)
_FX = {
    "STATIC": ("locked", 0), "LOCKED": ("locked", 0), "RACK_FOCUS": ("locked", 0),
    "SLOW_PUSH_IN": ("zoom_in", 1), "SLOW_PULL_OUT": ("zoom_out", 1),
    "PAN_LEFT": ("pan_x", -1), "PAN_RIGHT": ("pan_x", 1),
    "TRUCK_LEFT": ("pan_x", -1), "TRUCK_RIGHT": ("pan_x", 1),
    "TILT_UP": ("pan_y", -1), "TILT_DOWN": ("pan_y", 1),
    "DOLLY_LEFT": ("dolly_x", -1), "DOLLY_RIGHT": ("dolly_x", 1),
    "CRANE_UP": ("pan_y", -1), "CRANE_DOWN": ("pan_y", 1),
    "ORBIT_LEFT": ("pan_x", -1), "ORBIT_RIGHT": ("pan_x", 1),
    "PARALLAX": ("parallax", 1), "DRONE_REVEAL": ("drone", 1),
    "MACRO_SLIDE": ("macro", 1), "MICRO_BREATHING": ("breathing", 0),
    "FLOATING": ("floating", 1),
    "HANDHELD_SUBTLE": ("handheld", 0), "HANDHELD_NERVOUS": ("handheld", 0),
}


def build_zoompan(motion_type: str, parameters: dict, duration: float,
                  fps: int, width: int, height: int) -> str:
    """Devuelve la cadena de filtro de vídeo (sin fades)."""
    kind, sign = _FX.get(motion_type, ("zoom_in", 1))
    easing = str(parameters.get("easing", "ease_in_out"))
    n = max(2, int(round(duration * fps)))
    p = f"(on/{n - 1})"
    e = _ep(p, easing)

    zoom_pct = min(25.0, abs(float(parameters.get("zoom_pct", 0.0))) or 10.0)
    amp_px = max(2.0, abs(float(parameters.get("amplitude_deg", 0.0))) * 9.0)

    cx = "iw/2-(iw/zoom/2)"
    cy = "ih/2-(ih/zoom/2)"
    mx = "(iw-iw/zoom)/2"
    my = "(ih-ih/zoom)/2"

    if kind == "locked":
        z, x, y = "1.001", cx, cy
    elif kind == "zoom_in":
        z, x, y = f"(1.0+{zoom_pct / 100.0:.4f}*{e})", cx, cy
    elif kind == "zoom_out":
        z, x, y = f"({1.0 + zoom_pct / 100.0:.4f}-{zoom_pct / 100.0:.4f}*{e})", cx, cy
    elif kind == "pan_x":
        z, x, y = "1.12", f"{cx}+({sign}*0.85*{mx}*{e})", cy
    elif kind == "pan_y":
        z, x, y = "1.12", cx, f"{cy}+({sign}*0.80*{my}*{e})"
    elif kind == "dolly_x":
        z, x, y = f"(1.10+0.06*{e})", f"{cx}+({sign}*0.50*{mx}*{e})", cy
    elif kind == "parallax":
        z, x, y = f"(1.10+0.06*{e})", f"{cx}+(0.40*{mx}*{e})", cy
    elif kind == "drone":
        z, x, y = f"({1.0 + 0.18:.4f}-0.18*{e})", cx, f"{cy}+(0.50*{my}*(1-{e}))"
    elif kind == "macro":
        z, x, y = "1.30", f"{cx}+(0.30*{mx}*{e})", cy
    elif kind == "breathing":
        z, x, y = f"(1.03+0.02*sin({p}*2*PI))", cx, cy
    elif kind == "floating":
        z = "1.07"
        x = f"{cx}+(0.18*{mx}*sin({p}*PI))"
        y = f"{cy}+(0.12*{my}*{e})"
    elif kind == "handheld":
        z = "1.10"
        x = f"{cx}+({amp_px:.2f}*sin(on/2.3))"
        y = f"{cy}+({amp_px:.2f}*cos(on/3.1))"
    else:
        z, x, y = f"(1.0+{zoom_pct / 100.0:.4f}*{e})", cx, cy

    return (f"scale={_SCALE_W}:-2,"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={width}x{height}:fps={fps},"
            f"format=yuv420p")


class FFmpegMotionExecutor:
    name = "ffmpeg"

    def __init__(self, fps: int = 25, width: int = 1280, height: int = 720) -> None:
        self._ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        self.fps = fps
        self.width = width
        self.height = height

    def execute(self, *, asset_path: str, motion_type: str, parameters: dict,
                duration: float, out_clip: str,
                fade_in: float = 0.0, fade_out: float = 0.0) -> str:
        if not os.path.exists(asset_path):
            raise FileNotFoundError(f"asset no encontrado: {asset_path}")
        os.makedirs(os.path.dirname(os.path.abspath(out_clip)) or ".", exist_ok=True)
        dur = max(0.5, float(duration))

        vfilter = build_zoompan(motion_type, parameters, dur, self.fps, self.width, self.height)
        if fade_in > 0:
            vfilter += f",fade=t=in:st=0:d={fade_in:.3f}"
        if fade_out > 0:
            vfilter += f",fade=t=out:st={max(0.0, dur - fade_out):.3f}:d={fade_out:.3f}"

        cmd = [
            self._ffmpeg, "-y",
            "-i", asset_path,
            "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={_SR}",
            "-filter_complex", f"[0:v]{vfilter}[v]",
            "-map", "[v]", "-map", "1:a",
            "-t", f"{dur:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(self.fps),
            "-c:a", "aac", "-ar", str(_SR), "-ac", "2",
            "-shortest", out_clip,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=600)
        if result.returncode != 0:
            stderr = (result.stderr or b"").decode("utf-8", "replace")[-1500:]
            raise RuntimeError(f"FFmpeg motion failed ({motion_type}): {stderr}")
        return out_clip
