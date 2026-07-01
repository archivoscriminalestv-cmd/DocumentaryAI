"""YouTubeIntelligenceEngine — orquesta el análisis de inteligencia de YouTube (YIE).

Pipeline:  URL → proveedor (metadatos + miniatura) → parsers/analizadores deterministas
→ persistencia (youtube/seo/thumbnail/popularity.json). Provider-agnóstico, determinista
y best-effort: nunca lanza (si una fuente falla, deja ``UNKNOWN`` y continúa). No toca el
DLE ni la generación.
"""

import logging
import os
import tempfile
from datetime import date

from app.yie import SCHEMA_VERSION
from app.yie.channel import parse_channel
from app.yie.metadata import extract_video_id, parse_metrics, parse_video
from app.yie.models import (
    ChannelInfo,
    PopularityMetrics,
    SeoAnalysis,
    ThumbnailAnalysis,
    VideoMetadata,
    VideoMetrics,
    YouTubeKnowledge,
)
from app.yie.persistence import write_intelligence
from app.yie.popularity import compute_popularity
from app.yie.seo import analyze_seo
from app.yie.thumbnail import analyze_thumbnail


class YouTubeIntelligenceEngine:
    def __init__(self, *, provider=None, knowledge_root: str = "knowledge",
                 reference_date: date | None = None, logger=None) -> None:
        self._provider = provider          # None → proveedor real perezoso
        self.knowledge_root = knowledge_root
        self.reference_date = reference_date or date.today()
        self._log = logger or logging.getLogger("yie")

    def _get_provider(self):
        if self._provider is None:
            from app.yie.providers.youtube import YtDlpYouTubeProvider
            self._provider = YtDlpYouTubeProvider()
        return self._provider

    def doc_dir(self, documentary_id: str) -> str:
        return os.path.join(self.knowledge_root, "documentaries", documentary_id)

    def inspect(self, url: str, *, documentary_id: str | None = None) -> dict:
        provider = self._get_provider()
        vid = extract_video_id(url)
        doc_id = documentary_id or (f"doc_yt_{vid}" if vid else "doc_yt_unknown")

        try:
            raw = provider.fetch_metadata(url) or {}
        except Exception as exc:  # noqa: BLE001 — best-effort, nunca rompe el pipeline
            self._log.warning("YIE: fallo obteniendo metadatos de %s: %s", url, exc)
            raw = {}

        video = parse_video(raw) if raw else VideoMetadata(video_id=vid or "UNKNOWN")
        channel = parse_channel(raw) if raw else ChannelInfo()
        metrics = parse_metrics(raw) if raw else VideoMetrics()
        seo = analyze_seo(video)

        thumb_path = None
        work_dir = tempfile.mkdtemp(prefix="yie_")
        try:
            if raw:
                thumb_path = provider.fetch_thumbnail(raw, work_dir)
            thumbnail = analyze_thumbnail(thumb_path)
        except Exception as exc:  # noqa: BLE001
            self._log.warning("YIE: fallo analizando la miniatura de %s: %s", url, exc)
            thumbnail = ThumbnailAnalysis(available=False)
        finally:
            _safe_rmtree(work_dir)

        popularity = compute_popularity(metrics, video.publish_date, self.reference_date)

        knowledge = YouTubeKnowledge(schema_version=SCHEMA_VERSION, video=video,
                                     channel=channel, metrics=metrics)
        paths = write_intelligence(self.doc_dir(doc_id), knowledge, seo, thumbnail, popularity)
        return {
            "documentary_id": doc_id,
            "available": bool(raw),
            "paths": paths,
            "youtube": knowledge,
            "seo": seo,
            "thumbnail": thumbnail,
            "popularity": popularity,
        }


def _safe_rmtree(path: str) -> None:
    import shutil
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass
