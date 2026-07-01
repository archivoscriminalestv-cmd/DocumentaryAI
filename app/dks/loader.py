"""Carga la base de conocimiento del DLE para sintetizarla (DKS).

Lee directamente ``knowledge/documentaries/<id>/{documentary.json, statistics.json,
shots.json}``. Independiente del DLE (solo consume sus ficheros en disco). Nunca
descarga ni analiza vídeo. Determinista: ordena los documentales por id.
"""

import json
import os
from dataclasses import dataclass, field


@dataclass
class DocRecord:
    documentary_id: str
    duration: float = 0.0
    statistics: dict = field(default_factory=dict)
    shots: list[dict] = field(default_factory=list)


@dataclass
class Corpus:
    documentaries: list[DocRecord] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.documentaries)

    def all_shots(self) -> list[dict]:
        return [shot for doc in self.documentaries for shot in doc.shots]


def _read_json(path: str):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None


def load_corpus(knowledge_root: str = "knowledge") -> Corpus:
    docs_dir = os.path.join(knowledge_root, "documentaries")
    corpus = Corpus()
    if not os.path.isdir(docs_dir):
        return corpus
    for doc_id in sorted(os.listdir(docs_dir)):
        doc_path = os.path.join(docs_dir, doc_id)
        index = _read_json(os.path.join(doc_path, "documentary.json"))
        if not isinstance(index, dict):
            continue                       # carpeta incompleta: se ignora, no se inventa
        stats = _read_json(os.path.join(doc_path, "statistics.json")) or {}
        shots = _read_json(os.path.join(doc_path, "shots.json")) or []
        corpus.documentaries.append(DocRecord(
            documentary_id=doc_id,
            duration=float(index.get("metadata", {}).get("duration", 0.0)),
            statistics=stats if isinstance(stats, dict) else {},
            shots=shots if isinstance(shots, list) else [],
        ))
    return corpus
