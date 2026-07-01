"""Catálogo de evidencia multimedia del dossier.

Cada imagen/vídeo del EvidenceGraph se registra INDIVIDUALMENTE (sin fusionar) y SIN
descargar (``hash`` pendiente). Conserva URL, licencia, autor, resolución y proveedor.
"""

from app.dossier.models import MediaImage, MediaVideo


def _source_index(graph) -> dict[str, object]:
    """url -> SourceRef, para recuperar confianza/licencia por URL."""
    index: dict[str, object] = {}
    for src in graph.sources:
        if getattr(src, "url", ""):
            index.setdefault(src.url, src)
    return index


def build_media(graph) -> tuple[list[MediaImage], list[MediaVideo]]:
    src_index = _source_index(graph)

    images: list[MediaImage] = []
    for img in graph.images:
        src = src_index.get(img.original_url)
        images.append(MediaImage(
            id=img.id, url=img.original_url, thumbnail_url=img.thumbnail_url,
            license=img.license, author=img.author, caption=img.caption,
            resolution=img.resolution, hash=img.hash, provider=img.provider,
            confidence=getattr(src, "confidence", 0.0) if src else 0.0,
            relevance=img.relevance,
        ))

    videos: list[MediaVideo] = []
    for vid in graph.videos:
        src = src_index.get(vid.url)
        videos.append(MediaVideo(
            id=vid.id, url=vid.url, title=vid.title, channel=vid.channel,
            duration=vid.duration, published=vid.published,
            thumbnail_url=vid.thumbnail_url, license=vid.license, hash="",
            provider=vid.provider,
            confidence=getattr(src, "confidence", 0.0) if src else 0.0,
        ))

    images.sort(key=lambda m: m.id)
    videos.sort(key=lambda m: m.id)
    return images, videos


def media_ids(images: list[MediaImage], videos: list[MediaVideo]) -> tuple[set[str], set[str]]:
    return {i.id for i in images}, {v.id for v in videos}
