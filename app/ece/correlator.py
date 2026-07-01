"""Correlación de evidencias (ECE) — construye el EvidenceGraph y detecta conflictos.

Solo a partir de hechos OBSERVABLES de cada evidencia (su ``target``, su fecha, su texto):
- SAME_PERSON / SAME_LOCATION / SAME_EVENT cuando la evidencia apunta a esa entidad,
- REFERENCES cuando una fuente de referencia (Wikipedia/Wikidata) trata de la entidad,
- MENTIONS cuando el título/descripción nombra literalmente a otra entidad,
- REFERENCES a la Timeline cuando la evidencia tiene fecha conocida,
- SUPPORTS / CONTRADICTS entre evidencias del mismo sujeto según coincidan o difieran sus
  fechas. Los conflictos se REGISTRAN (requires_verification=True); nunca se deciden.
"""

from app.eae import UNKNOWN
from app.eae.planner.models import slugify
from app.ece.models import (
    Conflict,
    EvidenceGraph,
    GraphNode,
    GraphRelation,
    NodeType,
    RelationType,
)

_REFERENCE_PROVIDERS = {"wikipedia", "wikidata"}


def _known(value) -> bool:
    return bool(value) and value != UNKNOWN


def _ev_text(ev) -> str:
    extra = ev.extra or {}
    parts = [ev.title or "", extra.get("description", ""), extra.get("snippet", ""),
             extra.get("display_name", "")]
    return " ".join(str(p) for p in parts).lower()


class EvidenceCorrelationEngine:
    def correlate(self, plan, discovery_plan) -> tuple[EvidenceGraph, list[Conflict]]:
        profile = plan.profile
        people = list(profile.people) if profile else []
        locations = list(profile.locations) if profile else []
        events = list(profile.events) if profile else []

        # nodos de entidad + índice nombre -> (node_id, relation_directa)
        nodes: dict[str, GraphNode] = {}
        name_index: dict[str, tuple[str, str]] = {}

        def _entity(kind_id_prefix, ntype, relation, name):
            nid = f"{kind_id_prefix}:{slugify(name)}"
            nodes[nid] = GraphNode(id=nid, type=ntype, label=name)
            name_index[name] = (nid, relation)

        for p in people:
            _entity("person", NodeType.PERSON, RelationType.SAME_PERSON, p)
        for loc in locations:
            _entity("location", NodeType.LOCATION, RelationType.SAME_LOCATION, loc)
        for ev_name in events:
            _entity("event", NodeType.EVENT, RelationType.SAME_EVENT, ev_name)

        timeline_id = "timeline:case"
        nodes[timeline_id] = GraphNode(id=timeline_id, type=NodeType.TIMELINE,
                                       label="Case timeline", attributes={"events": events})

        relations: list[GraphRelation] = []
        by_target: dict[str, list] = {}

        for ev in discovery_plan.discovered:
            ev_node_id = f"evidence:{ev.id}"
            nodes[ev_node_id] = GraphNode(
                id=ev_node_id, type=NodeType.EVIDENCE, label=ev.title or ev.id,
                attributes={"category": ev.category, "provider": ev.provider,
                            "license": ev.license, "url": ev.url, "date": ev.date,
                            "target": ev.target})
            by_target.setdefault(ev.target, []).append(ev)

            # relación directa con la entidad objetivo (hecho observable: la evidencia
            # se localizó PARA esa entidad)
            if ev.target in name_index:
                entity_id, relation = name_index[ev.target]
                relations.append(GraphRelation(ev_node_id, relation, entity_id,
                                               [ev.id], "evidence targets entity"))
                if ev.provider in _REFERENCE_PROVIDERS:
                    relations.append(GraphRelation(ev_node_id, RelationType.REFERENCES,
                                                   entity_id, [ev.id],
                                                   f"{ev.provider} reference about entity"))

            # MENTIONS: el texto nombra literalmente a otra entidad
            text = _ev_text(ev)
            for name, (entity_id, _rel) in name_index.items():
                if name == ev.target or len(name) < 3:
                    continue
                if name.lower() in text:
                    relations.append(GraphRelation(ev_node_id, RelationType.MENTIONS,
                                                   entity_id, [ev.id], "text mentions entity"))

            # REFERENCES a la cronología si la evidencia tiene fecha conocida
            if _known(ev.date):
                relations.append(GraphRelation(ev_node_id, RelationType.REFERENCES,
                                               timeline_id, [ev.id], f"dated {ev.date}"))

        conflicts = self._date_relations_and_conflicts(by_target, name_index, relations)

        nodes_list = sorted(nodes.values(), key=lambda n: n.id)
        relations = _dedupe(relations)
        relations.sort(key=lambda r: (r.source_id, r.relation, r.target_id))
        return EvidenceGraph(nodes=nodes_list, relations=relations), conflicts

    @staticmethod
    def _date_relations_and_conflicts(by_target, name_index, relations) -> list[Conflict]:
        conflicts: list[Conflict] = []
        for target, evs in sorted(by_target.items()):
            dated = [(e.date, e) for e in evs if _known(e.date)]
            # SUPPORTS / CONTRADICTS por pares (mismo sujeto)
            for i in range(len(dated)):
                for j in range(i + 1, len(dated)):
                    a_date, a = dated[i]
                    b_date, b = dated[j]
                    rel = RelationType.SUPPORTS if a_date == b_date else RelationType.CONTRADICTS
                    relations.append(GraphRelation(
                        f"evidence:{a.id}", rel, f"evidence:{b.id}",
                        [a.id, b.id], f"dates {a_date} vs {b_date}"))
            distinct = []
            for date, e in dated:
                if date not in [d["value"] for d in distinct]:
                    distinct.append({"value": date, "evidence_id": e.id, "provider": e.provider})
            if len(distinct) > 1:
                subject_id = name_index.get(target, (f"target:{slugify(target)}", ""))[0]
                conflicts.append(Conflict(
                    id=f"conflict:date:{slugify(target)}", kind="date",
                    subject_id=subject_id, field="date",
                    candidates=sorted(distinct, key=lambda d: (str(d["value"]), d["evidence_id"])),
                    requires_verification=True))
        conflicts.sort(key=lambda c: c.id)
        return conflicts


def _dedupe(relations: list[GraphRelation]) -> list[GraphRelation]:
    seen: dict[tuple, GraphRelation] = {}
    for r in relations:
        key = (r.source_id, r.relation, r.target_id)
        if key in seen:
            for eid in r.evidence_ids:                  # fusiona soportes
                if eid not in seen[key].evidence_ids:
                    seen[key].evidence_ids.append(eid)
        else:
            seen[key] = GraphRelation(r.source_id, r.relation, r.target_id,
                                      list(r.evidence_ids), r.basis)
    return list(seen.values())
