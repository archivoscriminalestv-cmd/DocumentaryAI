"""WikidataProvider real — datos estructurados de Wikidata.

Resuelve el QID del personaje (vía pageprops de Wikipedia) y extrae datos
estructurados verificables: fechas de nacimiento/defunción (P569/P570),
ocupación (P106) y nacionalidad (P27). Las propiedades que son entidades se
resuelven a etiquetas legibles con una llamada ``wbgetentities``.

NO interpreta ni infiere: si un dato no existe, se omite. Integración HTTP
inyectable para tests.
"""

from app.cre.http import HttpClient, JsonHttpClient
from app.cre.models import CharacterRequest
from app.cre.providers.base import ResearchProvider, ResearchResult

CONFIDENCE = 0.9


class WikidataProvider(ResearchProvider):
    name = "wikidata"

    def __init__(self, client: HttpClient | None = None, lang: str = "en") -> None:
        self._client = client or JsonHttpClient()
        self._lang = lang

    def research(self, request: CharacterRequest) -> ResearchResult:
        try:
            qid = self._resolve_qid(request.name)
            if not qid:
                return ResearchResult(self.name, False, error="sin entidad Wikidata")
            entity = self._client.get_json(
                f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
            )
            claims = entity["entities"][qid]["claims"]
        except Exception as exc:
            return ResearchResult(self.name, False, error=str(exc)[:160])

        identity: dict[str, str] = {}
        birth = _first_date(claims, "P569")
        death = _first_date(claims, "P570")
        if birth:
            identity["birth_date"] = birth
        if death:
            identity["death_date"] = death

        occ_ids = _entity_ids(claims, "P106")
        nat_ids = _entity_ids(claims, "P27")
        labels = self._labels(occ_ids[:3] + nat_ids[:2])
        if occ_ids:
            identity["occupation"] = ", ".join(labels.get(i, i) for i in occ_ids[:3])
        if nat_ids:
            identity["nationality"] = ", ".join(labels.get(i, i) for i in nat_ids[:2])

        if not identity:
            return ResearchResult(self.name, False, error="entidad sin datos relevantes")

        return ResearchResult(
            provider=self.name,
            available=True,
            data={"identity": identity},
            sources=[f"https://www.wikidata.org/wiki/{qid}"],
            confidence=CONFIDENCE,
            notes="Datos estructurados verificables de Wikidata.",
        )

    def _resolve_qid(self, name: str) -> str:
        api = f"https://{self._lang}.wikipedia.org/w/api.php"
        data = self._client.get_json(
            api,
            {
                "action": "query",
                "prop": "pageprops",
                "ppprop": "wikibase_item",
                "redirects": 1,
                "titles": name,
                "format": "json",
            },
        )
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            qid = page.get("pageprops", {}).get("wikibase_item", "")
            if qid:
                return qid
        return ""

    def _labels(self, ids: list[str]) -> dict[str, str]:
        if not ids:
            return {}
        data = self._client.get_json(
            "https://www.wikidata.org/w/api.php",
            {
                "action": "wbgetentities",
                "ids": "|".join(ids),
                "props": "labels",
                "languages": self._lang,
                "format": "json",
            },
        )
        out: dict[str, str] = {}
        for qid, ent in data.get("entities", {}).items():
            label = ent.get("labels", {}).get(self._lang, {}).get("value", "")
            if label:
                out[qid] = label
        return out


def _first_date(claims: dict, prop: str) -> str:
    """Extrae 'YYYY-MM-DD' (o 'YYYY') del primer claim temporal de ``prop``."""
    for claim in claims.get(prop, []):
        time_value = (
            claim.get("mainsnak", {})
            .get("datavalue", {})
            .get("value", {})
            .get("time", "")
        )
        if time_value:
            # formato Wikidata: "+1856-07-10T00:00:00Z"
            iso = time_value.lstrip("+").split("T", 1)[0]
            return _trim_unknown(iso)
    return ""


def _trim_unknown(iso: str) -> str:
    """Recorta meses/días desconocidos ('1856-00-00' -> '1856')."""
    parts = iso.split("-")
    if len(parts) == 3 and parts[1] == "00":
        return parts[0]
    if len(parts) == 3 and parts[2] == "00":
        return f"{parts[0]}-{parts[1]}"
    return iso


def _entity_ids(claims: dict, prop: str) -> list[str]:
    ids: list[str] = []
    for claim in claims.get(prop, []):
        qid = (
            claim.get("mainsnak", {})
            .get("datavalue", {})
            .get("value", {})
            .get("id", "")
        )
        if qid and qid not in ids:
            ids.append(qid)
    return ids
