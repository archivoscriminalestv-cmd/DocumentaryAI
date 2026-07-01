"""Tests deterministas de ERE-002: ProjectKnowledge, Query Builder, Ranking, Entity
Resolution y desambiguación por puntuación. Sin red.
"""

import json
import os
import tempfile

from app.ere.entity_resolution import EntityResolver
from app.ere.models import (
    Claim,
    Entity,
    EvidenceGraph,
    ImageAsset,
    ProjectQuery,
    Relationship,
    SourceRef,
)
from app.ere.orchestrator import EvidenceOrchestrator
from app.ere.project_knowledge import ProjectKnowledge
from app.ere.providers.base import EvidenceProvider, EvidenceResult
from app.ere.query_builder import QueryBuilder, EvidenceQuery, AliasStrategy
from app.ere.ranking import RankingEngine, RankingWeights


def coquito_knowledge() -> ProjectKnowledge:
    return ProjectKnowledge(
        title="Coquito",
        canonical_name="Jonathan Burgos",
        aliases=["Coquito"],
        locations=["Trinitat Vella", "Barcelona"],
        dates=["2021-01-04"],
        country="España",
        language="es",
        genre="true_crime",
        keywords=["asesinato", "Mossos", "Vall d'Hebron"],
    )


# --- ProjectKnowledge -------------------------------------------------------
def test_project_knowledge_roundtrip_and_to_query():
    k = coquito_knowledge()
    assert ProjectKnowledge.from_dict(k.to_dict()) == k
    q = k.to_query()
    assert q.name == "Jonathan Burgos"          # el sujeto es la persona real
    assert "Coquito" in q.aliases               # el título pasa a alias
    assert q.subject_id() == "character:jonathan_burgos"
    assert q.date == "2021-01-04"


# --- Query Builder ----------------------------------------------------------
def test_query_builder_generates_enriched_deterministic_queries():
    qb = QueryBuilder()
    q1 = qb.build(coquito_knowledge())
    q2 = qb.build(coquito_knowledge())
    texts1 = [q.text for q in q1]
    assert texts1 == [q.text for q in q2]                 # determinista
    assert len(texts1) == len(set(texts1))                # sin duplicados
    # ordenado por peso descendente
    assert all(q1[i].weight >= q1[i + 1].weight for i in range(len(q1) - 1))
    # contexto documental presente
    joined = " || ".join(texts1)
    assert "Jonathan Burgos Barcelona" in joined
    assert "Jonathan Burgos Trinitat Vella" in joined
    assert any("Mossos" in t for t in texts1)
    assert any("2021" in t for t in texts1)
    # nunca una única búsqueda
    assert len(texts1) >= 8


def test_query_builder_strategies_are_pluggable():
    qb = QueryBuilder(strategies=[AliasStrategy()])
    out = qb.build(coquito_knowledge())
    assert out and all(isinstance(q, EvidenceQuery) for q in out)
    assert all(q.strategy == "alias" for q in out)


# --- Ranking ----------------------------------------------------------------
def test_ranking_prioritizes_context_over_provider_quality():
    k = coquito_knowledge()
    engine = RankingEngine()
    # cóctel: solo coincide el alias, proveedor/confianza altos
    cocktail, _ = engine.score_text(
        "Coquito is a traditional Christmas drink from Puerto Rico",
        k, provider="wikipedia", confidence=0.9,
    )
    # caso real: nombre + ubicación + fecha + keyword
    real, _ = engine.score_text(
        "Jonathan Burgos asesinato en Trinitat Vella Barcelona 2021 Mossos",
        k, provider="news", confidence=0.8,
    )
    assert real > 0.5 > cocktail
    assert cocktail < 0.15           # por debajo del umbral típico
    # determinista
    assert engine.score_text("Jonathan Burgos Barcelona 2021", k)[0] == \
        engine.score_text("Jonathan Burgos Barcelona 2021", k)[0]


def test_ranking_weights_are_configurable():
    k = coquito_knowledge()
    text = "Jonathan Burgos Barcelona"
    base = RankingEngine().score_text(text, k)[0]
    boosted = RankingEngine(weights=RankingWeights(location=10.0)).score_text(text, k)[0]
    assert boosted != base


def test_ranking_filters_irrelevant_nodes():
    k = coquito_knowledge()
    res = EvidenceResult(
        "news", True,
        entities=[
            Entity(id="character:jonathan_burgos", canonical_name="Jonathan Burgos",
                   attributes={"event": [Claim("event", "asesinato Trinitat Vella Barcelona 2021",
                                               "news", 0.8, "u")]},
                   sources=[SourceRef(provider="news", confidence=0.8)]),
            Entity(id="character:coquito_drink", canonical_name="Coquito",
                   attributes={"desc": [Claim("desc", "Christmas drink Puerto Rico",
                                              "wikipedia", 0.9, "u2")]},
                   sources=[SourceRef(provider="wikipedia", confidence=0.9)]),
        ],
    )
    filtered, ranked = RankingEngine().rank_result(res, k, min_score=0.15)
    ids = {e.id for e in filtered.entities}
    assert "character:jonathan_burgos" in ids
    assert "character:coquito_drink" not in ids          # descartado por score
    assert any(n.node_id == "character:jonathan_burgos" and n.accepted for n in ranked)


