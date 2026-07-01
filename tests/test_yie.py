"""Tests del YouTube Intelligence Engine (YIE-001) — deterministas, sin red.

Toda la red está mockeada con proveedores falsos. Cubren metadata, SEO, miniatura,
popularidad, serialización, reproducibilidad, proveedor independiente e integración
Queue → YIE → DLE.
"""

import json
import os
from datetime import date

from app.yie.channel import parse_channel
from app.yie.metadata import extract_video_id, parse_metrics, parse_video
from app.yie.orchestrator import YouTubeIntelligenceEngine
from app.yie.popularity import compute_popularity
from app.yie.seo import analyze_seo
from app.yie.thumbnail import analyze_thumbnail

URL = "https://www.youtube.com/watch?v=F0tfsMwKk-M"

RAW = {
    "id": "F0tfsMwKk-M",
    "title": "The SHOCKING True Crime Case of 2021?? #truecrime",
    "description": "A documentary about a real case. More at https://x #crime",
    "upload_date": "20210104",
    "duration": 612.0,
    "categories": ["Education"],
    "language": "en",
    "tags": ["true crime", "documentary"],
    "license": "Standard YouTube License",
    "fps": 30.0,
    "width": 1920,
    "height": 1080,
    "view_count": 1_000_000,
    "like_count": 50_000,
    "comment_count": 2_000,
    "channel_id": "UC123",
    "channel": "Crime Docs",
    "channel_follower_count": 500_000,
    "channel_total_views": 200_000_000,
    "channel_total_videos": 400,
    "chapters": [{"title": "Intro", "start_time": 0, "end_time": 30}],
    "subtitles": {"en": [{}], "es": [{}]},
    "thumbnail": "https://img/thumb.jpg",
}

REF = date(2021, 1, 11)   # 7 días después de la publicación → determinista


class FakeProvider:
    """Proveedor falso: devuelve metadatos canónicos y genera una miniatura local."""

    def __init__(self, raw=None, color=(200, 50, 50)):
        self._raw = RAW if raw is None else raw
        self._color = color

    def fetch_metadata(self, url):
        return dict(self._raw)

    def fetch_thumbnail(self, raw, work_dir):
        from PIL import Image
        os.makedirs(work_dir, exist_ok=True)
        path = os.path.join(work_dir, "t.png")
        Image.new("RGB", (120, 90), self._color).save(path)
        return path


def _engine(tmp_path, provider=None):
    return YouTubeIntelligenceEngine(
        provider=provider or FakeProvider(),
        knowledge_root=str(tmp_path / "knowledge"),
        reference_date=REF,
    )


# --- metadata ----------------------------------------------------------------
def test_extract_video_id():
    assert extract_video_id(URL) == "F0tfsMwKk-M"
    assert extract_video_id("https://youtu.be/abcDEF123") == "abcDEF123"
    assert extract_video_id("not a url") == ""


def test_parse_video_and_metrics():
    v = parse_video(RAW)
    assert v.video_id == "F0tfsMwKk-M"
    assert v.publish_date == "2021-01-04"
    assert v.duration == 612.0 and v.fps == 30.0
    assert v.category == "Education" and v.language == "en"
    assert v.tags == ["true crime", "documentary"]
    assert v.hashtags == ["truecrime", "crime"]
    assert v.subtitles == ["en", "es"]
    assert v.resolution == "1920x1080"
    m = parse_metrics(RAW)
    assert (m.views, m.likes, m.comments) == (1_000_000, 50_000, 2_000)


def test_channel_average_views():
    c = parse_channel(RAW)
    assert c.channel_name == "Crime Docs" and c.subscribers == 500_000
    assert c.average_views == 500000.0       # 200M / 400


def test_unknown_when_missing():
    v = parse_video({})
    assert v.video_id == "UNKNOWN" and v.duration is None and v.resolution == "UNKNOWN"
    m = parse_metrics({})
    assert m.views is None and m.likes is None


# --- SEO ---------------------------------------------------------------------
def test_seo_rules_are_deterministic():
    seo = analyze_seo(parse_video(RAW))
    assert seo.has_year is True and seo.is_question is True and seo.has_numbers is True
    assert seo.uppercase_ratio > 0.0
    assert seo.hashtag_count == 2 and seo.tag_count == 2   # #truecrime + #crime
    assert "crime" in seo.significant_words and "shocking" in seo.significant_words
    assert seo.emoji_count == 0


def test_seo_detects_emoji():
    v = parse_video({**RAW, "title": "Crimen real 🔪😱"})
    seo = analyze_seo(v)
    assert seo.has_emoji is True and seo.emoji_count == 2


# --- miniatura ---------------------------------------------------------------
def test_thumbnail_objective_attributes(tmp_path):
    from PIL import Image
    p = str(tmp_path / "warm.png")
    Image.new("RGB", (120, 90), (200, 50, 50)).save(p)        # rojizo → warm
    t = analyze_thumbnail(p)
    assert t.available is True
    assert t.resolution == "120x90" and t.width == 120 and t.height == 90
    assert t.color_temperature == "warm"
    assert t.dominant_color.startswith("#")
    assert len(t.histogram["r"]) == 16 and len(t.histogram["b"]) == 16
    assert 0.0 <= t.brightness <= 1.0 and 0.0 <= t.saturation <= 1.0


