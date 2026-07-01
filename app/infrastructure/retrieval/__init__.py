from app.infrastructure.retrieval.academic_fetcher import AcademicFetcher
from app.infrastructure.retrieval.archive_fetcher import ArchiveFetcher
from app.infrastructure.retrieval.news_fetcher import NewsFetcher
from app.infrastructure.retrieval.wikipedia_fetcher import WikipediaFetcher
from app.infrastructure.retrieval.youtube_fetcher import YouTubeFetcher

__all__ = [
    "WikipediaFetcher",
    "YouTubeFetcher",
    "NewsFetcher",
    "AcademicFetcher",
    "ArchiveFetcher",
]
