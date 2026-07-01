"""Knowledge Snapshot (INF-001) — resumen completo del estado del conocimiento.

NUNCA copia vídeos. NUNCA copia output. Solo conocimiento (estadísticas + estilos sintetizados +
recuento de documentales aprendidos), con hashes de los estilos para detectar corrupción.
"""

import os

from app.infra.manifest import TEMP_DIR_NAMES, _load_json, dir_stats, sha256_file
from app.infra.manifest import file_size, rel
from app.infra.models import ArtifactHash, KnowledgeSnapshot


def build_knowledge_snapshot(root: str = ".") -> KnowledgeSnapshot:
    kroot = os.path.join(root, "knowledge")
    stats = _load_json(os.path.join(kroot, "learning_statistics.json"))

    styles_dir = os.path.join(kroot, "styles")
    styles: list[str] = []
    style_hashes: list[ArtifactHash] = []
    if os.path.isdir(styles_dir):
        for f in sorted(os.listdir(styles_dir)):
            if f.endswith(".json"):
                styles.append(f)
                p = os.path.join(styles_dir, f)
                style_hashes.append(ArtifactHash(path=rel(root, p), sha256=sha256_file(p),
                                                 size_bytes=file_size(p)))

    docs_dir = os.path.join(kroot, "documentaries")
    documentary_count = 0
    if os.path.isdir(docs_dir):
        documentary_count = sum(1 for n in os.listdir(docs_dir)
                                if os.path.isdir(os.path.join(docs_dir, n)))

    _files, ksize = dir_stats(kroot, exclude=TEMP_DIR_NAMES)

    return KnowledgeSnapshot(
        documentaries_learned=int(stats.get("documentaries_learned", 0) or 0),
        shots_analyzed=int(stats.get("shots_analyzed", 0) or 0),
        scenes_analyzed=int(stats.get("scenes", 0) or 0),
        hours_learned=float(stats.get("hours_learned", 0.0) or 0.0),
        styles=styles,
        documentary_count=documentary_count,
        statistics=stats,
        style_hashes=style_hashes,
        knowledge_size_bytes=ksize,
    )