def test_thumbnail_missing_is_unavailable():
    t = analyze_thumbnail(None)
    assert t.available is False and t.resolution == "UNKNOWN"


# --- popularidad -------------------------------------------------------------
def test_popularity_derived_metrics_deterministic():
    pop = compute_popularity(parse_metrics(RAW), "2021-01-04", REF)
    assert pop.age_days == 7
    assert pop.views_per_day == round(1_000_000 / 7, 4)
    assert pop.likes_per_view == 0.05
    assert pop.comments_per_view == 0.002
    assert pop.engagement_rate == 0.052
    assert pop.reference_date == "2021-01-11"


def test_popularity_handles_missing_metrics():
    from app.yie.models import VideoMetrics
    pop = compute_popularity(VideoMetrics(), "UNKNOWN", REF)
    assert pop.age_days is None and pop.views_per_day is None and pop.engagement_rate is None


# --- orquestador / serialización / reproducibilidad --------------------------
def test_inspect_writes_four_json_files(tmp_path):
    result = _engine(tmp_path).inspect(URL)
    assert result["documentary_id"] == "doc_yt_F0tfsMwKk-M"
    for name in ("youtube", "seo", "thumbnail", "popularity"):
        assert os.path.exists(result["paths"][name])
    yt = json.load(open(result["paths"]["youtube"], encoding="utf-8"))
    assert yt["video"]["title"].startswith("The SHOCKING")
    assert yt["metrics"]["views"] == 1_000_000


def test_inspect_is_reproducible(tmp_path):
    a = _engine(tmp_path / "a").inspect(URL)
    b = _engine(tmp_path / "b").inspect(URL)
    for name in ("youtube", "seo", "thumbnail", "popularity"):
        da = json.load(open(a["paths"][name], encoding="utf-8"))
        db = json.load(open(b["paths"][name], encoding="utf-8"))
        assert da == db                       # misma URL → mismos JSON


def test_provider_independent_degrades_to_unknown(tmp_path):
    class EmptyProvider:
        def fetch_metadata(self, url):
            return {}
        def fetch_thumbnail(self, raw, work_dir):
            return None

    result = _engine(tmp_path, provider=EmptyProvider()).inspect(URL)
    assert result["available"] is False
    assert result["documentary_id"] == "doc_yt_F0tfsMwKk-M"   # id desde la URL
    yt = json.load(open(result["paths"]["youtube"], encoding="utf-8"))
    assert yt["video"]["video_id"] in ("F0tfsMwKk-M", "UNKNOWN")
    thumb = json.load(open(result["paths"]["thumbnail"], encoding="utf-8"))
    assert thumb["available"] is False


def test_engine_never_raises_on_provider_error(tmp_path):
    class BoomProvider:
        def fetch_metadata(self, url):
            raise RuntimeError("network down")
        def fetch_thumbnail(self, raw, work_dir):
            raise RuntimeError("no thumb")

    result = _engine(tmp_path, provider=BoomProvider()).inspect(URL)
    assert result["available"] is False and os.path.exists(result["paths"]["youtube"])


# --- integración Queue -> YIE -> DLE -----------------------------------------
class _FakeDLE:
    def __init__(self):
        self.store = _FakeStore()
        self.learned = []

    def learn(self, *, youtube=None, video=None, force=False, on_stage=None,
              work_dir=None, on_event=None):
        ref = youtube or video
        self.learned.append(ref)
        from app.dle.queue.downloader import resolve_source
        doc_id = resolve_source(ref).documentary_id
        self.store.add(doc_id)

        class _K:
            schema_version = "1.0"

            class statistics:
                shot_count = 0
                scene_count = 0
        return {"status": "learned", "documentary_id": doc_id, "knowledge": _K()}


class _FakeStore:
    def __init__(self):
        self._ids = set()

    def add(self, doc_id):
        self._ids.add(doc_id)

    def exists(self, doc_id):
        return doc_id in self._ids


def test_queue_runs_yie_then_dle(tmp_path):
    from app.dle.queue import LearningQueueManager
    from app.dle.queue.index import KnowledgeIndex
    from app.dle.queue.store import QueueStore

    kroot = str(tmp_path / "knowledge")
    dle = _FakeDLE()
    yie = YouTubeIntelligenceEngine(provider=FakeProvider(), knowledge_root=kroot,
                                    reference_date=REF)
    mgr = LearningQueueManager(
        engine=dle,
        store=QueueStore(os.path.join(kroot, "q.json")),
        index=KnowledgeIndex(os.path.join(kroot, "idx.json")),
        knowledge_root=kroot,
        intelligence=yie,
    )
    mgr.add_urls([URL])
    mgr.process_all()

    # YIE corrió ANTES del DLE y escribió su conocimiento...
    doc_dir = os.path.join(kroot, "documentaries", "doc_yt_F0tfsMwKk-M")
    for name in ("youtube.json", "seo.json", "thumbnail.json", "popularity.json"):
        assert os.path.exists(os.path.join(doc_dir, name))
    # ...y el DLE se ejecutó igualmente.
    assert dle.learned == [URL]
    assert mgr.status()["documentaries_learned"] == 1
