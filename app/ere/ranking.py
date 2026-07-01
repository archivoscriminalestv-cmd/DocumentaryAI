"""Evidence Ranking Engine (ERE-002) — puntúa cada evidencia frente al contexto.

No se acepta automáticamente el primer resultado: cada nodo (entidad, artículo,
imagen, vídeo) recibe un ``score`` en [0, 1] combinando **señales genéricas** con
pesos configurables. NO hay reglas específicas por género (nada de ``if true_crime``):
la desambiguación emerge de la puntuación.

Señales de contexto: nombre, alias, persona, ubicación, fecha, palabras clave.
Señales de calidad: confianza, proveedor, idioma.
    score = contexto * (0.5 + 0.5 * calidad)
Así, una evidencia sin apenas contexto (p.ej. el cóctel "Coquito": solo coincide el
alias) obtiene un score bajo aunque su proveedor/confianza sean altos.

Determinista y sin red.
"""

import re
import unicodedata
from dataclasses import dataclass, field, replace

from app.ere.project_knowledge import ProjectKnowledge
from app.ere.providers.base import EvidenceResult

_TOKEN_RE = re.compile(r"[a-z0-9]+")

DEFAULT_PROVIDER_PRIORS = {
    "wikipedia": 0.7, "wikidata": 0.7, "commons": 0.6,
    "news": 0.8, "youtube": 0.7, "google-images": 0.6, "archive": 0.7,
    "court-documents": 0.8, "seed": 0.7, "mock-evidence": 0.3,
}


@dataclass
class RankingWeights:
    # contexto
    name: float = 3.0
    alias: float = 1.0
    person: float = 1.5
    location: float = 1.5
    date: float = 1.5
    keyword: float = 2.0
    # calidad
    confidence: float = 1.0
    provider: float = 1.0
    language: float = 0.5
    # extensible: añadir nuevas señales = añadir un peso aquí + computarlo en el engine.


@dataclass
class RankedNode:
    kind: str          # entity | article | image | video
    node_id: str
    score: float
    accepted: bool
    signals: dict = field(default_factory=dict)


def _tokens(text: str) -> set[str]:
    nfkd = unicodedata.normalize("NFKD", text or "")
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii").lower()
    return set(_TOKEN_RE.findall(ascii_only))


def _term_match(term: str, tokens: set[str]) -> float:
    """Fracción de los tokens del término presentes en el texto (0..1)."""
    tterms = _tokens(term)
    if not tterms:
        return 0.0
    return sum(1 for t in tterms if t in tokens) / len(tterms)


def _max_match(terms: list[str], tokens: set[str]) -> float:
    return max((_term_match(t, tokens) for t in terms), default=0.0)


def _year(date: str) -> str:
    digits = "".join(ch for ch in (date or "") if ch.isdigit())
    return digits[:4] if len(digits) >= 4 else ""


def _date_match(date: str, tokens: set[str]) -> float:
    year = _year(date)
    return 1.0 if year and year in tokens else 0.0


