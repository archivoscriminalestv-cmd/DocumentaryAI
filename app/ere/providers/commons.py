"""CommonsProvider (ERE) — cataloga evidencia visual pública (Wikimedia Commons).

Registra metadatos de imágenes asociadas al artículo del sujeto (URL, licencia,
autor, resolución, calidad). NO descarga imágenes (``hash`` reservado). Crea además
relaciones ``subject -> has_reference -> image``.
"""

import re

from app.ere.http import HttpClient, JsonHttpClient
from app.ere.models import ImageAsset, ProjectQuery, Relationship, SourceRef, slugify
from app.ere.providers.base import EvidenceProvider, EvidenceResult

CONFIDENCE = 0.7
MAX_IMAGES = 12
_IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".gif")
_TAG_RE = re.compile(r"<[^>]+>")


class CommonsProvider(EvidenceProvider):
    name = "commons"

    def __init__(self, client: HttpClient | None = None, lang: str = "en") -> None:
        self._client = client or JsonHttpClient()
        self._lang = lang

    def research(self, query: ProjectQuery) -> EvidenceResult:
        try:
            files = self._page_images(query.name)
        except Exception as exc:
            return EvidenceResult(self.name, False, error=str(exc)[:160])

        images: list[ImageAsset] = []
        relationships: list[Relationship] = []
        sources: list[SourceRef] = []
        for title in files[:MAX_IMAGES]:
            try:
                asset = self._image_asset(title)
            except Exception:
                continue
            if asset is None:
                continue
            images.append(asset)
            relationships.append(
                Relationship(query.subject_id(), "has_reference", asset.id,
                             self.name, CONFIDENCE)
            )
            sources.append(
                SourceRef(provider=self.name, url=asset.original_url,
                          source="Wikimedia Commons", confidence=CONFIDENCE,
                          license=asset.license)
            )

        if not images:
            return EvidenceResult(self.name, False, error="sin imágenes")

        return EvidenceResult(
            self.name, True, images=images, relationships=relationships,
            sources=sources, confidence=CONFIDENCE,
            notes=f"{len(images)} imagen(es) catalogada(s) (sin descarga).",
        )

    def _page_images(self, name: str) -> list[str]:
        data = self._client.get_json(
            f"https://{self._lang}.wikipedia.org/w/api.php",
            {"action": "query", "prop": "images", "imlimit": 50, "redirects": 1,
             "titles": name, "format": "json"},
        )
        titles: list[str] = []
        for page in data.get("query", {}).get("pages", {}).values():
            for image in page.get("images", []):
                title = image.get("title", "")
                if title.lower().endswith(_IMAGE_EXTS) and title not in titles:
                    titles.append(title)
        return titles

    def _image_asset(self, file_title: str) -> ImageAsset | None:
        data = self._client.get_json(
            "https://commons.wikimedia.org/w/api.php",
            {"action": "query", "prop": "imageinfo", "iiprop": "url|size|extmetadata",
             "titles": file_title, "format": "json"},
        )
        for page in data.get("query", {}).get("pages", {}).values():
            infos = page.get("imageinfo") or []
            if not infos:
                continue
            info = infos[0]
            meta = info.get("extmetadata", {})
            width = info.get("width", 0) or 0
            height = info.get("height", 0) or 0
            author = _clean(meta.get("Artist", {}).get("value", ""))
            return ImageAsset(
                id=f"image:{slugify(file_title)}",
                provider=self.name,
                original_url=info.get("url", ""),
                thumbnail_url=info.get("thumburl", "") or info.get("url", ""),
                license=_clean(meta.get("LicenseShortName", {}).get("value", "")),
                author=author,
                caption=file_title,
                resolution=f"{width}x{height}" if width and height else "",
                quality=_quality(width, height),
                relevance=0.0,
            )
        return None


def _clean(value: str) -> str:
    return _TAG_RE.sub("", value or "").strip()


def _quality(width: int, height: int) -> float:
    if not width or not height:
        return 0.0
    return round(min(1.0, (width * height) / (1920 * 1080)), 3)
