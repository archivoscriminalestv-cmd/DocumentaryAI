"""Proveedores de descubrimiento REALES (EAE-004, fase 1).

Wikimedia Commons, Internet Archive, OpenStreetMap (Nominatim), Wikidata y Wikipedia, vía
sus APIs/endpoints JSON oficiales. NUNCA scraping/Selenium/Playwright/HTML; el HTTP es
inyectable (``HttpClient``) y opcional: sin cliente el proveedor actúa como CONTRATO
(``available()`` False), de modo que el descubrimiento offline sigue siendo determinista.

Pensados como un documentalista: priorizan calidad/licencia/fiabilidad sobre cantidad. Cada
``DiscoveredEvidence`` queda autocontenida (URL + metadatos) para que la ADQUISICIÓN futura
no tenga que volver a consultar al proveedor. UNKNOWN antes que inventar; orden determinista.
"""

import re

from app.eae import UNKNOWN
from app.eae.discovery.cache import cache_key
from app.eae.discovery.models import Availability, DiscoveredEvidence
from app.eae.discovery.providers.base import BaseDiscoveryProvider, DiscoveryQuery
from app.eae.planner.models import EvidenceCategory as C
from app.eae.planner.models import slugify

_TAG_RE = re.compile(r"<[^>]+>")
_PD = ("PUBLIC_DOMAIN", "CC0", "CC-BY", "CC-BY-SA")


def _clean(value) -> str:
    if not isinstance(value, str):
        return ""
    return _TAG_RE.sub("", value).strip()


def _terms(query: DiscoveryQuery) -> str:
    if query.terms:
        return " ".join(t for t in query.terms if t)
    return query.target if query.target and query.target != "case" else ""


class RealDiscoveryProvider(BaseDiscoveryProvider):
    """Base de los proveedores reales: cache + HTTP seguro + orden determinista."""

    def __init__(self, http=None, cache=None) -> None:
        self._http = http
        self._cache = cache

    def available(self) -> bool:
        return self._http is not None

    def discover(self, query: DiscoveryQuery) -> list[DiscoveredEvidence]:
        if not self.available():
            return []
        key = cache_key(self.name, category=query.category, target=query.target,
                        terms=query.terms, language=query.language,
                        filters=query.license_requirements)
        if self._cache is not None:
            cached = self._cache.get(key)
            if cached is not None:
                return cached
        try:
            results = self._search(query)
        except Exception:
            return []                       # nunca cachea errores; nunca rompe el pipeline
        results = sorted(results, key=lambda e: e.id)[: max(0, query.limit) or None]
        if self._cache is not None:
            self._cache.set(key, results)
        return results

    def _search(self, query: DiscoveryQuery) -> list[DiscoveredEvidence]:
        raise NotImplementedError


