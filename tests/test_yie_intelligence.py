"""Tests de inteligencia competitiva (YIE-002) — deterministas, sin red.

Reutiliza el proveedor falso y los datos canónicos del YIE-001. Cubre canal, audiencia,
engagement, SEO extendido, miniatura extendida, cobertura de proveedores, orquestador,
reproducibilidad, independencia de proveedores e integración Queue → YIE → DLE.
"""

import json
import os
from datetime import date

from app.yie.intelligence.audience import build_audience
from app.yie.intelligence.channel import build_channel_intelligence
from app.yie.intelligence.engagement import build_engagement
from app.yie.intelligence.orchestrator import CompetitiveIntelligenceEngine
from app.yie.intelligence.providers.future import SocialBladeProvider
from app.yie.intelligence.providers.vidiq import VidIQProvider
from app.yie.intelligence.seo_ext import analyze_seo_extended
from app.yie.intelligence.thumbnail_ext import analyze_thumbnail_extended
from app.yie.metadata import parse_metrics, parse_video
from tests.test_yie import REF, RAW, URL, FakeProvider, _FakeDLE

ENRICH = {
    "total_views": 200_000_000, "total_videos": 400, "creation_date": "2015-06-01",
    "country": "US", "playlist_count": 12, "channel_keywords": ["crime", "docs"],
    "verified": True, "custom_url": "@crimedocs",
}


class FakeVidIQ:
    name = "vidiq"

    def __init__(self, data):
        self._data = data

    def available(self):
        return True

    def fetch(self, video_id, raw):
        return dict(self._data)


def _engine(tmp_path, provider=None, enrichment=None):
    return CompetitiveIntelligenceEngine(
        provider=provider or FakeProvider(),
        enrichment_providers=enrichment if enrichment is not None else [VidIQProvider()],
        knowledge_root=str(tmp_path / "knowledge"),
        reference_date=REF,
    )


# --- canal / audiencia / engagement ------------------------------------------
def test_channel_intelligence_with_enrichment():
    ch = build_channel_intelligence(RAW, ENRICH, REF)
    assert ch.subscribers == 500_000
    assert ch.total_videos == 400 and ch.total_views == 200_000_000
    assert ch.average_views_per_video == 500000.0
    assert ch.channel_age_days and ch.channel_age_days > 0
    assert ch.uploads_per_year and ch.uploads_per_month
    assert ch.verified is True and ch.custom_url == "@crimedocs"


def test_channel_unknown_without_enrichment():
    ch = build_channel_intelligence(RAW, {}, REF)
    assert ch.subscribers == 500_000           # del dump por vídeo
    assert ch.total_videos is None and ch.total_views is None
    assert ch.channel_age_days is None and ch.uploads_per_year is None


def test_audience_and_engagement_formulas():
    ch = build_channel_intelligence(RAW, ENRICH, REF)
    aud = build_audience(ch, parse_metrics(RAW))
    assert aud.views_per_subscriber == 2.0          # 1.000.000 / 500.000
    assert aud.channel_views_per_subscriber == 400.0  # 200M / 500k

    eng = build_engagement(parse_metrics(RAW), age_days=7)
    assert eng.views_per_day == round(1_000_000 / 7, 4)
    assert eng.likes_per_view == 0.05 and eng.comments_per_view == 0.002
    assert eng.engagement_rate == 0.052
    assert eng.like_velocity == round(50_000 / 7, 4)


def test_engagement_handles_missing():
    from app.yie.models import VideoMetrics
    eng = build_engagement(VideoMetrics(), age_days=None)
    assert eng.views_per_day is None and eng.engagement_rate is None


# --- SEO extendido -----------------------------------------------------------
def test_seo_extended_rules():
    seo = analyze_seo_extended(parse_video(RAW), ENRICH)
    assert seo.title_length > 0 and seo.description_length > 0
    assert seo.link_count == 1                  # https://x en la descripción
    assert seo.hashtag_count == 2 and seo.tag_count == 2
    assert seo.chapter_count == 1
    assert 0.0 <= seo.stopword_ratio <= 1.0
    assert seo.keyword_repetition >= 1
    assert isinstance(seo.keyword_density, dict)


# --- miniatura extendida -----------------------------------------------------
def test_thumbnail_extended(tmp_path):
    from PIL import Image
    p = str(tmp_path / "t.png")
    Image.new("RGB", (160, 90), (40, 90, 200)).save(p)    # azulado → cool
    t = analyze_thumbnail_extended(p)
    assert t.available is True
    assert t.aspect_ratio == round(160 / 90, 4)
    assert t.color_temperature == "cool"
    assert t.dominant_colors and t.dominant_colors[0].startswith("#")
    assert abs(sum(c["fraction"] for c in t.color_palette) - 1.0) < 0.05
    assert len(t.histogram["g"]) == 16