class RankingEngine:
    def __init__(
        self,
        weights: RankingWeights | None = None,
        provider_priors: dict[str, float] | None = None,
        default_provider_prior: float = 0.5,
    ) -> None:
        self.weights = weights or RankingWeights()
        self.provider_priors = provider_priors or dict(DEFAULT_PROVIDER_PRIORS)
        self.default_provider_prior = default_provider_prior

    # --- score de un texto/candidato genérico --------------------------------
    def score_text(
        self, text: str, knowledge: ProjectKnowledge, *,
        provider: str = "", confidence: float = 0.5, language: str = "",
    ) -> tuple[float, dict]:
        tokens = _tokens(text)
        w = self.weights

        s_name = _term_match(knowledge.subject_name(), tokens)
        s_alias = _max_match(knowledge.aliases + ([knowledge.title] if knowledge.title else []), tokens)
        s_person = _max_match(knowledge.known_people, tokens)
        s_loc = _max_match(knowledge.locations, tokens)
        s_date = max((_date_match(d, tokens) for d in knowledge.dates), default=0.0)
        s_kw = (
            sum(1 for k in knowledge.keywords if _term_match(k, tokens) >= 0.5)
            / len(knowledge.keywords)
        ) if knowledge.keywords else 0.0

        context_terms = [
            (w.name, s_name), (w.alias, s_alias), (w.person, s_person),
            (w.location, s_loc), (w.date, s_date), (w.keyword, s_kw),
        ]
        context_total = sum(weight for weight, _ in context_terms) or 1.0
        context = sum(weight * signal for weight, signal in context_terms) / context_total

        prov = self.provider_priors.get(provider, self.default_provider_prior)
        if knowledge.language and language:
            s_lang = 1.0 if language == knowledge.language else 0.3
        else:
            s_lang = 0.6  # neutro cuando no se conoce el idioma del candidato
        qual_terms = [(w.confidence, confidence), (w.provider, prov), (w.language, s_lang)]
        qual_total = sum(weight for weight, _ in qual_terms) or 1.0
        quality = sum(weight * signal for weight, signal in qual_terms) / qual_total

        score = context * (0.5 + 0.5 * quality)
        signals = {
            "name": round(s_name, 3), "alias": round(s_alias, 3),
            "person": round(s_person, 3), "location": round(s_loc, 3),
            "date": round(s_date, 3), "keyword": round(s_kw, 3),
            "context": round(context, 3), "quality": round(quality, 3),
        }
        return round(score, 4), signals

    # --- texto representativo por tipo de nodo --------------------------------
    @staticmethod
    def _entity_text(entity) -> str:
        parts = [entity.canonical_name, *entity.aliases]
        for claims in entity.attributes.values():
            parts.extend(str(c.value) for c in claims)
        return " ".join(parts)

    @staticmethod
    def _entity_conf(entity) -> float:
        return max((s.confidence for s in entity.sources), default=0.0)

    # --- ranking de un EvidenceResult completo --------------------------------
    def rank_result(
        self, result: EvidenceResult, knowledge: ProjectKnowledge, min_score: float
    ) -> tuple[EvidenceResult, list[RankedNode]]:
        ranked: list[RankedNode] = []
        dropped_ids: set[str] = set()

        kept_entities = []
        for entity in result.entities:
            score, sig = self.score_text(
                self._entity_text(entity), knowledge,
                provider=result.provider, confidence=self._entity_conf(entity),
            )
            entity.metadata = {**entity.metadata, "relevance_score": score}
            accepted = score >= min_score
            ranked.append(RankedNode("entity", entity.id, score, accepted, sig))
            (kept_entities.append(entity) if accepted else dropped_ids.add(entity.id))

        kept_articles = []
        for art in result.articles:
            score, sig = self.score_text(
                f"{art.headline} {art.snippet} {art.medium}", knowledge,
                provider=result.provider, confidence=art.source.confidence,
            )
            accepted = score >= min_score
            ranked.append(RankedNode("article", art.id, score, accepted, sig))
            (kept_articles.append(art) if accepted else dropped_ids.add(art.id))

        kept_images = []
        for img in result.images:
            score, sig = self.score_text(
                f"{img.caption} {img.author}", knowledge,
                provider=result.provider, confidence=0.5,
            )
            img.relevance = score
            accepted = score >= min_score
            ranked.append(RankedNode("image", img.id, score, accepted, sig))
            (kept_images.append(img) if accepted else dropped_ids.add(img.id))

        kept_videos = []
        for vid in result.videos:
            score, sig = self.score_text(
                f"{vid.title} {vid.channel}", knowledge,
                provider=result.provider, confidence=0.5,
            )
            accepted = score >= min_score
            ranked.append(RankedNode("video", vid.id, score, accepted, sig))
            (kept_videos.append(vid) if accepted else dropped_ids.add(vid.id))

        # relaciones que apuntan a nodos descartados se eliminan (sin colgar aristas)
        kept_rels = [
            r for r in result.relationships
            if r.source_id not in dropped_ids and r.target_id not in dropped_ids
        ]

        new_result = replace(
            result, entities=kept_entities, articles=kept_articles,
            images=kept_images, videos=kept_videos, relationships=kept_rels,
        )
        return new_result, ranked
