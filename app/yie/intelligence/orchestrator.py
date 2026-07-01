"""CompetitiveIntelligenceEngine — orquesta toda la inteligencia de YouTube (YIE-002).

URL → proveedor (metadatos + miniatura, una sola vez) → análisis base (YIE-001, reutilizado)
+ análisis competitivo (canal/audiencia/engagement/SEO ext/miniatura ext) + enriquecimiento
opcional → persistencia de 9 JSON + provider_coverage.json. Provider-agnóstico, determinista
y best-effort: nunca lanza; lo ausente queda UNKNOWN. No toca el DLE ni el DKS.
"""

import logging
import os
import shutil
import tempfile
from datetime import date

from app.yie import UNKNOWN
from app.yie.channel import parse_channel
from app.yie.intelligence import CI_VERSION, SCHEMA_VERSION
from app.yie.intelligence.audience import build_audience
from app.yie.intelligence.channel import build_channel_intelligence
from app.yie.intelligence.coverage import build_coverage
from app.yie.intelligence.engagement import build_engagement
from app.yie.intelligence.persistence import write_competitive
from app.yie.intelligence.seo_ext import analyze_seo_extended
from app.yie.intelligence.thumbnail_ext import analyze_thumbnail_extended
from app.yie.metadata import extract_video_id, parse_metrics, parse_video
from app.yie.models import ChannelInfo, VideoMetadata, VideoMetrics, YouTubeKnowledge
from app.yie.persistence import write_intelligence
from app.yie.popularity import compute_popularity
from app.yie.seo import analyze_seo
from app.yie.thumbnail import analyze_thumbnail

# Campos de canal que pueden venir del enriquecimiento (clave canónica -> campo del modelo).
_ENRICHMENT_FIELDS = ("total_views", "total_videos", "creation_date", "country",
                      "verified", "official_artist", "custom_url", "channel_keywords",
                      "playlist_count", "subscribers", "pinned_comment")


