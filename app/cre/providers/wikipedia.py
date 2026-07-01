"""WikipediaProvider real — investiga vía la REST API pública de Wikipedia.

Obtiene nombre canónico y un extracto biográfico (texto enciclopédico, sin resumen
por IA). NO inventa: si no hay artículo o es desambiguación, devuelve
``available=False``. La integración HTTP es inyectable (``client``) para que los
tests la mockeen por completo.

Endpoint: ``/api/rest_v1/page/summary/{title}``  (sin API key).
"""

import urllib.parse

from app.cre.http import HttpClient, JsonHttpClient
from app.cre.models import CharacterRequest
from app.cre.providers.base import ResearchProvider, ResearchResult

CONFIDENCE = 0.8


class WikipediaProvider(ResearchProvider):
    name = "wikipedia"

    def __init__(self, client: HttpClient | None = None, lang: str = "en") -> None:
        self._client = client or JsonHttpClient()
        self._lang = lang

    def research(self, request: CharacterRequest) -> ResearchResult:
        title = urllib.parse.quote(request.name.replace(" ", "_"))
        url = f"https://{self._lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
        try:
            summary = self._client.get_json(url)
        except Exception as exc:  # red/HTTP: degradación limpia, sin inventar
            return ResearchResult(self.name, False, error=str(exc)[:160])

        if not isinstance(summary, dict) or summary.get("type") == "disambiguation":
            return ResearchResult(self.name, False, error="sin artículo o desambiguación")

        canonical = summary.get("title", "") or ""
        extract = summary.get("extract", "") or ""
        if not canonical and not extract:
            return ResearchResult(self.name, False, error="artículo vacío")

        page_url = (
            summary.get("content_urls", {})
            .get("desktop", {})
            .get("page", "")
        )
        data = {
            "identity": {"canonical_name": canonical},
            "biography": {"summary": extract},
        }
        return ResearchResult(
            provider=self.name,
            available=True,
            data=data,
            sources=[page_url] if page_url else [],
            confidence=CONFIDENCE,
            notes="Extracto enciclopédico (sin resumen IA).",
        )
