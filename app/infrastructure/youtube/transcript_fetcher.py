"""TranscriptFetcher: obtains a YouTube transcript when one is available.

The external dependency is intentionally encapsulated in this infrastructure
adapter. Domain, application, and CLI layers do not know it exists.
"""

import urllib.parse
import warnings
from typing import Any

import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)
from urllib3.exceptions import InsecureRequestWarning


class TranscriptFetcher:
    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout
        self._session = requests.Session()
        self._session.verify = False

    def fetch(self, url: str) -> str:
        """Return the full transcript text, or "" when no transcript is available."""
        try:
            video_id = self._extract_video_id(url)
            if not video_id:
                return ""
            transcript = self._fetch_transcript(video_id)
            return self._to_text(transcript)
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
            return ""
        except Exception:
            return ""

    def _extract_video_id(self, url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        host = parsed.netloc.lower()

        if host.endswith("youtu.be"):
            return parsed.path.strip("/")

        if "youtube.com" in host:
            query = urllib.parse.parse_qs(parsed.query)
            if "v" in query and query["v"]:
                return query["v"][0]
            if parsed.path.startswith("/shorts/"):
                return parsed.path.split("/")[2]
            if parsed.path.startswith("/embed/"):
                return parsed.path.split("/")[2]

        # Useful for local verification without changing the public interface.
        if "/" not in url and "?" not in url and len(url) >= 6:
            return url

        return ""

    def _fetch_transcript(self, video_id: str) -> Any:
        languages = ["es", "es-ES", "es-419", "en", "en-US", "en-GB"]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InsecureRequestWarning)

            # youtube-transcript-api 0.x exposed get_transcript as a class/static API.
            if hasattr(YouTubeTranscriptApi, "get_transcript"):
                return YouTubeTranscriptApi.get_transcript(
                    video_id, languages=languages
                )

            # youtube-transcript-api 1.x exposes an instance API.
            api = YouTubeTranscriptApi(http_client=self._session)
            return api.fetch(video_id, languages=languages)

    def _to_text(self, transcript: Any) -> str:
        lines: list[str] = []
        for item in transcript:
            text = self._item_text(item)
            if text:
                lines.append(text)
        return "\n".join(lines)

    def _item_text(self, item: Any) -> str:
        if isinstance(item, dict):
            return str(item.get("text", "")).strip()
        text = getattr(item, "text", "")
        if text is None:
            return ""
        return str(text).strip()
