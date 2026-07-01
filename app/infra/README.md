# INFRA — Infrastructure Protection & Backup Foundation (INF-001)

Subsistema **independiente** cuyo único objetivo es que DocumentaryAI **sobreviva** a un fallo de
disco, una reinstalación de Windows, un cambio de ordenador, una corrupción o un error humano.

**No** genera contenido, **no** modifica ningún motor, **no** sube nada a Internet, **no** usa
Git ni conoce GitHub. Solo **prepara la infraestructura de protección**: describe qué copiar, qué
no copiar, qué conocimiento existe, qué estado tiene el proyecto y si está listo para un backup.
Solo lectura del proyecto; escribe únicamente en `output/system/`. Determinista.

## Filosofía

> El conocimiento es permanente; los binarios temporales son desechables.

Nunca se respaldan renders, workspaces ni descargas. El conocimiento (`knowledge/`), el código
(`app/`), la arquitectura (`docs/`) y las pruebas (`tests/`) son lo que **nunca** debe perderse.

## Qué produce

- **Project Manifest** — identidad determinista del proyecto: versión, fecha (inyectada), schema,
  motores, ADR/RFC/SPEC, nº de subsistemas/tests/capacidades, documentales aprendidos, planos,
  escenas, horas, tamaño de `knowledge/` y del proyecto, y **SHA256** de todos los artefactos
  críticos (configs, estilos de conocimiento, todos los ADR/RFC/SPEC).
- **Knowledge Snapshot** — estado completo del conocimiento (estadísticas + estilos + nº de
  documentales + hashes de estilos). Nunca vídeos, nunca output.
- **Project Snapshot** — fotografía que responde *"¿cómo era DocumentaryAI el día X?"* (compone
  todo lo anterior + integridad + restauración + salud + `ready_for_backup`).
- **Integrity Report** — carpetas críticas inexistentes, archivos faltantes, documentación
  perdida, conocimiento corrupto y (con un manifiesto previo) **hashes distintos**.
- **Backup Plan** — clasificación exacta de qué respaldar:
  - `CRITICAL` (nunca perder): `app/`, `docs/`, `knowledge/`, `tests/`, `config/`, `pyproject.toml`…
  - `IMPORTANT` (recomendado): `output/dca`, `output/kbg`, `output/system`, `output/narrative`,
    `output/eae`, `output/projects`, `datasets/`, `assets/`…
  - `TEMPORARY` (nunca copiar): `cache/`, `workspace/`, `downloads/`, `render/`, `tmp/`, `outputs/`…
- **Restore Plan** — pasos ordenados para reconstruir el proyecto desde un backup, sin restaurar
  binarios temporales.

## Módulos

`models.py`, `manifest.py` (+ helpers de FS: hash/sizes/recuentos), `knowledge_snapshot.py`,
`project_snapshot.py`, `integrity.py`, `backup_manager.py`, `restore.py`, `persistence.py`
(escribe en `output/system/`, rechaza `knowledge/`).

## CLIs

```bash
python -m app.cli.project_status      # estado legible (versión/arquitectura/conocimiento/integridad/backup)
python -m app.cli.project_snapshot    # genera los 6 JSON en output/system/
```

`project_snapshot` escribe: `project_manifest.json`, `knowledge_snapshot.json`,
`project_snapshot.json`, `backup_plan.json`, `integrity_report.json`, `restore_plan.json`.

## Determinismo

Todo es reproducible dado el mismo árbol de proyecto. La única entrada variable —la fecha— se
**inyecta** (`as_of`); el núcleo no usa `datetime` (lo aporta la CLI). Hashes y listados se
ordenan y las rutas se normalizan a POSIX.

Ver `docs/adr/ADR-0028-Infrastructure-Protection.md`.
