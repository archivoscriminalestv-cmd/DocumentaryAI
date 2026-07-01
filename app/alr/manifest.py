"""Manifest de documental por REFERENCIA (ALR).

Un documental no posee imágenes: las referencia por ``asset_id``. Este módulo
construye/serializa ``documentary_manifest``: project -> scenes -> shots -> asset_id.
Nunca contiene rutas de imagen propias del render temporal como fuente de verdad.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any

from app.alr import SCHEMA_VERSION


@dataclass
class ShotReference:
    shot: str
    shot_id: str
    asset_id: str
    library_path: str
    status: str = ""          # new | referenced | perceptual_duplicate


@dataclass
class DocumentaryManifest:
    project: str
    render_id: str = ""
    schema_version: str = SCHEMA_VERSION
    scenes: dict[str, list[ShotReference]] = field(default_factory=dict)

    def add(self, scene: str, ref: ShotReference) -> None:
        self.scenes.setdefault(scene, []).append(ref)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "project": self.project,
            "render_id": self.render_id,
            "scenes": {
                scene: [r.__dict__ for r in refs] for scene, refs in self.scenes.items()
            },
            "asset_ids": [r.asset_id for refs in self.scenes.values() for r in refs],
        }

    def write(self, path: str) -> str:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, ensure_ascii=False, indent=2)
        return path
