"""Extracción de personas del EvidenceGraph hacia el dossier.

Genérico (sin lógica de ningún caso concreto): cada entidad de tipo persona se
convierte en ``Person`` con sus atributos atribuidos, sus relaciones (familia,
amistades, bandas, organizaciones, lugares habituales) y sus referencias multimedia.
Nada se infiere: solo se mapea lo que el grafo aporta, con procedencia.
"""

from app.dossier.claims import DossierClaim, from_ere_claim, license_lookup
from app.dossier.models import Person

PERSON_TYPES = {"character", "person"}

_FAMILY = {"family_of", "relative_of", "parent_of", "child_of", "sibling_of", "married_to", "spouse_of"}
_FRIENDS = {"friend_of", "knows"}
_BANDS = {"band_member_of", "plays_in"}
_ORGS = {"member_of", "works_for", "affiliated_with"}
_LOCATIONS = {"located_in", "frequented", "lives_in", "resident_of", "based_in"}


def build_people(graph, image_ids: set[str], video_ids: set[str]) -> list[Person]:
    by_id = {e.id: e for e in graph.entities}
    people: list[Person] = []

    for entity in graph.entities:
        if entity.type not in PERSON_TYPES:
            continue
        licenses = license_lookup(entity.sources)
        attributes = {
            fname: [from_ere_claim(c, licenses) for c in claims]
            for fname, claims in entity.attributes.items()
        }

        person = Person(
            id=entity.id, name=entity.canonical_name, aliases=list(entity.aliases),
            attributes=attributes,
        )

        def _name_of(target_id: str) -> str:
            target = by_id.get(target_id)
            return target.canonical_name if target and target.canonical_name else target_id

        for rel in graph.relationships:
            if rel.source_id != entity.id:
                continue
            claim = DossierClaim(
                field=rel.relation, value=_name_of(rel.target_id),
                confidence=rel.confidence, provider=rel.provider,
            )
            if rel.relation in _FAMILY:
                person.family.append(claim)
            elif rel.relation in _FRIENDS:
                person.friends.append(claim)
            elif rel.relation in _BANDS:
                person.bands.append(claim)
            elif rel.relation in _ORGS:
                target = by_id.get(rel.target_id)
                (person.bands if target and target.type == "band" else person.organizations).append(claim)
            elif rel.relation in _LOCATIONS:
                if rel.target_id not in person.usual_locations:
                    person.usual_locations.append(rel.target_id)

        # referencias multimedia: relaciones + entity.references
        for ref in list(entity.references) + [
            r.target_id for r in graph.relationships
            if r.source_id == entity.id and r.relation in ("has_reference", "depicted_in")
        ]:
            if ref in image_ids and ref not in person.photos:
                person.photos.append(ref)
            elif ref in video_ids and ref not in person.videos:
                person.videos.append(ref)

        person.usual_locations.sort()
        person.photos.sort()
        person.videos.sort()
        people.append(person)

    people.sort(key=lambda p: p.id)
    return people
