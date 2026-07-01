"""Rutas y constantes de DocumentaryAI Studio (DAS-001).

Resuelve la raíz del proyecto (la carpeta que contiene ``app/``) y expone las rutas de los
artefactos que Studio CONSUME (estadísticas y cola del DLE) y de los que gestiona (lock/log de
la sesión de aprendizaje). Todas las funciones aceptan un ``root`` opcional para poder testear
con un proyecto falso.
"""

import os

# .../app/studio/config.py  →  raíz = tres niveles arriba
_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_ROOT = os.path.dirname(os.path.dirname(_HERE))


def project_root(root: str | None = None) -> str:
    return os.path.abspath(root or _DEFAULT_ROOT)


def knowledge_dir(root: str | None = None) -> str:
    return os.path.join(project_root(root), "knowledge")


def stats_path(root: str | None = None) -> str:
    """learning_statistics.json — estadísticas ya calculadas por el DLE (nunca se recalculan)."""
    return os.path.join(knowledge_dir(root), "learning_statistics.json")


def queue_path(root: str | None = None) -> str:
    """learning_queue.json — cola persistente del DLE (para leer el vídeo en curso)."""
    return os.path.join(knowledge_dir(root), "learning_queue.json")


def studio_dir(root: str | None = None) -> str:
    return os.path.join(project_root(root), "output", "studio")


def lock_path(root: str | None = None) -> str:
    """Marca de sesión de aprendizaje lanzada por Studio (PID + inicio)."""
    return os.path.join(studio_dir(root), "learning.lock")


def run_log_path(root: str | None = None) -> str:
    """Salida del proceso learn_queue lanzado por Studio."""
    return os.path.join(studio_dir(root), "learning_run.log")
