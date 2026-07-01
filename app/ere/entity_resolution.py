"""Entity Resolution Engine (ERE-002) — resuelve alias, agrupa y deduplica entidades.

Agrupa entidades que se refieren al mismo sujeto real (mismo nombre normalizado, o
relación de alias con el sujeto del proyecto) en UNA sola, conservando alias,
atributos, referencias y fuentes. NO crea entidades nuevas: solo agrupa las
existentes. Tras agrupar, reapunta las relaciones a la entidad superviviente y
recalcula los conflictos.

Determinista y sin red. La desambiguación de relevancia la hace el Ranking; aquí solo
se unifican identidades equivalentes.
"""

from dataclasses import replace

from app.ere.graph_builder import entity_conflicts
from app.ere.models import Entity, EvidenceGraph, slugify
from app.ere.project_knowledge import ProjectKnowledge


def _dedupe(seq: list) -> list:
    out: list = []
    for item in seq:
        if item not in out:
            out.append(item)
    return out


def _names(entity: Entity) -> set[str]:
    names = {slugify(entity.canonical_name)} if entity.canonical_name else set()
    names |= {slugify(a) for a in entity.aliases if a}
    return {n for n in names if n}


class EntityResolver:
    def resolve(
        self, graph: EvidenceGraph, knowledge: ProjectKnowledge | None = None
    ) -> EvidenceGraph:
        if not graph.entities:
            return graph

        subject_terms = self._subject_terms(knowledge)
        subject_key = slugify(knowledge.subject_name()) if knowledge else ""

        # 1) asignar a cada entidad una clave de grupo.
        group_of: dict[str, str] = {}
        for entity in graph.entities:
            names = _names(entity)
            if subject_terms and (names & subject_terms):
                group_of[entity.id] = f"subject::{subject_key}"
            else:
                group_of[entity.id] = "name::" + (slugify(entity.canonical_name) or entity.id)

        # 2) fusionar entidades por grupo (orden determinista).
        groups: dict[str, list[Entity]] = {}
        for entity in graph.entities:
            groups.setdefault(group_of[entity.id], []).append(entity)

        merged: list[Entity] = []
        id_remap: dict[str, str] = {}
        for key in sorted(groups):
            members = sorted(groups[key], key=lambda e: (-self._conf(e), e.id))
            survivor = self._merge(members, key, subject_key)
            merged.append(survivor)
            for member in members:
                id_remap[member.id] = survivor.id

        # 3) reapuntar relaciones y referencias; deduplicar.
        relationships = []
        for rel in graph.relationships:
            new = replace(
                rel,
                source_id=id_remap.get(rel.source_id, rel.source_id),
                target_id=id_remap.get(rel.target_id, rel.target_id),
            )
            if new.source_id == new.target_id:
                continue  # auto-relación tras fusión
            relationships.append(new)
        relationships = _dedupe(relationships)
        relationships.sort(key=lambda r: (r.source_id, r.relation, r.target_id))

        for entity in merged:
            entity.references = sorted(_dedupe(
                [id_remap.get(ref, ref) for ref in entity.references]
            ))

        resolved = replace(
            graph,
            entities=sorted(merged, key=lambda e: e.id),
            relationships=relationships,
            conflicts=entity_conflicts(sorted(merged, key=lambda e: e.id)),
        )
        return resolved

    @staticmethod
    def _subject_terms(knowledge: ProjectKnowledge | None) -> set[str]:
        if not knowledge:
            return set()
        terms = {slugify(knowledge.subject_name())} if knowledge.subject_name() else set()
        terms |= {slugify(a) for a in knowledge.aliases if a}
        if knowledge.title:
            terms.add(slugify(knowledge.title))
        return {t for t in terms if t}

    @staticmethod
    def _conf(entity: Entity) -> float:
        return max((s.confidence for s in entity.sources), default=0.0)

    @staticmethod
    def _merge(members: list[Entity], group_key: str, subject_key: str) -> Entity:
        survivor_id = (
            f"character:{subject_key}" if group_key.startswith("subject::") and subject_key
            else members[0].id
        )
        base = members[0]
        canonical = base.canonical_name
        etype = base.type
        aliases = list(base.aliases)
        attributes = {k: list(v) for k, v in base.attributes.items()}
        references = list(base.references)
        sources = list(base.sources)
        metadata = dict(base.metadata)

        for other in members[1:]:
            # nombres distintos al canónico pasan a ser alias (agrupar, no crear)
            if other.canonical_name and slugify(other.canonical_name) != slugify(canonical):
                aliases.append(other.canonical_name)
            aliases.extend(other.aliases)
            references.extend(other.references)
            sources.extend(other.sources)
            for fname, claims in other.attributes.items():
                attributes.setdefault(fname, [])
                attributes[fname] = _dedupe(attributes[fname] + list(claims))
            for k, v in other.metadata.items():
                metadata.setdefault(k, v)
            if etype == "character" and other.type != "character":
                etype = other.type

        # ordenar claims de forma estable
        for fname in attributes:
            attributes[fname] = sorted(
                attributes[fname], key=lambda c: (-c.confidence, c.provider, str(c.value))
            )

        return Entity(
            id=survivor_id, type=etype, canonical_name=canonical,
            aliases=_dedupe([a for a in aliases if a and slugify(a) != slugify(canonical)]),
            attributes=attributes, references=_dedupe(references),
            sources=_dedupe(sources), metadata=metadata,
        )
