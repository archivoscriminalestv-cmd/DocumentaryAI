"""DossierBuilder — EvidenceGraph (+ ProjectKnowledge) → DocumentaryDossier.

Orquesta los motores independientes (people/locations/media/timeline/conflicts) y
ensambla el dossier. Determinista. No fusiona evidencias individuales, no infiere, no
resume, no decide qué es importante.
"""

from dataclasses import asdict

from app.dossier.conflicts import ConflictEngine
from app.dossier.locations import build_locations
from app.dossier.media import build_media, media_ids
from app.dossier.models import (
    CourtItem,
    DocumentaryDossier,
    DossierSource,
    NewsItem,
)
from app.dossier.people import build_people
from app.dossier.timeline import TimelineBuilder


def _dedupe(seq: list) -> list:
    out: list = []
    for item in seq:
        if item not in out:
            out.append(item)
    return out


class DossierBuilder:
    def build(self, graph, knowledge=None) -> DocumentaryDossier:
        images, videos = build_media(graph)
        img_ids, vid_ids = media_ids(images, videos)

        people = build_people(graph, img_ids, vid_ids)
        timeline = TimelineBuilder().build(graph)
        locations = build_locations(graph, knowledge, img_ids)
        conflicts = ConflictEngine().detect(people, timeline)

        news = sorted(
            (NewsItem(
                id=a.id, headline=a.headline, medium=a.medium, date=a.date, url=a.url,
                snippet=a.snippet, entities_detected=list(a.entities_detected),
                provider=a.source.provider, confidence=a.source.confidence,
                license=a.source.license,
            ) for a in graph.articles),
            key=lambda n: n.id,
        )
        court = sorted(
            (CourtItem(
                id=c.id, title=c.title, reference=c.reference, court=c.court,
                date=c.date, url=c.url, provider=c.provider,
                confidence=max((s.confidence for s in graph.sources
                                if s.provider == c.provider), default=0.0),
            ) for c in graph.court_documents),
            key=lambda c: c.id,
        )

        sources = _dedupe([
            DossierSource(provider=s.provider, url=s.url, source=s.source,
                          confidence=s.confidence, license=s.license)
            for s in graph.sources
        ])
        sources.sort(key=lambda s: (s.provider, s.url, s.source))

        relationships = sorted(
            (asdict(r) for r in graph.relationships),
            key=lambda r: (r["source_id"], r["relation"], r["target_id"]),
        )

        project = {
            "title": getattr(knowledge, "title", "") if knowledge else graph.project.name,
            "canonical_name": getattr(knowledge, "canonical_name", "") if knowledge else "",
            "subject_id": graph.project.subject_id(),
            "language": getattr(knowledge, "language", "") if knowledge else "",
            "genre": getattr(knowledge, "genre", "") if knowledge else "",
        }

        dossier = DocumentaryDossier(
            project=project,
            people=people,
            timeline=timeline,
            locations=locations,
            media_images=images,
            media_videos=videos,
            news=news,
            court_documents=court,
            relationships=relationships,
            conflicts=conflicts,
            sources=sources,
            providers_used=list(graph.providers_used),
        )
        dossier.coverage = _coverage(dossier)
        return dossier


def _coverage(dossier: DocumentaryDossier) -> dict:
    buckets = {
        "people": dossier.people,
        "timeline": dossier.timeline,
        "locations": dossier.locations,
        "media_images": dossier.media_images,
        "media_videos": dossier.media_videos,
        "news": dossier.news,
        "court_documents": dossier.court_documents,
        "relationships": dossier.relationships,
    }
    present = sum(1 for v in buckets.values() if v)

    # calidad: confianza media de las afirmaciones (timeline + atributos de persona)
    confidences: list[float] = [e.confidence for e in dossier.timeline]
    for person in dossier.people:
        for claims in person.attributes.values():
            confidences.extend(c.confidence for c in claims)
    avg_conf = round(sum(confidences) / len(confidences), 3) if confidences else 0.0

    return {
        "buckets_with_data": present,
        "buckets_total": len(buckets),
        "ratio": round(present / len(buckets), 3),
        "facts_scored": len(confidences),
        "average_confidence": avg_conf,
        "conflicts": len(dossier.conflicts),
    }