class WikimediaCommonsProvider(RealDiscoveryProvider):
    name = "wikimedia_commons"
    _media = (C.PHOTO, C.MAP, C.SCENE_PHOTO, C.PUBLIC_RECORD)
    _licenses = _PD
    _priority = 10
    _cost = "free"
    _rate_limits = {"requests_per_minute": 200}
    _capabilities = ("search", "metadata", "download")
    _reliability = "HIGH"

    def _search(self, query):
        terms = _terms(query)
        if not terms:
            return []
        data = self._http.get("https://commons.wikimedia.org/w/api.php", params={
            "action": "query", "generator": "search", "gsrsearch": terms,
            "gsrnamespace": 6, "gsrlimit": query.limit, "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata", "format": "json",
        }).json()
        out = []
        for page in (data.get("query", {}).get("pages", {}) or {}).values():
            info = (page.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata", {}) or {}
            title = page.get("title", "")
            w, h = info.get("width", 0) or 0, info.get("height", 0) or 0
            out.append(DiscoveredEvidence(
                id=f"{self.name}:{slugify(title)}", need_id=query.need_id,
                target=query.target, category=query.category, title=title,
                url=info.get("url", ""), provider=self.name,
                media_type=info.get("mime", UNKNOWN) or UNKNOWN,
                license=_clean(meta.get("LicenseShortName", {}).get("value")) or UNKNOWN,
                resolution=f"{w}x{h}" if w and h else UNKNOWN,
                fmt=(info.get("mime", "").split("/")[-1] or UNKNOWN),
                date=_clean(meta.get("DateTimeOriginal", {}).get("value")) or UNKNOWN,
                reliability=self._reliability, availability=Availability.AVAILABLE,
                priority=query.priority, query_used=[terms],
                extra={"author": _clean(meta.get("Artist", {}).get("value")),
                       "description": _clean(meta.get("ImageDescription", {}).get("value"))[:280],
                       "categories": _clean(meta.get("Categories", {}).get("value")),
                       "descriptionurl": info.get("descriptionurl", "")},
            ))
        return out


class InternetArchiveProvider(RealDiscoveryProvider):
    name = "internet_archive"
    _media = (C.ARCHIVE_VIDEO, C.VIDEO, C.AUDIO, C.BOOK, C.NEWSPAPER, C.TV_REPORT)
    _licenses = _PD
    _priority = 15
    _cost = "free"
    _rate_limits = {"requests_per_minute": 60}
    _capabilities = ("search", "metadata", "download")
    _reliability = "HIGH"

    def _search(self, query):
        terms = _terms(query)
        if not terms:
            return []
        data = self._http.get("https://archive.org/advancedsearch.php", params={
            "q": terms, "rows": query.limit, "output": "json",
            "fl[]": ["identifier", "title", "mediatype", "licenseurl", "year", "format"],
        }).json()
        out = []
        for doc in (data.get("response", {}).get("docs", []) or []):
            ident = doc.get("identifier", "")
            if not ident:
                continue
            fmt = doc.get("format")
            out.append(DiscoveredEvidence(
                id=f"{self.name}:{slugify(ident)}", need_id=query.need_id,
                target=query.target, category=query.category, title=doc.get("title", ""),
                url=f"https://archive.org/details/{ident}", provider=self.name,
                media_type=doc.get("mediatype", UNKNOWN) or UNKNOWN,
                license=doc.get("licenseurl", "") or UNKNOWN,
                fmt=", ".join(fmt) if isinstance(fmt, list) else (fmt or UNKNOWN),
                date=str(doc.get("year", "")) or UNKNOWN,
                reliability=self._reliability, availability=Availability.AVAILABLE,
                priority=query.priority, query_used=[terms],
                extra={"identifier": ident,
                       "metadata_url": f"https://archive.org/metadata/{ident}"},
            ))
        return out


class OpenStreetMapProvider(RealDiscoveryProvider):
    name = "openstreetmap"
    _media = (C.MAP,)
    _licenses = ("ODbL",)
    _priority = 10
    _cost = "free"
    _rate_limits = {"requests_per_minute": 60}
    _capabilities = ("search", "metadata", "download")
    _reliability = "HIGH"

    def _search(self, query):
        terms = query.target if query.target and query.target != "case" else _terms(query)
        if not terms:
            return []
        data = self._http.get("https://nominatim.openstreetmap.org/search", params={
            "q": terms, "format": "jsonv2", "limit": query.limit, "addressdetails": 0,
        }).json()
        out = []
        for place in (data or []):
            osm_type = place.get("osm_type", "")
            osm_id = place.get("osm_id", "")
            out.append(DiscoveredEvidence(
                id=f"{self.name}:{osm_type}{osm_id}", need_id=query.need_id,
                target=query.target, category=query.category,
                title=place.get("display_name", ""),
                url=f"https://www.openstreetmap.org/{osm_type}/{osm_id}", provider=self.name,
                media_type=C.MAP, license="ODbL",
                reliability=self._reliability, availability=Availability.AVAILABLE,
                priority=query.priority, query_used=[terms],
                extra={"lat": place.get("lat"), "lon": place.get("lon"),
                       "bounding_box": place.get("boundingbox"),
                       "type": place.get("type"), "category": place.get("category"),
                       "display_name": place.get("display_name", "")},
            ))
        return out


class WikidataProvider(RealDiscoveryProvider):
    name = "wikidata"
    _media = (C.PUBLIC_RECORD, C.TIMELINE)
    _licenses = ("CC0",)
    _priority = 18
    _cost = "free"
    _capabilities = ("search", "metadata")
    _reliability = "HIGH"

    def _search(self, query):
        terms = _terms(query) or query.target
        if not terms:
            return []
        lang = query.language or "en"
        data = self._http.get("https://www.wikidata.org/w/api.php", params={
            "action": "wbsearchentities", "search": terms, "language": lang,
            "uselang": lang, "format": "json", "limit": query.limit,
        }).json()
        out = []
        for ent in (data.get("search", []) or []):
            qid = ent.get("id", "")
            if not qid:
                continue
            out.append(DiscoveredEvidence(
                id=f"{self.name}:{qid}", need_id=query.need_id, target=query.target,
                category=query.category, title=ent.get("label", ""),
                url=ent.get("concepturi") or f"https://www.wikidata.org/wiki/{qid}",
                provider=self.name, media_type="entity", license="CC0",
                language=lang, reliability=self._reliability,
                availability=Availability.AVAILABLE, priority=query.priority,
                query_used=[terms],
                extra={"qid": qid, "description": ent.get("description", ""),
                       "aliases": ent.get("aliases", []),
                       "entity_data": f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"},
            ))
        return out


class WikipediaProvider(RealDiscoveryProvider):
    name = "wikipedia"
    _media = (C.TIMELINE, C.NEWS, C.PUBLIC_RECORD)
    _licenses = ("CC-BY-SA",)
    _priority = 22
    _cost = "free"
    _capabilities = ("search", "metadata")
    _reliability = "MEDIUM"

    def _search(self, query):
        terms = _terms(query) or query.target
        if not terms:
            return []
        lang = query.language or "en"
        data = self._http.get(f"https://{lang}.wikipedia.org/w/api.php", params={
            "action": "query", "list": "search", "srsearch": terms,
            "srlimit": query.limit, "format": "json",
        }).json()
        out = []
        for hit in (data.get("query", {}).get("search", []) or []):
            pageid = hit.get("pageid", "")
            if not pageid:
                continue
            out.append(DiscoveredEvidence(
                id=f"{self.name}:{pageid}", need_id=query.need_id, target=query.target,
                category=query.category, title=hit.get("title", ""),
                url=f"https://{lang}.wikipedia.org/?curid={pageid}", provider=self.name,
                media_type="reference", license="CC-BY-SA", language=lang,
                reliability=self._reliability, availability=Availability.AVAILABLE,
                priority=query.priority, query_used=[terms],
                extra={"pageid": pageid, "snippet": _clean(hit.get("snippet", "")),
                       "summary_api": f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
                                      f"{hit.get('title', '').replace(' ', '_')}"},
            ))
        return out


def real_providers(http=None, cache=None) -> list[RealDiscoveryProvider]:
    return [
        WikimediaCommonsProvider(http, cache), InternetArchiveProvider(http, cache),
        OpenStreetMapProvider(http, cache), WikidataProvider(http, cache),
        WikipediaProvider(http, cache),
    ]
