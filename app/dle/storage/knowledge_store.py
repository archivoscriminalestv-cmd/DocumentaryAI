"""Base de conocimiento permanente del DLE (``knowledge/documentaries/<id>/``).

Cada documental tiene un ID estable. Nunca se sobrescribe un documental distinto; un
re-análisis del mismo (mismo ID) es idempotente (no duplica). ``exists`` permite saltar
el re-análisis.
"""

import os

from app.dle.models import DocumentaryKnowledge
from app.dle.persistence import write_knowledge


class KnowledgeStore:
    def __init__(self, root: str = "knowledge") -> None:
        self.root = root
        self.docs_dir = os.path.join(root, "documentaries")

    def doc_dir(self, documentary_id: str) -> str:
        return os.path.join(self.docs_dir, documentary_id)

    def exists(self, documentary_id: str) -> bool:
        return os.path.exists(os.path.join(self.doc_dir(documentary_id), "documentary.json"))

    def save(self, knowledge: DocumentaryKnowledge) -> dict[str, str]:
        return write_knowledge(self.doc_dir(knowledge.documentary_id), knowledge)

    def list_ids(self) -> list[str]:
        if not os.path.exists(self.docs_dir):
            return []
        return sorted(d for d in os.listdir(self.docs_dir)
                      if os.path.exists(os.path.join(self.docs_dir, d, "documentary.json")))
