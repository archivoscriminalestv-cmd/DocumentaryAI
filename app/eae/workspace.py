"""Project Workspace + WorkspaceManager (EAE-003).

Cada documental tiene un workspace TEMPORAL para el material descargado. Al terminar, TODO
el binario se elimina automáticamente; lo único permanente son los metadatos (manifest,
sources, timeline, verification, report) en la raíz del proyecto.

Layout:
    output/projects/<case>/
        workspace/{downloads,photos,videos,documents,audio,maps,news,cache}/   (temporal)
        manifest.json · timeline.json · sources.json · verification.json · report.json
        discovery_report.md

Este sprint NO descarga: crea la estructura y deja todo listo para la adquisición.
"""

import os
import shutil
from dataclasses import dataclass, field

WORKSPACE_SUBDIRS = ("downloads", "photos", "videos", "documents", "audio", "maps",
                     "news", "cache")
# Ficheros de metadatos PERMANENTES (nunca se borran al finalizar el workspace).
METADATA_FILES = ("manifest.json", "timeline.json", "sources.json", "verification.json",
                  "report.json", "discovery_report.md")


@dataclass
class Workspace:
    case_id: str
    project_dir: str
    workspace_dir: str
    subdirs: dict = field(default_factory=dict)

    def path(self, name: str) -> str:
        return self.subdirs[name]

    def metadata_path(self, filename: str) -> str:
        return os.path.join(self.project_dir, filename)


class WorkspaceManager:
    def __init__(self, root: str = os.path.join("output", "projects")) -> None:
        self.root = root

    def create(self, case_id: str) -> Workspace:
        project_dir = os.path.join(self.root, case_id)
        workspace_dir = os.path.join(project_dir, "workspace")
        subdirs = {}
        for name in WORKSPACE_SUBDIRS:
            path = os.path.join(workspace_dir, name)
            os.makedirs(path, exist_ok=True)
            subdirs[name] = path
        return Workspace(case_id=case_id, project_dir=project_dir,
                         workspace_dir=workspace_dir, subdirs=subdirs)

    def size(self, workspace: Workspace) -> int:
        total = 0
        for base, _dirs, files in os.walk(workspace.workspace_dir):
            for name in files:
                try:
                    total += os.path.getsize(os.path.join(base, name))
                except OSError:
                    pass
        return total

    def clean_cache(self, workspace: Workspace) -> None:
        cache = workspace.subdirs.get("cache")
        if cache and os.path.isdir(cache):
            shutil.rmtree(cache, ignore_errors=True)
            os.makedirs(cache, exist_ok=True)

    def finalize(self, workspace: Workspace) -> int:
        """Elimina TODO el binario (workspace/) al terminar; conserva los metadatos.

        Seguridad: solo borra el subárbol ``.../workspace``; nunca el project_dir ni sus
        JSON. Devuelve los bytes liberados.
        """
        if os.path.basename(workspace.workspace_dir.rstrip(os.sep)) != "workspace":
            return 0                          # nunca borra algo que no sea el workspace
        freed = self.size(workspace)
        shutil.rmtree(workspace.workspace_dir, ignore_errors=True)
        return freed
