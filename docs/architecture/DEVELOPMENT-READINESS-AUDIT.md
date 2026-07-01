# DEVELOPMENT READINESS AUDIT — DocumentaryAI (DS-0008)

| Campo | Valor |
|---|---|
| **Document ID** | ARCH-DEV-READINESS-AUDIT |
| **Title** | Development Readiness Audit — DocumentaryAI |
| **Status** | Draft (audit) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | `pyproject.toml`, `docs/architecture/REPOSITORY-STRUCTURE-AUDIT.md`, `docs/architecture/Architecture-Index.md` |

> **Auditoría, exclusivamente descriptiva.** Evalúa la **capacidad real para empezar a implementar el MVP**, no el dominio ni la arquitectura.
> **No** propone soluciones, **no** modifica el repositorio, **no** crea otros archivos y **no** diseña arquitectura técnica. Solo audita el estado a 2026-06-28.

---

## 1. Estructura actual del repositorio (vista de implementación)

```
(raíz)
├── main.py                 # entry point (CLI)
├── app/                    # app.py, ui.py, project_manager.py, __init__.py
├── config/                 # settings.py, __init__.py
├── pyproject.toml          # config de Black/Ruff/mypy/pytest
├── .gitignore
├── CONTRIBUTING.md
├── docs/                   # documentación (architecture, research, spec, governance, adr, rfc)
├── templates/              # plantillas de documentación
├── scripts/  tools/  .github/   # solo .gitkeep (vacíos)
├── Agents/ prompts/ outputs/     # vacíos, fuera de la estructura documentada
├── projects/Fago/                # árbol de trabajo (01_sources … 10_video)
└── __pycache__/ (+ app/, config/)  # artefactos (ignorados por .gitignore)
```

---

## 2. Elementos presentes

- **Código fuente mínimo:** `main.py` + `app/` (CLI: `app.py`, `ui.py`, `project_manager.py`) + `config/settings.py`. Aplicación de consola que arranca.
- **Configuración de calidad:** `pyproject.toml` con secciones para **Black, Ruff, mypy y pytest** (`requires-python = ">=3.11"`).
- **Higiene de repo:** `.gitignore` (Python) presente; sin `.pyc` rastreados.
- **Intérprete:** **Python 3.14.6** disponible; `pip` disponible.
- **Documentación abundante:** arquitectura, investigación (Discovery), gobernanza, esqueletos de SPEC (SPEC-0001, scaffolding del módulo Research), plantillas.
- **Convenciones documentales:** estándar de cabecera, índice, CONTRIBUTING, estructura `docs/`.
- **Estructura de carpetas técnicas creada (vacía):** `scripts/`, `tools/`, `.github/`.

---

## 3. Elementos ausentes necesarios para comenzar el desarrollo

> Constatación de ausencias; sin proponer cómo resolverlas.

- **Herramientas de desarrollo no instaladas:** Black, Ruff, mypy y pytest **no están instalados** (solo configurados). No es posible ejecutar lint/format/type-check/test.
- **Sin carpeta de pruebas:** no existe `tests/`; no hay arnés de testing.
- **Sin declaración de dependencias del proyecto:** `pyproject.toml` **no declara `dependencies`** ni `[build-system]`; no hay `requirements*.txt` ni lockfile (`poetry.lock`/`uv.lock`/`Pipfile`).
- **Sin entorno virtual** en el repositorio (`.venv`/`venv`/`env`).
- **Sin CI:** `.github/` solo contiene `.gitkeep` (sin workflows).
- **Sin fuente normativa de dominio implementable:** **RFC-0002 (Domain Model) no existe**; SPEC-0001 y el scaffolding del módulo Research son **esqueletos** (sin contenido). No hay especificación completa contra la que implementar el dominio.
- **Sin código de dominio/módulos del MVP:** solo existe el esqueleto CLI heredado; no hay `core/`/módulos del MVP.

---

## 4. Convenciones existentes

- **Estilo de código:** PEP 8 y type hints aplicados en el código actual (Fase 1); Black/Ruff/mypy configurados en `pyproject.toml` (line-length 88, target py311).
- **Pruebas:** pytest configurado con `testpaths = ["tests"]` (carpeta aún inexistente).
- **Documentación:** estándar de cabecera (tabla Markdown, sin YAML), numeración `TIPO-NNNN`, estructura `docs/{architecture,adr,rfc,spec,governance,research}` y `templates/`.
- **Flujo de trabajo:** `CONTRIBUTING.md` (Architect decide / Claude implementa / repositorio como fuente de verdad / no adelantarse a la fuente normativa).
- **Git:** cambios pequeños y coherentes (gobernanza); gran parte de la documentación aún *untracked*.

---

