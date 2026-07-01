"""Índice de conocimiento: evita aprender dos veces el mismo documental.

Mapea documentary_id -> {video_id, canonical_url, hash, schema_version}. Permite
detectar SKIPPED por id de vídeo, URL canónica o hash, ANTES de descargar. Soporta la
decisión de aprendizaje incremental: si el esquema almacenado < esquema actual, procede
re-aprender; si es igual, se omite.
"""

import json
import os

from app.dle import SCHEMA_VERSION


class KnowledgeIndex:
    def __init__(self, path: str = os.path.join("knowledge", "learning_index.json")) -> None:
        self.path = path
        self._by_doc: dict[str, dict] = {}
        self._by_video: dict[str, str] = {}
        self._by_url: dict[str, str] = {}
        self.load()

    def load(self) -> "KnowledgeIndex":
        self._by_doc.clear(); self._by_video.clear(); self._by_url.clear()
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as h:
                    data = json.load(h)
                for doc_id, entry in (data.get("entries", {}) or {}).items():
                    self._register_local(doc_id, entry)
            except (OSError, json.JSONDecodeError):
                pass
        return self

    def save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.path)) or ".", exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as h:
            json.dump({"entries": self._by_doc}, h, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(tmp, self.path)

    def _register_local(self, doc_id: str, entry: dict) -> None:
        self._by_doc[doc_id] = entry
        if entry.get("video_id"):
            self._by_video[entry["video_id"]] = doc_id
        if entry.get("canonical_url"):
            self._by_url[entry["canonical_url"]] = doc_id

    def record(self, *, documentary_id: str, video_id: str = "", canonical_url: str = "",
               hash: str = "", schema_version: str = SCHEMA_VERSION) -> None:
        self._register_local(documentary_id, {
            "video_id": video_id, "canonical_url": canonical_url,
            "hash": hash, "schema_version": schema_version,
        })

    def find(self, *, documentary_id: str = "", video_id: str = "", url: str = "") -> dict | None:
        doc_id = (documentary_id if documentary_id in self._by_doc else
                  self._by_video.get(video_id) or self._by_url.get(url))
        return self._by_doc.get(doc_id) if doc_id else None

    def should_skip(self, *, documentary_id: str = "", video_id: str = "", url: str = "") -> bool:
        """True si ya está aprendido con el esquema ACTUAL (mismo → omitir)."""
        entry = self.find(documentary_id=documentary_id, video_id=video_id, url=url)
        if entry is None:
            return False
        return str(entry.get("schema_version", "")) >= SCHEMA_VERSION

    def __len__(self) -> int:
        return len(self._by_doc)
