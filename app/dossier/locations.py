"""Extracción de lugares del EvidenceGraph (+ contexto declarado) hacia el dossier.

Incluye las entidades de tipo ``location`` del grafo y los lugares declarados en el
``ProjectKnowledge`` (marcados con proveedor ``project_knowledge`` como contexto, no
como hecho descubierto). Coordenadas reservadas (sin geocodificación inventada).
"""

from app.ere.models import slugify
from app.dossier.models import Location


def build_locations(graph, knowledge, image_ids: set[str]) -> list[Location]:
    locations: dict[str, Location] = {}

    # 1) lugares con evidencia (entidades 'location' del grafo)
    for entity in graph.entities:
        if entity.type != "location":
            continue
        conf = max((s.confidence for s in entity.sources), default=0.0)
        provider = entity.sources[0].provider if entity.sources else ""
        url = entity.sources[0].url if entity.sources else ""
        loc = Location(
            id=entity.id, name=entity.canonical_name, type="location",
            coordinates=str(entity.metadata.get("coordinates", "")),
            confidence=conf, provider=provider, source_url=url,
        )
        for rel in graph.relationships:
            if rel.source_id == entity.id and rel.target_id in image_ids:
                loc.photos.append(rel.target_id)
        loc.photos.sort()
        locations[entity.id] = loc

    # 2) lugares declarados en el ProjectKnowledge (contexto trazable)
    if knowledge is not None:
        for name in knowledge.locations:
            loc_id = f"location:{slugify(name)}"
            if loc_id not in locations:
                locations[loc_id] = Location(
                    id=loc_id, name=name, type="context",
                    provider="project_knowledge", confidence=0.5,
                )

    return sorted(locations.values(), key=lambda loc: loc.id)
