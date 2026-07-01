"""Orquestador del Architectural Backlog (DCA-004).

Compone loader + validator + updater. Es la capacidad que el DocumentaryChiefArchitect usa para
leer el backlog, validarlo y PROPONER cambios tras un sprint. Solo lectura del documento; las
propuestas se escriben como artefactos en ``output/dca/backlog/`` (nunca el documento humano).
"""

import os

from app.dca.backlog.loader import BacklogLoader
from app.dca.backlog.models import ArchitecturalBacklog, BacklogProposal
from app.dca.backlog.updater import BacklogUpdater
from app.dca.backlog.validator import BacklogValidator

DEFAULT_BACKLOG_PATH = os.path.join("docs", "roadmap", "ARCHITECTURAL-BACKLOG.md")


class BacklogOrchestrator:
    def __init__(self, path: str = DEFAULT_BACKLOG_PATH, loader=None, validator=None,
                 updater=None) -> None:
        self._path = path
        self._loader = loader or BacklogLoader()
        self._validator = validator or BacklogValidator()
        self._updater = updater or BacklogUpdater()
        self._cache: ArchitecturalBacklog | None = None

    def load(self, refresh: bool = False) -> ArchitecturalBacklog:
        if self._cache is None or refresh:
            self._cache = self._loader.load(self._path)
        return self._cache

    def validate(self) -> list:
        return self._validator.validate(self.load())

    def review(self, sprint_review: dict) -> BacklogProposal:
        """Genera la propuesta de cambios de un sprint (no escribe el documento)."""
        return self._updater.propose(self.load(), sprint_review)

    def summary(self) -> dict:
        backlog = self.load()
        issues = self.validate()
        return {
            "source_path": backlog.source_path,
            "counts": backlog.counts,
            "issues": {
                "errors": sum(1 for i in issues if i.level == "ERROR"),
                "warnings": sum(1 for i in issues if i.level == "WARNING"),
            },
        }
