# ADR-0028 — Infrastructure Protection & Backup Foundation

- **Status:** Accepted
- **Date:** 2026-07-01
- **Sprint:** INF-001
- **Nota de numeración:** el sprint pedía "ADR-0027", pero ese número ya lo ocupa el Architectural
  Backlog (DCA-004). Para no sobrescribir una decisión existente, esta ADR usa **0028**.
- **Relates:** ADR-0010 (DLE storage policy), ADR-0016 (EAE workspace temporal), ADR-0020 (DCA),
  ADR-0027 (Architectural Backlog)

## Contexto

DocumentaryAI ha crecido hasta el punto de que **perderlo es un riesgo crítico**. Debe poder
sobrevivir a un fallo de disco, una reinstalación de Windows, un cambio de ordenador, una
corrupción o un error humano. Hasta hoy no existía forma automática de saber qué hay que
proteger, qué estado tiene el proyecto ni si está listo para un backup.

## Decisión 1 — Un subsistema independiente, solo de preparación

Se crea `app/infra/` como subsistema **aislado y aditivo**. **No** genera contenido, **no**
modifica ningún motor, **no** sube nada a Internet, **no** usa Git ni conoce GitHub. Solo
**prepara** la infraestructura de protección y solo **lee** el proyecto; escribe únicamente en
`output/system/`. El acto físico de copiar/subir es externo y humano.

## Decisión 2 — El conocimiento es permanente; los binarios temporales son desechables

El backup se clasifica en tres niveles deterministas: **CRITICAL** (nunca perder: `app/`,
`docs/`, `knowledge/`, `tests/`, `config/`, manifiestos de paquete…), **IMPORTANT** (recomendado:
artefactos derivados auditables como `output/dca`, `output/kbg`, `output/system`,
`output/narrative`, `output/eae`, `output/projects`, `datasets/`, `assets/`) y **TEMPORARY**
(nunca copiar: `cache/`, `workspace/`, `downloads/`, `render/`, `tmp/`, `outputs/`,
`__pycache__/`). Coherente con ADR-0010 (DLE) y ADR-0016 (EAE): el binario es un medio, el
conocimiento es la verdad. Nunca se respaldan renders, workspaces ni descargas.

## Decisión 3 — Estado reproducible y auditable

`app/infra/` produce seis artefactos en `output/system/`: **project_manifest** (identidad +
SHA256 de todos los artefactos críticos), **knowledge_snapshot** (solo conocimiento, nunca
vídeos/output), **project_snapshot** (la fotografía que responde "¿cómo era el día X?"),
**backup_plan**, **integrity_report** y **restore_plan**. Todo es determinista dado el mismo
árbol; la única entrada variable —la fecha— se **inyecta** (el núcleo no usa `datetime`; lo
aporta la CLI). Hashes y listas se ordenan; las rutas se normalizan a POSIX.

## Decisión 4 — Integridad comprobable, restauración planificable

El **Integrity Checker** detecta carpetas críticas inexistentes, archivos faltantes,
documentación perdida, conocimiento corrupto (JSON ilegible) y, contra un manifiesto previo,
**hashes distintos**. El **Restore Plan** describe los pasos ordenados para reconstruir el
proyecto desde un backup **sin** restaurar binarios temporales.

## Decisión 5 — CLIs de cara al desarrollador

`python -m app.cli.project_status` (estado legible: versión, arquitectura, conocimiento,
integridad, backups, carpetas críticas, archivos faltantes, salud, listo-para-backup) y
`python -m app.cli.project_snapshot` (genera los seis JSON).

## Consecuencias

- **Positivo:** DocumentaryAI puede "mudarse" a otro ordenador en cualquier momento; el estado es
  reproducible y auditable; el backup es determinista y sabe exactamente qué incluir y qué excluir;
  cero riesgo para el pipeline (solo lectura + `output/system/`). Criterio de aceptación cumplido:
  el proyecto responde automáticamente qué copiar, qué no, qué conocimiento/motores/documentación
  existe, qué salud tiene y si está listo para un backup.
- **Limitaciones aceptadas:** el subsistema **no ejecuta** la copia ni la restauración (las
  planifica); no comprime ni cifra; no integra almacenamiento remoto (por diseño: nada de red/Git).
  La clasificación de `library/`/`assets/` como IMPORTANT (binarios permanentes) queda a criterio
  del usuario.
```
=============================
DOCUMENTARYAI PROJECT STATUS  (prueba real INF-001)
  subsistemas: 32 · capacidades: 26 · ADR: 27 · tests: 744
  conocimiento: 97 documentales · 31.884 planos · 49,1 h · 26,6 MB
  integridad: OK · backup CRITICAL 29,1 MB + IMPORTANT 28,6 MB · listo: SÍ
=============================
```
