"""Tests del Source Retrieval Engine (C-03). Sin red real, sin IA, determinista."""

import json
from dataclasses import asdict

from app.application.retrieval_service import RetrievalService
from app.domain.search import SearchPriority, SearchTask, SearchType
from app.domain.source.retrieved_source import RetrievedSource
from app.infrastructure.retrieval import (
    AcademicFetcher,
    ArchiveFetcher,
    NewsFetcher,
    WikipediaFetcher,
    YouTubeFetcher,
)


def _task(type_: SearchType, query: str = "Q", id_: str = "task-01") -> SearchTask:
    return SearchTask(id=id_, type=type_, query=query, priority=SearchPriority.HIGH, reason="r")


# --- Fetchers de prueba ------------------------------------------------------

class _FakeFetcher:
    def __init__(self, type_: SearchType, sources: list[RetrievedSource]):
        self._type = type_
        self._sources = sources

    def handles(self, search_type: SearchType) -> bool:
        return search_type == self._type

    def fetch(self, task: SearchTask) -> list[RetrievedSource]:
        return list(self._sources)


class _BoomFetcher:
    def handles(self, search_type: SearchType) -> bool:
        return True

    def fetch(self, task: SearchTask) -> list[RetrievedSource]:
        raise RuntimeError("boom")


def _src(title: str, url: str, type_=SearchType.WIKIPEDIA) -> RetrievedSource:
    return RetrievedSource(id="", type=type_, title=title, url=url)


# --- RetrievalService --------------------------------------------------------

def test_routes_task_to_matching_fetcher_by_type():
    wiki = _FakeFetcher(SearchType.WIKIPEDIA, [_src("Mars", "http://w/Mars")])
    news = _FakeFetcher(SearchType.NEWS, [_src("News", "http://n/1", SearchType.NEWS)])
    service = RetrievalService([wiki, news])

    out = service.retrieve([_task(SearchType.WIKIPEDIA)])

    assert [s.title for s in out] == ["Mars"]  # solo el fetcher de wikipedia respondió


def test_unmatched_type_yields_no_sources():
    wiki = _FakeFetcher(SearchType.WIKIPEDIA, [_src("Mars", "http://w/Mars")])
    service = RetrievalService([wiki])

    assert service.retrieve([_task(SearchType.BOOKS)]) == []


def test_deduplicates_by_url_then_title():
    dupes = [
        _src("Mars", "http://w/Mars"),
        _src("Mars (planet)", "http://w/Mars"),   # misma url -> duplicado
        _src("Mars", "http://w/Other"),            # mismo título -> duplicado
        _src("Venus", "http://w/Venus"),
    ]
    service = RetrievalService([_FakeFetcher(SearchType.WIKIPEDIA, dupes)])

    out = service.retrieve([_task(SearchType.WIKIPEDIA)])

    assert [s.url for s in out] == ["http://w/Mars", "http://w/Venus"]
    assert [s.id for s in out] == ["src-01", "src-02"]  # ids deterministas


def test_failing_fetcher_degrades_to_empty_without_crashing():
    service = RetrievalService([_BoomFetcher()])
    assert service.retrieve([_task(SearchType.WIKIPEDIA)]) == []


def test_output_is_json_serializable():
    service = RetrievalService([_FakeFetcher(SearchType.WIKIPEDIA, [_src("Mars", "http://w/Mars")])])
    out = service.retrieve([_task(SearchType.WIKIPEDIA)])

    decoded = json.loads(json.dumps([asdict(s) for s in out], ensure_ascii=False))
    assert decoded[0]["type"] == "wikipedia"
    assert decoded[0]["url"] == "http://w/Mars"


def test_retrieval_is_deterministic():
    fetcher = _FakeFetcher(SearchType.WIKIPEDIA, [_src("Mars", "http://w/Mars"), _src("Venus", "http://w/Venus")])
    service = RetrievalService([fetcher])
    tasks = [_task(SearchType.WIKIPEDIA)]

    a = service.retrieve(tasks)
    b = service.retrieve(tasks)
    assert [asdict(x) for x in a] == [asdict(x) for x in b]


# --- WikipediaFetcher (real, con HTTP inyectado) -----------------------------

_WIKI_JSON = json.dumps({
    "pages": [
        {"id": 1, "key": "Fermi_paradox", "title": "Fermi paradox",
         "excerpt": "The <span class=\"searchmatch\">Fermi</span> paradox is...",
         "description": "Absence of evidence for extraterrestrial civilizations"},
        {"id": 2, "key": "Drake_equation", "title": "Drake equation",
         "excerpt": "probabilistic argument", "description": ""},
        {"id": 3, "key": "", "title": "", "excerpt": "x", "description": "y"},  # inválida -> descartada
    ]
})


def test_wikipedia_fetcher_parses_injected_response():
    fetcher = WikipediaFetcher(http_get=lambda url, timeout: _WIKI_JSON)

    out = fetcher.fetch(_task(SearchType.WIKIPEDIA, query="The Fermi Paradox"))

    assert len(out) == 2  # la entrada inválida (sin title/key) se descarta
    assert out[0].title == "Fermi paradox"
    assert out[0].url == "https://en.wikipedia.org/wiki/Fermi_paradox"
    assert out[0].snippet == "Absence of evidence for extraterrestrial civilizations"
    # sin description -> usa el excerpt con HTML eliminado
    assert out[1].snippet == "probabilistic argument"
    assert all(s.type == SearchType.WIKIPEDIA for s in out)
    assert all(s.query == "The Fermi Paradox" for s in out)


def test_wikipedia_fetcher_handles_only_wikipedia():
    fetcher = WikipediaFetcher(http_get=lambda url, timeout: _WIKI_JSON)
    assert fetcher.handles(SearchType.WIKIPEDIA)
    assert not fetcher.handles(SearchType.NEWS)


def test_wikipedia_fetcher_degrades_on_http_error():
    def boom(url, timeout):
        raise OSError("network down")

    fetcher = WikipediaFetcher(http_get=boom)
    assert fetcher.fetch(_task(SearchType.WIKIPEDIA)) == []


def test_wikipedia_fetcher_degrades_on_bad_json():
    fetcher = WikipediaFetcher(http_get=lambda url, timeout: "not json")
    assert fetcher.fetch(_task(SearchType.WIKIPEDIA)) == []


# --- Stubs -------------------------------------------------------------------

def test_stub_fetchers_return_empty_and_route_correctly():
    assert YouTubeFetcher().handles(SearchType.YOUTUBE)
    assert NewsFetcher().handles(SearchType.NEWS)
    assert AcademicFetcher().handles(SearchType.SCIENTIFIC_PAPERS)
    assert ArchiveFetcher().handles(SearchType.GOVERNMENT)
    for stub in (YouTubeFetcher(), NewsFetcher(), AcademicFetcher(), ArchiveFetcher()):
        assert stub.fetch(_task(SearchType.YOUTUBE)) == []
