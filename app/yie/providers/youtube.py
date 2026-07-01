"""Proveedor real de metadatos de YouTube (YIE) — vía yt-dlp, sin descargar el vídeo.

Obtiene el dump de metadatos (``--dump-single-json --skip-download``) y descarga
ÚNICAMENTE la miniatura. La integración es inyectable: el ``runner`` (ejecuta yt-dlp) y
el ``http_get`` (descarga la miniatura) se pueden sustituir en los tests, de modo que
toda la red sea mockeable. Si algo falla, degrada con elegancia (no rompe el pipeline).
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from typing import Any, Protocol


class YouTubeProvider(Protocol):
    def fetch_metadata(self, url: str) -> dict: ...
    def fetch_thumbnail(self, raw: dict, work_dir: str) -> str | None: ...


def _resolve_ytdlp() -> list[str] | None:
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
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    return result.returncode, (result.stdout or b"").decode("utf-8", "replace")


def _default_http_get(url: str) -> bytes:
    import warnings

    import requests
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        resp = requests.get(url, timeout=30, verify=False)
        resp.raise_for_status()
        return resp.content


class YtDlpYouTubeProvider:
    name = "yt-dlp"

    def __init__(self, runner=_default_runner, http_get=_default_http_get,
                 ytdlp: list[str] | None = None) -> None:
        self._runner = runner
        self._http_get = http_get
        self._cmd = ytdlp or _resolve_ytdlp()

    def available(self) -> bool:
        return self._cmd is not None

    def fetch_metadata(self, url: str) -> dict[str, Any]:
        if not self.available():
            return {}
        rc, out = self._runner([*self._cmd, "--dump-single-json", "--skip-download",
                                "--no-playlist", url])
        if rc != 0 or not out.strip():
            return {}
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return {}

    def fetch_thumbnail(self, raw: dict, work_dir: str) -> str | None:
        thumb_url = raw.get("thumbnail")
        if not thumb_url:
            thumbs = raw.get("thumbnails") or []
            if thumbs:
                thumb_url = thumbs[-1].get("url")        # la última suele ser la mayor
        if not thumb_url:
            return None
        try:
            data = self._http_get(thumb_url)
        except Exception:
            return None
        os.makedirs(work_dir, exist_ok=True)
        path = os.path.join(work_dir, "thumbnail.img")
        with open(path, "wb") as handle:
            handle.write(data)
        return path