def test_thumbnail_extended_missing():
    assert analyze_thumbnail_extended(None).available is False


# --- cobertura de proveedores (auditoría) ------------------------------------
def test_coverage_marks_unknown_without_enrichment(tmp_path):
    result = _engine(tmp_path).inspect(URL)        # vidIQ por defecto: no disponible
    cov = json.load(open(result["paths"]["provider_coverage"], encoding="utf-8"))
    assert "vidiq" in cov["providers_unavailable"]
    assert cov["by_field"]["channel.total_views"] == "UNKNOWN"
    assert cov["by_field"]["video.views"] == "yt-dlp"
    assert 0.0 < cov["coverage_ratio"] < 1.0


def test_coverage_attributes_enrichment_provider(tmp_path):
    result = _engine(tmp_path, enrichment=[FakeVidIQ(ENRICH)]).inspect(URL)
    cov = json.load(open(result["paths"]["provider_coverage"], encoding="utf-8"))
    assert "vidiq" in cov["providers_available"]
    assert cov["by_field"]["channel.total_views"] == "vidiq"
    assert cov["by_field"]["channel.creation_date"] == "vidiq"


def test_future_providers_are_unavailable():
    p = SocialBladeProvider()
    assert p.available() is False and p.fetch("x", {}) == {}


# --- orquestador: 9 ficheros, reproducibilidad, robustez ---------------------
def test_inspect_writes_all_nine_files(tmp_path):
    result = _engine(tmp_path, enrichment=[FakeVidIQ(ENRICH)]).inspect(URL)
    expected = {"youtube", "seo", "thumbnail", "popularity",      # base (YIE-001)
                "channel", "audience", "engagement", "competitive", "provider_coverage"}
    assert expected <= set(result["paths"])
    for path in result["paths"].values():
        assert os.path.exists(path)
    comp = json.load(open(result["paths"]["competitive"], encoding="utf-8"))
    assert comp["video_id"] == "F0tfsMwKk-M"
    assert comp["engagement"]["engagement_rate"] == 0.052
    assert comp["channel"]["total_videos"] == 400
    assert "thumbnail" in comp and "seo" in comp


def test_inspect_is_reproducible(tmp_path):
    a = _engine(tmp_path / "a", enrichment=[FakeVidIQ(ENRICH)]).inspect(URL)
    b = _engine(tmp_path / "b", enrichment=[FakeVidIQ(ENRICH)]).inspect(URL)
    for name in ("channel", "audience", "engagement", "competitive", "provider_coverage"):
        assert json.load(open(a["paths"][name], encoding="utf-8")) == \
            json.load(open(b["paths"][name], encoding="utf-8"))


def test_inspect_never_raises_on_provider_failure(tmp_path):
    class Boom:
        def fetch_metadata(self, url):
            raise RuntimeError("down")
        def fetch_thumbnail(self, raw, work_dir):
            raise RuntimeError("down")

    result = _engine(tmp_path, provider=Boom()).inspect(URL)
    assert result["available"] is False
    assert os.path.exists(result["paths"]["competitive"])      # se escribe igualmente
    cov = json.load(open(result["paths"]["provider_coverage"], encoding="utf-8"))
    assert cov["by_field"]["video.views"] == "UNKNOWN"


# --- integración Queue -> YIE(CI) -> DLE -------------------------------------
def test_queue_runs_competitive_intelligence_then_dle(tmp_path):
    from app.dle.queue import LearningQueueManager
    from app.dle.queue.index import KnowledgeIndex
    from app.dle.queue.store import QueueStore

    kroot = str(tmp_path / "knowledge")
    dle = _FakeDLE()
    yie = CompetitiveIntelligenceEngine(
        provider=FakeProvider(), enrichment_providers=[FakeVidIQ(ENRICH)],
        knowledge_root=kroot, reference_date=REF)
    mgr = LearningQueueManager(
        engine=dle,
        store=QueueStore(os.path.join(kroot, "q.json")),
        index=KnowledgeIndex(os.path.join(kroot, "idx.json")),
        knowledge_root=kroot, intelligence=yie)
    mgr.add_urls([URL])
    mgr.process_all()

    doc_dir = os.path.join(kroot, "documentaries", "doc_yt_F0tfsMwKk-M")
    for name in ("youtube.json", "seo.json", "thumbnail.json", "popularity.json",
                 "channel.json", "audience.json", "engagement.json", "competitive.json",
                 "provider_coverage.json"):
        assert os.path.exists(os.path.join(doc_dir, name))
    assert dle.learned == [URL]
    assert mgr.status()["documentaries_learned"] == 1
