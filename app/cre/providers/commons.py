"""CommonsProvider real — localiza REFERENCIAS visuales públicas (Wikimedia Commons).

Registra metadatos de imágenes asociadas al artículo del personaje (URL, licencia,
autor, descripción, resolución). NO descarga imágenes (``hash`` queda reservado para
una futura descarga) y NO genera prompts ni consistencia: solo cataloga referencias
trazables con su licencia.

Flujo: imágenes del artículo (Wikipedia) -> imageinfo de cada fichero (Commons).
Integración HTTP inyectable para tests.
"""

import re

from app.cre.http import HttpClient, JsonHttpClient
from app.cre.models import CharacterRequest, VisualReference, slugify
from app.cre.providers.base import ResearchProvider, ResearchResult

CONFIDENCE = 0.7
MAX_REFERENCES = 12
_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".gif")
_TAG_RE = re.compile(r"<[^>]+>")


class CommonsProvider(ResearchProvider):
    name = "commons"

    def __init__(self, client: HttpClient | None = None, lang: str = "en") -> None:
        self._client = client or JsonHttpClient()
        self._lang = lang

    def research(self, request: CharacterRequest) -> ResearchResult:
        try:
            files = self._page_images(request.name)
        except Exception as exc:
            return ResearchResult(self.name, False, error=str(exc)[:160])

        references: list[VisualReference] = []
        errors: list[str] = []
        for title in files[:MAX_REFERENCES]:
            try:
                ref = self._image_reference(title)
            except Exception as exc:  # un fichero que falla no aborta el resto
                errors.append(str(exc)[:80])
                continue
            if ref is not None:
                references.append(ref)

        if not references:
            return ResearchResult(
                self.name, False, error="; ".join(errors)[:160] or "sin imágenes"
            )

        return ResearchResult(
            provider=self.name,
            available=True,
            data={},
            visual_references=references,
            sources=["https://commons.wikimedia.org"],
            confidence=CONFIDENCE,
            notes=f"{len(references)} referencia(s) visual(es) catalogada(s) (sin descarga).",
        )

    def _page_images(self, name: str) -> list[str]:
        api = f"https://{self._lang}.wikipedia.org/w/api.php"
        data = self._client.get_json(
            api,
            {
                "action": "query",
                "prop": "images",
                "imlimit": 50,
                "redirects": 1,
                "titles": name,
                "format": "json",
            },
        )
        titles: list[str] = []
        for page in data.get("query", {}).get("pages", {}).values():
            for image in page.get("images", []):
                title = image.get("title", "")
                if title.lower().endswith(_IMAGE_EXTS) and title not in titles:
                    titles.append(title)
        return titles

    def _image_reference(self, file_title: str) -> VisualReference | None:
        data = self._client.get_json(
            "https://commons.wikimedia.org/w/api.php",
            {
                "action": "query",
                "prop": "imageinfo",
                "iiprop": "url|size|extmetadata",
                "titles": file_title,
                "format": "json",
            },
        )
        for page in data.get("query", {}).get("pages", {}).values():
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            info = infos[0]
            meta = info.get("extmetadata", {})
            width = info.get("width", 0) or 0
            height = info.get("height", 0) or 0
            return VisualReference(
                id=slugify(file_title),
                provider=self.name,
                source="wikimedia-commons",
                url=info.get("url", ""),
                license=_clean(meta.get("LicenseShortName", {}).get("value", "")),
                copyright=_clean(meta.get("Artist", {}).get("value", "")),
                author=_clean(meta.get("Artist", {}).get("value", "")),
                caption=file_title,
                description=_clean(meta.get("ImageDescription", {}).get("value", ""))[:280],
                resolution=f"{width}x{height}" if width and height else "",
                quality_score=_quality(width, height),
                relevance_score=0.0,  # reservado (sin puntuación inventada)
            )
        return None


def _clean(value: str) -> str:
    """Elimina etiquetas HTML y espacios sobrantes de los metadatos de Commons."""
    return _TAG_RE.sub("", value or "").strip()


def _quality(width: int, height: int) -> float:
    """Métrica determinista de resolución (0..1) relativa a 1080p. No es un hecho."""
    if not width or not height:
        return 0.0
    ratio = (width * height) / (1920 * 1080)
    return round(min(1.0, ratio), 3)