# --- Entity Resolution ------------------------------------------------------
def test_entity_resolution_groups_alias_into_subject():
    k = coquito_knowledge()
    graph = EvidenceGraph(project=k.to_query())
    graph.entities = [
        Entity(id="character:jonathan_burgos", canonical_name="Jonathan Burgos",
               attributes={"nationality": [Claim("nationality", "España", "news", 0.8, "u")]},
               sources=[SourceRef(provider="news", confidence=0.8)]),
        Entity(id="character:coquito", canonical_name="Coquito",
               references=["image:1"],
               sources=[SourceRef(provider="seed", confidence=0.6)]),
    ]
    graph.images = [ImageAsset(id="image:1", provider="seed")]
    graph.relationships = [Relationship("character:coquito", "has_reference", "image:1")]

    resolved = EntityResolver().resolve(graph, k)
    # se agrupan en una sola entidad (no se crean nuevas)
    assert len(resolved.entities) == 1
    subject = resolved.entities[0]
    assert subject.id == "character:jonathan_burgos"
    assert "Coquito" in subject.aliases
    assert "image:1" in subject.references
    # la relación se reapunta al superviviente
    assert resolved.relationships[0].source_id == "character:jonathan_burgos"


def test_entity_resolution_keeps_distinct_entities_separate():
    graph = EvidenceGraph()
    graph.entities = [
        Entity(id="character:a", canonical_name="Persona A",
               sources=[SourceRef(provider="news", confidence=0.8)]),
        Entity(id="location:trinitat_vella", type="location", canonical_name="Trinitat Vella",
               sources=[SourceRef(provider="news", confidence=0.7)]),
    ]
    resolved = EntityResolver().resolve(graph, ProjectKnowledge(canonical_name="Persona A"))
    assert len(resolved.entities) == 2


# --- Pipeline completo: desambiguación por puntuación -----------------------
class _CaseProvider(EvidenceProvider):
    """Proveedor falso: devuelve el caso real + un falso positivo (cóctel)."""
    name = "news"

    def research(self, query: ProjectQuery) -> EvidenceResult:
        return EvidenceResult(
            self.name, True,
            entities=[
                Entity(id=query.subject_id(), canonical_name="Jonathan Burgos",
                       attributes={"event": [Claim("event",
                                   "asesinato Trinitat Vella Barcelona 2021 Mossos Vall Hebron",
                                   self.name, 0.85, "u")]},
                       sources=[SourceRef(provider=self.name, confidence=0.85)]),
            ],
        )


class _CocktailProvider(EvidenceProvider):
    name = "wikipedia"

    def research(self, query: ProjectQuery) -> EvidenceResult:
        return EvidenceResult(
            self.name, True,
            entities=[
                Entity(id="character:coquito_drink", canonical_name="Coquito",
                       attributes={"desc": [Claim("desc",
                                   "traditional Christmas drink from Puerto Rico coconut",
                                   self.name, 0.9, "u2")]},
                       sources=[SourceRef(provider=self.name, confidence=0.9)]),
            ],
        )


def test_pipeline_disambiguates_by_score_not_rules():
    k = coquito_knowledge()
    orch = EvidenceOrchestrator([_CaseProvider(), _CocktailProvider()])
    g1, manifest = orch.research_project(k, min_score=0.15)
    g2, _ = orch.research_project(k, min_score=0.15)
    assert g1 == g2                                          # reproducible

    ids = {e.id for e in g1.entities}
    assert "character:jonathan_burgos" in ids               # caso real aceptado
    assert "character:coquito_drink" not in ids             # cóctel descartado
    # trazabilidad en el manifest
    assert manifest["query_builder"]["total"] >= 8
    assert manifest["ranking"]["rejected"] >= 1
    assert any(n["id"] == "character:coquito_drink"
               for n in manifest["ranking"]["rejected_nodes"])
    assert "project_knowledge" in manifest


def test_pipeline_cli_with_knowledge_file():
    import app.cli.research_evidence as cli

    with tempfile.TemporaryDirectory() as tmp:
        kpath = os.path.join(tmp, "project_knowledge.json")
        coquito_knowledge().save(kpath)
        cli.main(["--knowledge", kpath, "--output-dir", tmp],
                 providers=[_CaseProvider(), _CocktailProvider()])
        graph_path = os.path.join(tmp, "jonathan_burgos", "evidence_graph.json")
        data = json.load(open(graph_path, encoding="utf-8"))
        ids = {e["id"] for e in data["entities"]}
        assert "character:jonathan_burgos" in ids
        assert "character:coquito_drink" not in ids


def test_project_knowledge_cli_writes_file():
    import app.cli.project_knowledge as cli

    with tempfile.TemporaryDirectory() as tmp:
        cli.main(["--title", "Coquito", "--canonical-name", "Jonathan Burgos",
                  "--alias", "Coquito", "--location", "Barcelona", "--date", "2021-01-04",
                  "--genre", "true_crime", "--keyword", "asesinato", "--output-dir", tmp])
        path = os.path.join(tmp, "project_knowledge.json")
        data = json.load(open(path, encoding="utf-8"))
        assert data["canonical_name"] == "Jonathan Burgos"
        assert data["title"] == "Coquito"
