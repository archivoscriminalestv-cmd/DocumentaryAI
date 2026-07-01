"""WikipediaProvider (ERE) — evidencia enciclopédica del sujeto, si existe.

Emite una Entity 'character' con un extracto biográfico atribuido. Pensado para
sujetos con presencia enciclopédica; para casos true-crime puede devolver
``available=False`` (y el pipeline continúa, sin inventar nada).
"""

import urllib.parse

from app.ere.http import HttpClient, JsonHttpClient
from app.ere.models import Claim, Entity, ProjectQuery, SourceRef
from app.ere.providers.base import EvidenceProvider, EvidenceResult

CONFIDENCE = 0.8


class WikipediaProvider(EvidenceProvider):
    name = "wikipedia"

    def __init__(self, client: HttpClient | None = None, lang: str = "en") -> None:
        self._client = client or JsonHttpClient()
        self._lang = lang

    def research(self, query: ProjectQuery) -> EvidenceResult:
        title = urllib.parse.quote(query.name.replace(" ", "_"))
        url = f"https://{self._lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
        try:
            summary = self._client.get_json(url)
        except Exception as exc:
            return EvidenceResult(self.name, False, error=str(exc)[:160])

        if not isinstance(summary, dict) or summary.get("type") == "disambiguation":
            return EvidenceResult(self.name, False, error="sin artículo o desambiguación")

        canonical = summary.get("title", "") or query.name
        extract = summary.get("extract", "") or ""
        page_url = summary.get("content_urls", {}).get("desktop", {}).get("page", "")
        source = SourceRef(
            provider=self.name, url=page_url, source="Wikipedia",
            confidence=CONFIDENCE, license="CC BY-SA",
        )
        entity = Entity(
            id=query.subject_id(),
            type="character",
            canonical_name=canonical,
            aliases=list(query.aliases),
            attributes={
                "biography_summary": [
                    Claim("biography_summary", extract, self.name, CONFIDENCE, page_url)
                ]
            } if extract else {},
            sources=[source],
        )
        return EvidenceResult(
            self.name, True, entities=[entity], sources=[source],
            confidence=CONFIDENCE, notes="Extracto enciclopédico (sin resumen IA).",
        )
