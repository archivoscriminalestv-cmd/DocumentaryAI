"""SeedEvidenceProvider (ERE) — normaliza evidencia pública aportada por el Director.

Para casos true-crime sin presencia enciclopédica, el camino realista es que el
Director aporte referencias PÚBLICAS ya localizadas (titulares, URLs de noticias,
imágenes con licencia, vídeos, referencias judiciales). Este proveedor las
**normaliza** en nodos del grafo con su procedencia y confianza. NO inventa ni
interpreta: solo estructura lo que recibe.

Formato del seed (JSON), todas las claves opcionales:
    {
      "entities":  [{"canonical_name","type","aliases","attributes":{campo:valor},
                     "references":[...], "confidence", "url"}],
      "articles":  [{"headline","medium","date","url","snippet","entities_detected"}],
      "images":    [{"original_url","thumbnail_url","license","author","caption",
                     "resolution","quality","relevance","id"}],
      "videos":    [{"title","url","channel","duration","published","thumbnail_url","license"}],
      "court_documents": [{"title","reference","court","date","url"}],
      "relationships":   [{"source_id","relation","target_id","confidence"}]
    }
"""

import json
from typing import Any

from app.ere.models import (
    Article,
    Claim,
    CourtDocument,
    Entity,
    ImageAsset,
    ProjectQuery,
    Relationship,
    SourceRef,
    VideoAsset,
    slugify,
)
from app.ere.providers.base import EvidenceProvider, EvidenceResult

DEFAULT_CONFIDENCE = 0.6


class SeedEvidenceProvider(EvidenceProvider):
    name = "seed"

    def __init__(self, data: dict[str, Any] | None = None, path: str | None = None) -> None:
        self._data = data
        self._path = path

    def research(self, query: ProjectQuery) -> EvidenceResult:
        try:
            payload = self._load()
        except Exception as exc:
            return EvidenceResult(self.name, False, error=str(exc)[:160])
        if not payload:
            return EvidenceResult(self.name, False, notes="Sin datos seed.")

        sources: list[SourceRef] = []
        entities = [self._entity(e, sources) for e in payload.get("entities", [])]
        articles = [self._article(a, sources) for a in payload.get("articles", [])]
        images = [self._image(i, sources) for i in payload.get("images", [])]
        videos = [self._video(v, sources) for v in payload.get("videos", [])]
        courts = [self._court(c, sources) for c in payload.get("court_documents", [])]
        rels = [
            Relationship(
                source_id=r["source_id"], relation=r["relation"], target_id=r["target_id"],
                provider=self.name, confidence=float(r.get("confidence", DEFAULT_CONFIDENCE)),
            )
            for r in payload.get("relationships", [])
        ]

        available = any([entities, articles, images, videos, courts, rels])
        return EvidenceResult(
            self.name, available, entities=entities, articles=articles, images=images,
            videos=videos, court_documents=courts, relationships=rels, sources=sources,
            confidence=DEFAULT_CONFIDENCE,
            notes="Evidencia pública aportada por el Director (normalizada, no inventada).",
        )

    def _load(self) -> dict[str, Any] | None:
        if self._data is not None:
            return self._data
        if self._path:
            with open(self._path, encoding="utf-8") as handle:
                return json.load(handle)
        return None

    def _entity(self, raw: dict, sources: list[SourceRef]) -> Entity:
        name = raw.get("canonical_name", "")
        etype = raw.get("type", "character")
        conf = float(raw.get("confidence", DEFAULT_CONFIDENCE))
        url = raw.get("url", "")
        attrs: dict[str, list[Claim]] = {}
        for fname, value in (raw.get("attributes", {}) or {}).items():
            attrs[fname] = [Claim(fname, value, self.name, conf, url)]
        src = SourceRef(provider=self.name, url=url, source="seed", confidence=conf)
        if url:
            sources.append(src)
        return Entity(
            id=raw.get("id") or f"{etype}:{slugify(name)}",
            type=etype, canonical_name=name, aliases=list(raw.get("aliases", [])),
            attributes=attrs, references=list(raw.get("references", [])),
            sources=[src] if url else [], metadata=dict(raw.get("metadata", {})),
        )

    def _article(self, raw: dict, sources: list[SourceRef]) -> Article:
        conf = float(raw.get("confidence", DEFAULT_CONFIDENCE))
        url = raw.get("url", "")
        src = SourceRef(provider=self.name, url=url, source=raw.get("medium", "seed"),
                        confidence=conf)
        if url:
            sources.append(src)
        return Article(
            id=raw.get("id") or f"article:{slugify(raw.get('headline', ''))}",
            headline=raw.get("headline", ""), medium=raw.get("medium", ""),
            date=raw.get("date", ""), url=url, snippet=raw.get("snippet", ""),
            entities_detected=list(raw.get("entities_detected", [])), source=src,
        )

    def _image(self, raw: dict, sources: list[SourceRef]) -> ImageAsset:
        url = raw.get("original_url", "")
        if url:
            sources.append(SourceRef(provider=self.name, url=url, source="seed-image",
                                     confidence=DEFAULT_CONFIDENCE,
                                     license=raw.get("license", "")))
        return ImageAsset(
            id=raw.get("id") or f"image:{slugify(raw.get('caption', '') or url)}",
            provider=self.name, original_url=url,
            thumbnail_url=raw.get("thumbnail_url", ""), license=raw.get("license", ""),
            author=raw.get("author", ""), caption=raw.get("caption", ""),
            resolution=raw.get("resolution", ""),
            quality=float(raw.get("quality", 0.0)), relevance=float(raw.get("relevance", 0.0)),
        )

    def _video(self, raw: dict, sources: list[SourceRef]) -> VideoAsset:
        url = raw.get("url", "")
        if url:
            sources.append(SourceRef(provider=self.name, url=url, source="seed-video",
                                     confidence=DEFAULT_CONFIDENCE))
        return VideoAsset(
            id=raw.get("id") or f"video:{slugify(raw.get('title', '') or url)}",
            provider=self.name, title=raw.get("title", ""), url=url,
            channel=raw.get("channel", ""), duration=raw.get("duration", ""),
            published=raw.get("published", ""), thumbnail_url=raw.get("thumbnail_url", ""),
            license=raw.get("license", ""), metadata=dict(raw.get("metadata", {})),
        )

    def _court(self, raw: dict, sources: list[SourceRef]) -> CourtDocument:
        url = raw.get("url", "")
        if url:
            sources.append(SourceRef(provider=self.name, url=url, source="seed-court",
                                     confidence=DEFAULT_CONFIDENCE))
        return CourtDocument(
            id=raw.get("id") or f"court:{slugify(raw.get('reference', '') or raw.get('title', ''))}",
            provider=self.name, title=raw.get("title", ""),
            reference=raw.get("reference", ""), court=raw.get("court", ""),
            date=raw.get("date", ""), url=url,
        )
