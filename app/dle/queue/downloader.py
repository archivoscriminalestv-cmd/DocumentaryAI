"""Registro de fuentes desacoplado (Downloader Interface).

Permite enchufar mañana YouTube/Vimeo/Archive.org/RTVE/BBC/… sin tocar el motor: cada
tipo sabe reconocer su URL, predecir el documentary_id SIN descargar y decir cómo
invocar al DLE. Provider-agnóstico.
"""

import os
from dataclasses import dataclass
from typing import Callable

from app.dle.downloader.youtube import video_id_from_url
from app.dle.providers.local_video import _file_hash


@dataclass
class ResolvedSource:
    kind: str
    video_id: str
    documentary_id: str
    learn_kwargs: dict        # {youtube: url} | {video: path}


@dataclass
class SourceType:
    name: str
    matches: Callable[[str], bool]
    resolve: Callable[[str], ResolvedSource]


def _is_youtube(ref: str) -> bool:
    r = ref.lower()
    return "youtube.com" in r or "youtu.be" in r


def _resolve_youtube(ref: str) -> ResolvedSource:
    vid = video_id_from_url(ref)
    return ResolvedSource(kind="youtube", video_id=vid,
                          documentary_id=f"doc_yt_{vid}", learn_kwargs={"youtube": ref})


def _is_local(ref: str) -> bool:
    return os.path.exists(ref)


def _resolve_local(ref: str) -> ResolvedSource:
    h = _file_hash(ref)
    return ResolvedSource(kind="local", video_id=h,
                          documentary_id=f"doc_{h}", learn_kwargs={"video": ref})


# Orden = prioridad de coincidencia. Extensible con ``register``.
_REGISTRY: list[SourceType] = [
    SourceType("youtube", _is_youtube, _resolve_youtube),
    SourceType("local", _is_local, _resolve_local),
]


def register(source_type: SourceType, *, front: bool = True) -> None:
    _REGISTRY.insert(0 if front else len(_REGISTRY), source_type)


def resolve_source(ref: str) -> ResolvedSource | None:
    for st in _REGISTRY:
        try:
            if st.matches(ref):
                return st.resolve(ref)
        except Exception:
            continue
    return None
