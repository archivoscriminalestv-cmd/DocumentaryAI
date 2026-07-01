"""Git Repository Sanitizer & Readiness (INF-003) — `app/gitops/`.

Utilidad de infraestructura Git: audita el árbol del proyecto, clasifica los archivos, revisa el
.gitignore, detecta archivos grandes (aviso >50 MB, BLOQUEO >100 MB por el límite de GitHub) y
posibles secretos, y produce un informe de "Git readiness". Deja el repositorio preparado para el
primer backup, pero NUNCA ejecuta git add/commit/push (eso lo hace el usuario a mano).

No es un motor: no aprende, no genera, no toca DLE/VIS/VAI/Composer/… Solo lee el repositorio
(con git en modo lectura) y escribe informes en output/system/.
"""

GITOPS_VERSION = "INF-003"
GITOPS_SCHEMA_VERSION = "0.1"

__all__ = ["GITOPS_VERSION", "GITOPS_SCHEMA_VERSION"]
