"""Comprobación de prerequisitos del Downloader (DLE-002B).

Verifica la disponibilidad de las herramientas externas (yt-dlp, ffmpeg, Whisper)
ANTES de procesar la cola y produce un informe claro. Nunca lanza excepciones: cada
detección se aísla y se traduce a un estado legible. Los detectores son inyectables
para poder simular entornos en los tests.
"""

import importlib.util
import shutil
import sys
from dataclasses import dataclass, field


@dataclass
class ToolStatus:
    name: str
    available: bool
    detail: str = ""
    optional: bool = False


@dataclass
class EnvironmentReport:
    tools: list[ToolStatus] = field(default_factory=list)

    def get(self, name: str) -> ToolStatus | None:
        return next((t for t in self.tools if t.name == name), None)

    def ready(self) -> bool:
        """True si están todas las herramientas NO opcionales."""
        return all(t.available for t in self.tools if not t.optional)

    def format(self) -> str:
        width = 16
        lines = ["Downloader", ""]
        for tool in self.tools:
            label = tool.name + " "
            dots = "." * max(3, width - len(label))
            status = "OK" if tool.available else "unavailable"
            lines.append(f"{label}{dots} {status}")
        return "\n".join(lines)


def _detect_ytdlp() -> tuple[bool, str]:
    path = shutil.which("yt-dlp")
    if path:
        return True, path
    # instalado como módulo pip pero sin el ejecutable en PATH (típico en Windows)
    try:
        if importlib.util.find_spec("yt_dlp") is not None:
            return True, f"{sys.executable} -m yt_dlp"
    except Exception:
        pass
    return False, ""


def _detect_ffmpeg() -> tuple[bool, str]:
    path = shutil.which("ffmpeg")
    if path:
        return True, path
    try:  # ffmpeg empaquetado (imageio-ffmpeg), como usa el resto del sistema
        import imageio_ffmpeg

        return True, imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return False, ""


def _detect_whisper() -> tuple[bool, str]:
    for module in ("whisper", "faster_whisper"):
        try:
            if importlib.util.find_spec(module) is not None:
                return True, module
        except Exception:
            continue
    return False, ""


def check_downloader_environment(
    *, ytdlp=_detect_ytdlp, ffmpeg=_detect_ffmpeg, whisper=_detect_whisper
) -> EnvironmentReport:
    """Devuelve el informe de prerequisitos. Detectores inyectables (tests)."""

    def _safe(detector) -> tuple[bool, str]:
        try:
            available, detail = detector()
            return bool(available), str(detail or "")
        except Exception as exc:  # un detector nunca rompe el arranque
            return False, f"error: {exc}"[:120]

    yt_ok, yt_detail = _safe(ytdlp)
    ff_ok, ff_detail = _safe(ffmpeg)
    wh_ok, wh_detail = _safe(whisper)
    return EnvironmentReport(tools=[
        ToolStatus("yt-dlp", yt_ok, yt_detail),
        ToolStatus("ffmpeg", ff_ok, ff_detail),
        ToolStatus("Whisper", wh_ok, wh_detail, optional=True),
    ])
