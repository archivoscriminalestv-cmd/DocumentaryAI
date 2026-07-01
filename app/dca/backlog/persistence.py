"""Persistencia del Architectural Backlog (DCA-004).

Escribe SOLO artefactos derivados (propuestas, snapshots, informes) en ``output/dca/backlog/``.
NUNCA toca el documento humano (``docs/roadmap/ARCHITECTURAL-BACKLOG.md``) ni ``knowledge/``:
el backlog se edita a mano tras aprobar la propuesta del DCA.
"""

import json
import os

from app.dca.backlog.models import ArchitecturalBacklog, BacklogProposal

_DOC_NAME = "ARCHITECTURAL-BACKLOG.md"


def _guard(out_dir: str) -> None:
    parts = os.path.normpath(out_dir).split(os.sep)
    if "knowledge" in parts:
        raise ValueError("El backlog del DCA nunca debe escribir dentro de knowledge/")
    if "roadmap" in parts:
        raise ValueError("El documento del backlog se edita a mano; no se escribe automáticamente")


def write_proposal(proposal: BacklogProposal,
                   out_dir: str = os.path.join("output", "dca", "backlog")) -> dict[str, str]:
    _guard(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    name = f"proposal_{proposal.sprint}".replace(os.sep, "_") + ".json"
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as h:
        json.dump(proposal.to_dict(), h, ensure_ascii=False, indent=2, sort_keys=True)
    return {"proposal": path}


def write_snapshot(backlog: ArchitecturalBacklog,
                   out_dir: str = os.path.join("output", "dca", "backlog")) -> dict[str, str]:
    """Snapshot interno del backlog cargado (para auditoría); no es el documento humano."""
    _guard(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "backlog_snapshot.json")
    with open(path, "w", encoding="utf-8") as h:
        json.dump(backlog.to_dict(), h, ensure_ascii=False, indent=2, sort_keys=True)
    return {"snapshot": path}
