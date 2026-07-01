"""Backup Plan (INF-001) — qué copiar y qué no, de forma determinista.

Clasifica las carpetas/archivos del proyecto en CRITICAL (nunca perder), IMPORTANT (recomendado)
y TEMPORARY (nunca copiar). El conocimiento es permanente; los binarios temporales (renders,
workspaces, descargas) son desechables. Solo lectura.
"""

import os

from app.infra.manifest import TEMP_DIR_NAMES, dir_stats, file_size
from app.infra.models import BackupClass, BackupEntry, BackupPlan

# (ruta relativa, motivo)
_CRITICAL = [
    ("app", "código de todos los motores"),
    ("docs", "ADR/RFC/SPEC/roadmap: la arquitectura y las decisiones"),
    ("knowledge", "conocimiento aprendido permanente (sin binarios)"),
    ("tests", "garantía de comportamiento del sistema"),
    ("config", "configuración del proyecto"),
    ("scripts", "utilidades y automatizaciones"),
    ("templates", "plantillas del proyecto"),
    ("tools", "herramientas del proyecto"),
    ("prompts", "prompts del sistema"),
    ("main.py", "punto de entrada"),
    ("pyproject.toml", "definición del paquete y dependencias"),
    ("requirements.txt", "dependencias"),
    ("CONTRIBUTING.md", "guía de contribución"),
    (".env.example", "plantilla de variables de entorno"),
    (".gitignore", "reglas de exclusión"),
    (".github", "CI / workflows"),
]
_IMPORTANT = [
    ("output/dca", "informes del arquitecto (DCA)"),
    ("output/kbg", "generation knowledge (KBG)"),
    ("output/system", "manifiestos y snapshots de infraestructura"),
    ("output/narrative", "blueprints narrativos (NAR)"),
    ("output/eae", "planes de evidencia (EAE)"),
    ("output/projects", "metadatos de casos investigados (sin binarios)"),
    ("datasets", "datos de entrada"),
    ("library", "biblioteca de assets permanente del ALR (binario; el usuario decide)"),
    ("assets", "activos del proyecto"),
    ("channel_intro.mp4", "intro del canal"),
    ("projects", "proyectos (metadatos)"),
    ("Agents", "configuración de agentes"),
]
_TEMPORARY = [
    ("cache", "caché regenerable"),
    ("workspace", "workspace temporal de casos"),
    ("downloads", "descargas temporales (binarios)"),
    ("render", "renders regenerables"),
    ("tmp", "archivos temporales"),
    ("outputs", "salidas derivadas regenerables"),
    ("__pycache__", "bytecode de Python"),
]


def _entry(root: str, relpath: str, classification: str, reason: str,
           measure: bool) -> BackupEntry:
    abspath = os.path.join(root, *relpath.split("/"))
    exists = os.path.exists(abspath)
    file_count = 0
    size = 0
    if exists and measure:
        if os.path.isdir(abspath):
            file_count, size = dir_stats(abspath, exclude=TEMP_DIR_NAMES)
        else:
            file_count, size = 1, file_size(abspath)
    return BackupEntry(path=relpath, classification=classification, exists=exists,
                       reason=reason, file_count=file_count, size_bytes=size)


def build_backup_plan(root: str = ".") -> BackupPlan:
    plan = BackupPlan()
    plan.critical = [_entry(root, p, BackupClass.CRITICAL, r, measure=True) for p, r in _CRITICAL]
    plan.important = [_entry(root, p, BackupClass.IMPORTANT, r, measure=True) for p, r in _IMPORTANT]
    # Las temporales no se miden (no se recorren): nunca se copian.
    plan.temporary = [_entry(root, p, BackupClass.TEMPORARY, r, measure=False) for p, r in _TEMPORARY]
    return plan