class CompetitiveIntelligenceEngine:
    def __init__(self, *, provider=None, enrichment_providers=None,
                 knowledge_root: str = "knowledge", reference_date: date | None = None,
                 logger=None) -> None:
        self._provider = provider
        self._enrichment = enrichment_providers if enrichment_providers is not None \
            else _default_enrichment()
        self.knowledge_root = knowledge_root
        self.reference_date = reference_date or date.today()
        self._log = logger or logging.getLogger("yie.intelligence")

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
        doc_dir = self.doc_dir(doc_id)

        try:
            raw = provider.fetch_metadata(url) or {}
        except Exception as exc:  # noqa: BLE001 — best-effort
            self._log.warning("YIE-CI: metadatos no disponibles para %s: %s", url, exc)
            raw = {}

        video = parse_video(raw) if raw else VideoMetadata(video_id=vid or UNKNOWN)
        base_channel = parse_channel(raw) if raw else ChannelInfo()
        metrics = parse_metrics(raw) if raw else VideoMetrics()
        seo = analyze_seo(video)
        popularity = compute_popularity(metrics, video.publish_date, self.reference_date)

        # Miniatura: se descarga, se analiza (base + extendida) y se DESCARTA.
        work = tempfile.mkdtemp(prefix="yie_ci_")
        try:
            thumb_path = provider.fetch_thumbnail(raw, work) if raw else None
            base_thumb = analyze_thumbnail(thumb_path)
            ext_thumb = analyze_thumbnail_extended(thumb_path)
        except Exception as exc:  # noqa: BLE001
            self._log.warning("YIE-CI: miniatura no disponible para %s: %s", url, exc)
            from app.yie.models import ThumbnailAnalysis
            base_thumb, ext_thumb = ThumbnailAnalysis(available=False), analyze_thumbnail_extended(None)
        finally:
            shutil.rmtree(work, ignore_errors=True)

        # Ficheros base (YIE-001), reutilizando sus funciones puras (no se modifican).
        base = YouTubeKnowledge(video=video, channel=base_channel, metrics=metrics)
        base_paths = write_intelligence(doc_dir, base, seo, base_thumb, popularity)

        # Enriquecimiento opcional e independiente.
        enrichment, sources, available, unavailable = self._enrich(video, vid, raw)

        channel_intel = build_channel_intelligence(raw, enrichment, self.reference_date)
        audience = build_audience(channel_intel, metrics)
        engagement = build_engagement(metrics, popularity.age_days)
        seo_ext = analyze_seo_extended(video, enrichment)

        competitive = {
            "schema_version": SCHEMA_VERSION,
            "ci_version": CI_VERSION,
            "video_id": video.video_id,
            "available": bool(raw),
            "metrics": metrics.to_dict(),
            "engagement": engagement.to_dict(),
            "audience": audience.to_dict(),
            "channel": channel_intel.to_dict(),
            "seo": seo_ext.to_dict(),
            "thumbnail": ext_thumb.to_dict(),
            "flags": {
                "verified": channel_intel.verified,
                "official_artist": channel_intel.official_artist,
                "has_captions": bool(video.subtitles),
                "has_chapters": bool(video.chapters),
            },
        }

        coverage = self._coverage(video, metrics, channel_intel, ext_thumb,
                                  sources, available, unavailable)
        new_paths = write_competitive(doc_dir, channel_intel, audience, engagement,
                                      competitive, coverage)

        return {
            "documentary_id": doc_id,
            "available": bool(raw),
            "paths": {**base_paths, **new_paths},
            "channel": channel_intel,
            "audience": audience,
            "engagement": engagement,
            "seo_extended": seo_ext,
            "thumbnail_extended": ext_thumb,
            "coverage": coverage,
        }

    def _enrich(self, video, vid, raw):
        enrichment: dict = {}
        sources: dict = {}
        available: list[str] = []
        unavailable: list[str] = []
        video_id = video.video_id if video.video_id != UNKNOWN else vid
        for prov in self._enrichment:
            try:
                ok = prov.available()
            except Exception:
                ok = False
            if not ok:
                unavailable.append(prov.name)
                continue
            available.append(prov.name)
            try:
                data = prov.fetch(video_id, raw) or {}
            except Exception:
                data = {}
            for key, value in data.items():
                if key not in enrichment:
                    enrichment[key] = value
                    sources[key] = prov.name
        return enrichment, sources, available, unavailable

    def _coverage(self, video, metrics, channel_intel, ext_thumb, sources, available, unavailable):
        fields = {
            "video.views": metrics.views,
            "video.likes": metrics.likes,
            "video.comments": metrics.comments,
            "video.duration": metrics.duration,
            "video.resolution": video.resolution,
            "video.fps": video.fps,
            "video.category": video.category,
            "video.language": video.language,
            "video.license": video.license,
            "video.tags": video.tags,
            "video.captions": video.subtitles,
            "channel.id": channel_intel.channel_id,
            "channel.name": channel_intel.channel_name,
            "channel.subscribers": channel_intel.subscribers,
            "channel.total_videos": channel_intel.total_videos,
            "channel.total_views": channel_intel.total_views,
            "channel.creation_date": channel_intel.creation_date,
            "channel.country": channel_intel.country,
            "channel.verified": channel_intel.verified,
            "channel.custom_url": channel_intel.custom_url,
            "channel.playlist_count": channel_intel.playlist_count,
            "thumbnail.available": ext_thumb.available,
        }
        # Origen por defecto: yt-dlp para vídeo/canal-básico; el enriquecimiento manda
        # para los campos que aportó (mapeados por su clave canónica).
        enrichment_to_field = {
            "total_views": "channel.total_views", "total_videos": "channel.total_videos",
            "creation_date": "channel.creation_date", "country": "channel.country",
            "verified": "channel.verified", "custom_url": "channel.custom_url",
            "playlist_count": "channel.playlist_count", "subscribers": "channel.subscribers",
        }
        origins: dict = {}
        for canonical, prov in sources.items():
            field = enrichment_to_field.get(canonical)
            if field:
                origins[field] = prov
        origins["thumbnail.available"] = "pillow"
        return build_coverage(fields, origins, available, unavailable)


def _default_enrichment():
    from app.yie.intelligence.providers.vidiq import VidIQProvider
    return [VidIQProvider()]
