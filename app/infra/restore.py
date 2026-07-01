"""Restore Plan (INF-001) — cómo reconstruir el proyecto desde un backup.

Es un PLAN determinista (pasos ordenados), no una restauración real: este subsistema nunca
ejecuta ni descarga nada. Nunca restaura binarios temporales (renders, workspaces, descargas).
"""

import os

from app.infra.models import RestorePlan, RestoreStep

# Carpetas que NUNCA se restauran (se regeneran solas).
_DO_NOT_RESTORE = ["cache", "workspace", "downloads", "render", "tmp", "outputs", "__pycache__"]


def build_restore_plan(root: str = ".") -> RestorePlan:
    req = "requirements.txt" if os.path.exists(os.path.join(root, "requirements.txt")) \
        else "pyproject.toml"
    steps = [
        RestoreStep(1, "create_folders", "app/ docs/ knowledge/ tests/ config/",
                    "crear el esqueleto de carpetas críticas"),
        RestoreStep(2, "restore_knowledge", "knowledge/",
                    "restaurar el conocimiento permanente (estadísticas + estilos + documentales)"),
        RestoreStep(3, "restore_docs", "docs/",
                    "restaurar ADR/RFC/SPEC/roadmap (la arquitectura)"),
        RestoreStep(4, "restore_code", "app/ tests/ config/ scripts/ templates/ tools/ prompts/",
                    "restaurar el código de los motores y sus pruebas"),
        RestoreStep(5, "restore_root_files", "main.py pyproject.toml requirements.txt .env.example",
                    "restaurar archivos raíz del proyecto"),
        RestoreStep(6, "restore_important_outputs",
                    "output/dca output/kbg output/system output/narrative output/eae output/projects",
                    "restaurar artefactos derivados recomendados (sin binarios)"),
        RestoreStep(7, "install_dependencies", req,
                    f"instalar dependencias desde {req}"),
        RestoreStep(8, "verify", "python -m app.cli.project_status",
                    "comprobar integridad y salud tras la restauración"),
    ]
    return RestorePlan(steps=steps, do_not_restore=list(_DO_NOT_RESTORE), requirements_file=req)