## 5. Riesgos técnicos detectados

- **Python 3.14 muy reciente:** posible incompatibilidad o falta de soporte estable de algunas herramientas/dependencias; `pyproject` declara `>=3.11`, pero el intérprete instalado es 3.14.6 (divergencia de versión objetivo).
- **Tooling configurado pero no instalado:** la configuración de calidad no está verificada en ejecución (riesgo de config que no corresponde a versiones reales).
- **Dependencias no fijadas:** sin `dependencies`/lockfile, la reproducibilidad del entorno no está garantizada.
- **Sin `[build-system]`:** el proyecto no es instalable/empaquetable como paquete en su estado actual.
- **Ausencia de pruebas:** no hay red de seguridad para cambios.
- **Directorios fuera de estructura sin versionar** (`Agents/`, `prompts/`, `outputs/`, `projects/Fago/`) y **anomalía `docs/PROJECT.md`** (directorio): pueden afectar a herramientas/build (también señalados en `REPOSITORY-STRUCTURE-AUDIT.md`).
- **Documentación mayoritariamente *untracked*:** el estado en disco diverge del versionado.

---

## 6. Bloqueos reales para comenzar a implementar

> Bloqueos efectivos (constatación, no resolución).

1. **Sin RFC-0002 (Domain Model):** no hay modelo de dominio aprobado ni comandos/invariantes especificados; SPEC-0001 y el scaffolding son esqueletos. **No hay especificación implementable del dominio.** (Bloqueo de dominio/spec, no de entorno.)
2. **Herramientas de desarrollo no instaladas:** sin Black/Ruff/mypy/pytest operativos no puede ejecutarse el ciclo de calidad/test. (Bloqueo de entorno.)
3. **Sin dependencias declaradas ni entorno reproducible:** no hay forma definida de instalar el conjunto de librerías del MVP. (Bloqueo de entorno.)
4. **Sin carpeta/arnés de pruebas:** no es posible validar implementación mediante tests. (Bloqueo de entorno.)

> Observación: los bloqueos 2–4 son de **entorno**; el bloqueo 1 es de **especificación** (precede a cualquier implementación de dominio, conforme a la regla "ningún documento derivado puede adelantarse a su fuente normativa").

---

## 7. Checklist de preparación (estado actual)

> Estado observado, **sin** acciones propuestas.

| # | Ítem | Estado |
|---|---|---|
| 1 | Intérprete Python disponible | ✅ Presente (3.14.6) |
| 2 | `pip` disponible | ✅ Presente |
| 3 | Configuración de calidad (Black/Ruff/mypy/pytest) en `pyproject.toml` | ✅ Presente |
| 4 | Herramientas de calidad instaladas | ❌ Ausente |
| 5 | Dependencias del proyecto declaradas (`dependencies`/lockfile) | ❌ Ausente |
| 6 | `[build-system]` (proyecto instalable) | ❌ Ausente |
| 7 | Entorno virtual | ❌ Ausente |
| 8 | Carpeta/arnés de pruebas (`tests/`) | ❌ Ausente |
| 9 | CI configurado (`.github/`) | ❌ Ausente (solo `.gitkeep`) |
| 10 | `.gitignore` adecuado | ✅ Presente |
| 11 | Estructura documental y convenciones | ✅ Presente |
| 12 | Fuente normativa de dominio (RFC-0002) | ❌ Ausente |
| 13 | SPEC implementable completa (SPEC-0001 con contenido) | ❌ Ausente (esqueleto) |
| 14 | Código de módulos del MVP | ❌ Ausente (solo esqueleto CLI heredado) |
| 15 | Estructura de carpetas técnicas (`scripts/`, `tools/`, `.github/`) | ⚠️ Presente pero vacía |
| 16 | Repositorio sin divergencias estructurales | ⚠️ Con divergencias (ver `REPOSITORY-STRUCTURE-AUDIT.md`) |

Resumen: **5 ítems presentes**, **9 ausentes**, **2 parciales**.

---

## 8. Observaciones (descriptivas)

- Desde el punto de vista de **entorno**, faltan los elementos básicos para desarrollar y validar (tooling instalado, dependencias, tests, CI).
- Desde el punto de vista de **especificación**, la implementación del dominio está bloqueada por la ausencia de **RFC-0002** (SPEC-0001 y el scaffolding son esqueletos).
- La **documentación está madura**; el **entorno técnico** y la **especificación de dominio**, no.
- Todo es constatación del estado actual; **no** se proponen soluciones ni se modifica el repositorio.

---

_Fin de la auditoría. Documento exclusivamente descriptivo del estado de preparación para implementar: no propone soluciones, no modifica el repositorio, no crea otros archivos y no diseña arquitectura técnica._
