"""GraphBuilder — fusiona EvidenceResult[] en un EvidenceGraph (ERE).

Determinista y reproducible (misma entrada → mismo grafo) y conserva la
trazabilidad:
- entidades: se agrupan por ``id``; alias y referencias se unen; los atributos
  acumulan TODOS los claims (cada uno con proveedor + confianza),
- conflictos: si un atributo de una entidad tiene >1 valor distinto, se registra en
  ``conflicts`` con todos los candidatos (no se decide),
- eventos/artículos/imágenes/vídeos/documentos: deduplicados por ``id``,
- relaciones: deduplicadas; ``has_reference`` puebla además ``entity.references``,
- ``providers_used``: proveedores disponibles que aportaron; ``sources`` deduplicadas.

No inventa nada: solo combina lo que aportan los proveedores.
"""

from dataclasses import replace

from app.ere.models import (
    Entity,
    EvidenceGraph,
    ProjectQuery,
    SourceRef,
)
from app.ere.providers.base import EvidenceResult


def _dedupe(seq: list) -> list:
    out: list = []
    for item in seq:
        if item not in out:
            out.append(item)
    return out


def _occurrence_confidence(entity: Entity) -> float:
    return max((s.confidence for s in entity.sources), default=0.0)


def entity_conflicts(entities) -> list[dict]:
    """Conflictos por atributo: si un campo tiene >1 valor distinto, se conservan
    todos los candidatos (no se decide). Determinista (ordenado por entidad/campo)."""
    conflicts: list[dict] = []
    for entity in entities:
        for fname, claims in entity.attributes.items():
            distinct: list = []
            for claim in claims:
                if claim.value not in [d["value"] for d in distinct]:
                    distinct.append(
                        {"value": claim.value, "provider": claim.provider,
                         "confidence": claim.confidence}
                    )
            if len(distinct) > 1:
                conflicts.append(
                    {"entity_id": entity.id, "field": fname, "candidates": distinct}
                )
    conflicts.sort(key=lambda c: (c["entity_id"], c["field"]))
    return conflicts


class GraphBuilder:
    def build(
        self, query: ProjectQuery, results: list[EvidenceResult]
    ) -> EvidenceGraph:
        available = [r for r in results if r.available]

        entities = self._merge_entities(available)
        conflicts = self._entity_conflicts(entities)

        graph = EvidenceGraph(
            project=query,
            entities=sorted(entities.values(), key=lambda e: e.id),
            events=_dedupe([e for r in available for e in r.events]),
            articles=_dedupe([a for r in available for a in r.articles]),
            images=_dedupe([i for r in available for i in r.images]),
            videos=_dedupe([v for r in available for v in r.videos]),
            court_documents=_dedupe([c for r in available for c in r.court_documents]),
            relationships=_dedupe([rel for r in available for rel in r.relationships]),
            conflicts=conflicts,
            providers_used=_dedupe([r.provider for r in available]),
            sources=_dedupe([s for r in available for s in r.sources]),
        )

        # Orden estable de los nodos y relaciones.
        graph.events.sort(key=lambda e: e.id)
        graph.articles.sort(key=lambda a: a.id)
        graph.images.sort(key=lambda i: i.id)
        graph.videos.sort(key=lambda v: v.id)
        graph.court_documents.sort(key=lambda c: c.id)
        graph.relationships.sort(key=lambda r: (r.source_id, r.relation, r.target_id))
        graph.sources.sort(key=lambda s: (s.provider, s.url, s.source))

        self._link_references(graph)
        return graph

    def _merge_entities(self, results: list[EvidenceResult]) -> dict[str, Entity]:
        merged: dict[str, Entity] = {}
        name_conf: dict[str, float] = {}
        for result in results:
            for entity in result.entities:
                conf = _occurrence_confidence(entity)
                existing = merged.get(entity.id)
                if existing is None:
                    # copia (claims por campo deduplicados más adelante)
                    merged[entity.id] = replace(
                        entity,
                        aliases=list(entity.aliases),
                        attributes={k: list(v) for k, v in entity.attributes.items()},
                        references=list(entity.references),
                        sources=list(entity.sources),
                        metadata=dict(entity.metadata),
                    )
                    name_conf[entity.id] = conf if entity.canonical_name else -1.0
                    continue
                # canonical_name: gana el no vacío de mayor confianza (estable)
                if entity.canonical_name and conf > name_conf.get(entity.id, -1.0):
                    existing.canonical_name = entity.canonical_name
                    name_conf[entity.id] = conf
                if existing.type == "character" and entity.type != "character":
                    existing.type = entity.type  # tipos más específicos no se pierden
                existing.aliases = _dedupe(existing.aliases + list(entity.aliases))
                existing.references = _dedupe(existing.references + list(entity.references))
                existing.sources = _dedupe(existing.sources + list(entity.sources))
                for fname, claims in entity.attributes.items():
                    existing.attributes.setdefault(fname, [])
                    existing.attributes[fname] = _dedupe(existing.attributes[fname] + list(claims))
                for key, value in entity.metadata.items():
                    existing.metadata.setdefault(key, value)

        # claims ordenados de forma estable (mayor confianza primero)
        for entity in merged.values():
            entity.aliases = _dedupe(entity.aliases)
            for fname in entity.attributes:
                entity.attributes[fname] = sorted(
                    entity.attributes[fname],
                    key=lambda c: (-c.confidence, c.provider, str(c.value)),
                )
        return merged

    @staticmethod
    def _entity_conflicts(entities: dict[str, Entity]) -> list[dict]:
        return entity_conflicts(entities.values())

    @staticmethod
    def _link_references(graph: EvidenceGraph) -> None:
        by_id = {e.id: e for e in graph.entities}
        for rel in graph.relationships:
            if rel.relation == "has_reference" and rel.source_id in by_id:
                entity = by_id[rel.source_id]
                if rel.target_id not in entity.references:
                    entity.references.append(rel.target_id)
        for entity in graph.entities:
            entity.references.sort()
