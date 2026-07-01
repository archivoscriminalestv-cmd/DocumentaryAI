"""Proveedor de YouTube: descarga el vídeo (downloader inyectable) y lo entrega local.

El ID del documental deriva del id de YouTube (estable, reproducible).
"""

from app.dle.downloader.youtube import YouTubeDownloader, video_id_from_url


class YouTubeProvider:
    name = "youtube"

    def __init__(self, downloader: YouTubeDownloader | None = None) -> None:
        self._downloader = downloader or YouTubeDownloader()

    def resolve(self, ref: str, work_dir: str) -> dict:
        vid = video_id_from_url(ref)
        path = self._downloader.download(ref, work_dir)  # puede lanzar DownloadError
        return {"path": path, "source_type": "youtube", "source_ref": ref,
                "video_id": f"doc_yt_{vid}"}
