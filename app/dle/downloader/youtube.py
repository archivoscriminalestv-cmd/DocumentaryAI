"""Descarga de YouTube vía yt-dlp (runner inyectable; degrada con elegancia).

No descarga contenido fuera del flujo normal de análisis. Si yt-dlp no está disponible,
lanza ``DownloadError`` (el orquestador lo registra y continúa sin romper).
"""

import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys


class DownloadError(Exception):
    pass


# Sentinela: distingue "autodetectar" (por defecto) de "deshabilitado explícitamente".
_AUTO = object()


def _resolve_ytdlp() -> list[str] | None:
    """Comando para invocar yt-dlp. Prioriza el ejecutable en PATH; si no está pero el
    módulo ``yt_dlp`` sí (instalado por pip sin que su Scripts esté en PATH, típico en
    Windows), usa ``python -m yt_dlp``. Devuelve None si no hay ninguno."""
    path = shutil.which("yt-dlp")
    if path:
        return [path]
    try:
        if importlib.util.find_spec("yt_dlp") is not None:
            return [sys.executable, "-m", "yt_dlp"]
    except Exception:
        pass
    return None


def _default_runner(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, timeout=1800)
    return result.returncode, (result.stderr or b"").decode("utf-8", "replace")


def video_id_from_url(url: str) -> str:
    m = re.search(r"(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{6,})", url or "")
    if m:
        return m.group(1)
    return "yt_" + hashlib.sha256((url or "").encode("utf-8")).hexdigest()[:10]


class YouTubeDownloader:
    name = "yt-dlp"

    def __init__(self, runner=_default_runner, ytdlp=_AUTO) -> None:
        self._runner = runner
        if ytdlp is _AUTO:                       # autodetección (PATH o módulo)
            self._cmd = _resolve_ytdlp()
        elif ytdlp:                              # ruta o comando explícito
            self._cmd = [ytdlp] if isinstance(ytdlp, str) else list(ytdlp)
        else:                                    # None/"" -> deshabilitado explícitamente
            self._cmd = None

    def available(self) -> bool:
        return self._cmd is not None

    def download(self, url: str, out_dir: str) -> str:
        if not self.available():
            raise DownloadError("yt-dlp no está instalado; no se puede descargar el vídeo")
        os.makedirs(out_dir, exist_ok=True)
        vid = video_id_from_url(url)
        out_tmpl = os.path.join(out_dir, f"{vid}.%(ext)s")
        rc, err = self._runner([
            *self._cmd, "-f", "mp4/best", "-o", out_tmpl, "--no-playlist", url,
        ])
        if rc != 0:
            raise DownloadError(f"yt-dlp falló (rc={rc}): {err[-300:]}")
        for ext in (".mp4", ".mkv", ".webm"):
            candidate = os.path.join(out_dir, f"{vid}{ext}")
            if os.path.exists(candidate):
                return candidate
        raise DownloadError("yt-dlp no produjo un fichero reconocible")
