"""WikidataProvider (ERE) — atributos estructurados verificables del sujeto.

Resuelve el QID (vía pageprops de Wikipedia) y extrae fechas (P569/P570),
ocupación (P106) y nacionalidad (P27) como claims atribuidos sobre la Entity
'character' del sujeto. No interpreta ni infiere.
"""

from app.ere.http import HttpClient, JsonHttpClient
from app.ere.models import Claim, Entity, ProjectQuery, SourceRef
from app.ere.providers.base import EvidenceProvider, EvidenceResult

CONFIDENCE = 0.9


class WikidataProvider(EvidenceProvider):
    name = "wikidata"

    def __init__(self, client: HttpClient | None = None, lang: str = "en") -> None:
        self._client = client or JsonHttpClient()
        self._lang = lang

    def research(self, query: ProjectQuery) -> EvidenceResult:
        try:
            qid = self._resolve_qid(query.name)
            if not qid:
                return EvidenceResult(self.name, False, error="sin entidad Wikidata")
            entity_json = self._client.get_json(
                f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
            )
            claims = entity_json["entities"][qid]["claims"]
        except Exception as exc:
            return EvidenceResult(self.name, False, error=str(exc)[:160])

        url = f"https://www.wikidata.org/wiki/{qid}"
        attributes: dict[str, list[Claim]] = {}

        def _add(field_name: str, value: str) -> None:
            if value:
                attributes[field_name] = [Claim(field_name, value, self.name, CONFIDENCE, url)]

        _add("birth_date", _first_date(claims, "P569"))
        _add("death_date", _first_date(claims, "P570"))
        occ_ids = _entity_ids(claims, "P106")
        nat_ids = _entity_ids(claims, "P27")
        labels = self._labels(occ_ids[:3] + nat_ids[:2])
        if occ_ids:
            _add("occupation", ", ".join(labels.get(i, i) for i in occ_ids[:3]))
        if nat_ids:
            _add("nationality", ", ".join(labels.get(i, i) for i in nat_ids[:2]))

        if not attributes:
            return EvidenceResult(self.name, False, error="entidad sin datos relevantes")

        source = SourceRef(provider=self.name, url=url, source="Wikidata",
                           confidence=CONFIDENCE, license="CC0")
        entity = Entity(
            id=query.subject_id(), type="character", canonical_name=query.name,
            aliases=list(query.aliases), attributes=attributes, sources=[source],
        )
        return EvidenceResult(
            self.name, True, entities=[entity], sources=[source],
            confidence=CONFIDENCE, notes="Datos estructurados verificables.",
        )

    def _resolve_qid(self, name: str) -> str:
        data = self._client.get_json(
            f"https://{self._lang}.wikipedia.org/w/api.php",
            {"action": "query", "prop": "pageprops", "ppprop": "wikibase_item",
             "redirects": 1, "titles": name, "format": "json"},
        )
        for page in data.get("query", {}).get("pages", {}).values():
            qid = page.get("pageprops", {}).get("wikibase_item", "")
            if qid:
                return qid
        return ""

    def _labels(self, ids: list[str]) -> dict[str, str]:
        if not ids:
            return {}
        data = self._client.get_json(
            "https://www.wikidata.org/w/api.php",
            {"action": "wbgetentities", "ids": "|".join(ids), "props": "labels",
             "languages": self._lang, "format": "json"},
        )
        out: dict[str, str] = {}
        for qid, ent in data.get("entities", {}).items():
            label = ent.get("labels", {}).get(self._lang, {}).get("value", "")
            if label:
                out[qid] = label
        return out


def _first_date(claims: dict, prop: str) -> str:
    for claim in claims.get(prop, []):
        time_value = (
            claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("time", "")
        )
        if time_value:
            iso = time_value.lstrip("+").split("T", 1)[0]
            parts = iso.split("-")
            if len(parts) == 3 and parts[1] == "00":
                return parts[0]
            if len(parts) == 3 and parts[2] == "00":
                return f"{parts[0]}-{parts[1]}"
            return iso
    return ""


def _entity_ids(claims: dict, prop: str) -> list[str]:
    ids: list[str] = []
    for claim in claims.get(prop, []):
        qid = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id", "")
        if qid and qid not in ids:
            ids.append(qid)
    return ids
