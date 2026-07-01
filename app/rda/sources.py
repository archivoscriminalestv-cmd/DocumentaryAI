"""Resolución de la fuente de vídeo para el RDA (local / YouTube / URL).

Desacopla la ADQUISICIÓN del análisis: devuelve una ruta local + un ``cleanup``.
No está ligado a ningún vídeo concreto: cualquier referencia accesible vale.
"""

import os
import tempfile
from typing import Callable


class RDASourceError(Exception):
    """No se pudo resolver/obtener el vídeo de referencia."""


def resolve_source(reference: str) -> tuple[str, str, Callable[[], None]]:
    """Devuelve (ruta_local, source_type, cleanup).

    - Fichero local existente -> uso directo (cleanup no-op).
    - URL de YouTube/genérica -> descarga temporal vía yt-dlp (si está instalado).
    """
    ref = (reference or "").strip()
    if not ref:
        raise RDASourceError("Referencia vacía.")

    if os.path.exists(ref):
        return ref, "local", lambda: None

    if ref.startswith("http://") or ref.startswith("https://"):
        return _download_with_ytdlp(ref)

    raise RDASourceError(f"Referencia no encontrada ni como fichero ni como URL: {ref}")


def _download_with_ytdlp(url: str) -> tuple[str, str, Callable[[], None]]:
    try:
        import yt_dlp  # noqa: F401
    except Exception as exc:  # dependencia opcional
        raise RDASourceError(
            "Para analizar URLs instala yt-dlp (`pip install yt-dlp`) "
            "o proporciona un fichero MP4 local."
        ) from exc

    tmp_dir = tempfile.mkdtemp(prefix="rda_")
    out_tmpl = os.path.join(tmp_dir, "ref.%(ext)s")
    # Formato ligero: la calidad alta no aporta a la GRAMÁTICA (cortes/luz/color).
    options = {
        "format": "mp4[height<=480]/best[height<=480]/best",
        "outtmpl": out_tmpl,
        "quiet": True,
        "noprogress": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
    except Exception as exc:
        _rmtree(tmp_dir)
        raise RDASourceError(f"Fallo al descargar la referencia: {exc}") from exc

    if not os.path.exists(path):
        # yt-dlp pudo remuxar a otra extensión; busca el fichero resultante.
        candidates = [os.path.join(tmp_dir, f) for f in os.listdir(tmp_dir)]
        candidates = [c for c in candidates if os.path.isfile(c)]
        if not candidates:
            _rmtree(tmp_dir)
            raise RDASourceError("La descarga no produjo ningún fichero.")
        path = max(candidates, key=os.path.getsize)

    source_type = "youtube" if "youtu" in url else "url"
    return path, source_type, lambda: _rmtree(tmp_dir)


def _rmtree(path: str) -> None:
    import shutil
    shutil.rmtree(path, ignore_errors=True)
