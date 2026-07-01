"""Arquitectura de ALMACENAMIENTO del EAE (EAE-001) — biblioteca permanente (contrato).

Define la ESTRUCTURA objetivo de la biblioteca documental por caso. NO almacena binarios
todavía: ``store`` solo PLANIFICA la ruta donde iría una evidencia. Nunca escribe en
``knowledge/`` (raíz por defecto ``output/eae/``).
"""

import os

from app.eae import UNKNOWN
from app.eae.models import Evidence, EvidenceKind

# Estructura objetivo de la biblioteca de un caso.
LIBRARY_LAYOUT = (
    "people", "locations", "timeline", "photos", "videos", "documents",
    "maps", "articles", "social", "metadata",
)

# Tipo de evidencia -> subcarpeta de la biblioteca.
_KIND_DIR = {
    EvidenceKind.PHOTO: "photos",
    EvidenceKind.VIDEO: "videos",
    EvidenceKind.INTERVIEW: "videos",
    EvidenceKind.PRESS_CONFERENCE: "videos",
    EvidenceKind.AUDIO: "videos",
    EvidenceKind.DOCUMENT: "documents",
    EvidenceKind.PDF: "documents",
    EvidenceKind.COURT_RECORD: "documents",
    EvidenceKind.OFFICIAL_PUBLICATION: "documents",
    EvidenceKind.STATEMENT: "documents",
    EvidenceKind.MAP: "maps",
    EvidenceKind.NEWS: "articles",
    EvidenceKind.SOCIAL_POST: "social",
    EvidenceKind.TIMELINE: "timeline",
}


class BaseEvidenceStorage:
    """Implementa ``EvidenceStorage`` como contrato. Planifica rutas; no escribe binarios."""

    def __init__(self, root: str = os.path.join("output", "eae")) -> None:
        if "knowledge" in os.path.normpath(root).split(os.sep):
            raise ValueError("El EAE nunca debe escribir dentro de knowledge/")
        self.root = root

    def case_dir(self, case_id: str) -> str:
        return os.path.join(self.root, "cases", case_id)

    def layout(self) -> dict:
        return {"root": self.root, "case_subdirs": list(LIBRARY_LAYOUT)}

    def planned_path(self, case_id: str, evidence: Evidence) -> str:
        subdir = _KIND_DIR.get(evidence.kind, "metadata")
        ext = ""  # desconocido hasta adquirir
        return os.path.join(self.case_dir(case_id), subdir, f"{evidence.id}{ext}")

    def store(self, evidence: Evidence) -> str:
        """Contrato EAE-001: devuelve la ruta planificada SIN escribir binarios."""
        return self.planned_path(case_id=UNKNOWN, evidence=evidence)
