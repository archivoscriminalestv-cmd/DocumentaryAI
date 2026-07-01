# REPOSITORY STRUCTURE AUDIT — DocumentaryAI (DS-0002)

| Campo | Valor |
|---|---|
| **Document ID** | ARCH-REPO-STRUCTURE-AUDIT |
| **Title** | Repository Structure Audit — DocumentaryAI |
| **Status** | Draft (audit) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | `CONTRIBUTING.md`, `docs/README.md`, `docs/architecture/Architecture-Index.md`, `docs/architecture/Document-Header-Standard.md` |

> **Documento de auditoría, exclusivamente descriptivo.** Inventaria la estructura actual y detecta divergencias para preparar una futura consolidación.
> **No** mueve, renombra ni modifica archivos; **no** crea arquitectura nueva; **no** interpreta el dominio. Las recomendaciones son observaciones, no acciones ejecutadas.
> Estado observado: 2026-06-28.

---

## 1. Inventario de la estructura actual

```
(raíz)
├── .github/               (vacío salvo .gitkeep)
├── .gitignore
├── CONTRIBUTING.md
├── pyproject.toml
├── main.py
├── app/                   (código: app.py, ui.py, project_manager.py, __init__.py)
├── config/                (settings.py, __init__.py)
├── scripts/               (vacío salvo .gitkeep)
├── tools/                 (vacío salvo .gitkeep)
├── templates/             (DS-0001)
│   ├── architecture/ARCH-template.md
│   ├── adr/ADR-template.md
│   ├── rfc/RFC-template.md
│   └── spec/SPEC-template.md
├── docs/
│   ├── README.md
│   ├── DEVELOPMENT_GUIDE.md
│   ├── TEAM_CHARTER.md
│   ├── VISION.md          (0 bytes)
│   ├── PROJECT.md         (⚠️ es un DIRECTORIO vacío, no un archivo)
│   ├── adr/               (DS-0001; vacío salvo .gitkeep)
│   ├── rfc/               (DS-0001; vacío salvo .gitkeep)
│   ├── spec/              (DS-0001; vacío salvo .gitkeep)
│   ├── governance/PROJECT-CHARTER.md
│   ├── research/          (10 documentos WP-0009…WP-0018 + índices)
│   └── architecture/
│       ├── ARCH-0002-Domain-Philosophy.md
│       ├── RFC-0001-Architecture.md          (0 bytes)
│       ├── Architecture-Index.md
│       ├── Architecture-Audit.md
│       ├── Document-Header-Standard.md
│       ├── Documentation-Linter-Design.md
│       ├── Evidence-Centric-Domain-Research.md
│       ├── Repository-Structure-Proposal.md
│       ├── glossary.md                        (0 bytes)
│       ├── ADR/           (WP-0002; vacío salvo .gitkeep)
│       ├── diagrams/      (vacío salvo .gitkeep)
│       └── templates/     (WP-0002: ARCH/ADR/RFC/SPEC/Review-template.md)
├── Agents/                (⚠️ vacío; fuera de la estructura documentada)
├── prompts/               (⚠️ vacío; fuera de la estructura documentada)
├── outputs/               (⚠️ vacío; fuera de la estructura documentada)
├── projects/Fago/         (⚠️ árbol de trabajo: 01_sources … 10_video; fuera de la estructura documentada)
└── __pycache__/, app/__pycache__/, config/__pycache__/   (artefactos; ignorados por .gitignore)
```

Notas de versionado: los `.pyc` **no** están rastreados por git (`.gitignore` activo). Casi toda la documentación (`docs/`, `templates/`, `CONTRIBUTING.md`, etc.) figura como *untracked* (pendiente de versionar por decisión de gobernanza).

---

## 2. Directorios duplicados o solapados

| # | Caso | Ubicación A | Ubicación B | Observación |
|---|---|---|---|---|
| D-1 | **Plantillas** | `templates/` (DS-0001) | `docs/architecture/templates/` (WP-0002) | Dos hogares de plantillas coexistiendo. |
| D-2 | **ADR** | `docs/adr/` (DS-0001) | `docs/architecture/ADR/` (WP-0002) | Dos hogares de ADR; además difieren en mayúsculas (ver §4). |
| D-3 | **Directorios fuera de la estructura documentada** | `Agents/`, `prompts/`, `outputs/`, `projects/` | — | No definidos en DS-0001 (`docs/`, `templates/`, `.github/`, `scripts/`, `tools/`); vacíos salvo `projects/Fago/` (árbol de trabajo). |
| D-4 | **Índices** | `docs/architecture/Architecture-Index.md` | `docs/research/DISCOVERY-INDEX.md` | No están duplicados (alcances distintos), pero coexisten dos índices; se anota por claridad. |

> `projects/Fago/` coincide con `config/settings.py: PROJECT_NAME = "Fago"`; aparenta ser un **área de trabajo** de la app, no documentación. Constatación descriptiva.

---

## 3. Plantillas duplicadas

| Plantilla | `templates/…` (DS-0001) | `docs/architecture/templates/…` (WP-0002) | Diferencias observadas |
|---|:--:|:--:|---|
| ARCH | ✓ | ✓ | DS-0001: minimalista (secciones vacías + reglas en comentario). WP-0002: con comentarios explicativos por sección. |
| ADR | ✓ | ✓ | Ídem. |
| RFC | ✓ | ✓ | Ídem. |
| SPEC | ✓ | ✓ | Ídem. |
| Review | ✗ | ✓ | Solo existe en WP-0002; no hay equivalente en `templates/`. |

Resultado: **4 plantillas duplicadas** (ARCH/ADR/RFC/SPEC) con formato divergente y **1 plantilla huérfana** (Review) presente solo en la ubicación heredada.

---

## 4. Convenciones inconsistentes

- **Mayúsculas/minúsculas en carpetas:** `docs/architecture/ADR/` (mayúsculas) vs `docs/adr/` (minúsculas). En sistemas de archivos insensibles a mayúsculas (Windows) esto es especialmente delicado.
- **Ubicación de plantillas:** raíz `templates/` vs `docs/architecture/templates/` (ver §2/§3).
- **Formato de cabecera (front matter) divergente:**
  - `Document-Header-Standard.md` define **10 campos** en tabla Markdown.
  - `PROJECT-CHARTER.md` y los documentos de `docs/research/` usan esa tabla de 10 campos.
  - `ARCH-0002-Domain-Philosophy.md` usa una **cabecera ligera** (Status/Owner/Version/Created/Depends On), no la tabla de 10 campos.
- **Nomenclatura de archivos heterogénea:**
  - UPPER-KEBAB: `DOMAIN-ONTOLOGY-RESEARCH.md`, `MVP-CAPABILITY-INVENTORY.md`.
  - Mixed-Kebab: `Architecture-Index.md`, `Evidence-Centric-Domain-Research.md`, `Document-Header-Standard.md`.
  - Prefijo+número: `ARCH-0002-Domain-Philosophy.md`, `RFC-0001-Architecture.md`.
- **Anomalía de tipo:** `docs/PROJECT.md` es un **directorio** con nombre de archivo `.md` (ya señalado en `Architecture-Audit.md`).
- **Directorios vacíos sin preservación uniforme:** unos usan `.gitkeep` (`docs/adr`, `.github`, etc.); `Agents/`, `prompts/`, `outputs/` están vacíos **sin** `.gitkeep` (no se versionarían).

---

## 5. Referencias rotas o potencialmente rotas

- **`docs/architecture/README.md`** — referenciado (como recomendación) en documentos previos, pero **no existe**. No es un enlace activo roto, pero sí una referencia a un documento ausente.
- **`docs/PROJECT.md`** — referenciado como ruta de archivo en varios documentos, pero es un **directorio vacío**: cualquier intento de abrirlo como documento fallaría.
- **Referencias como texto/código, no como enlaces:** las rutas entre documentos se escriben en *inline code* (p. ej. `` `docs/...` ``), no como enlaces Markdown navegables (constatado también en auditorías previas). No hay rotura, pero no hay navegabilidad.
- **Índice potencialmente desactualizado:** `Architecture-Index.md` se creó antes de DS-0001/ARCH-0002 y **no** referencia `templates/` (raíz), `docs/adr|rfc|spec/`, `ARCH-0002-Domain-Philosophy.md` ni este audit. No es un enlace roto, pero el índice no refleja la estructura actual. *(Constatación; no se modifica.)*
- **Plantillas nuevas → estándar de cabecera:** las plantillas de `templates/` referencian `docs/architecture/Document-Header-Standard.md`, que **sí existe** (referencia válida).

---

## 6. Riesgos de reorganización

- **Rotura de referencias por consolidación de plantillas/ADR:** mover o unificar `docs/architecture/templates/` → `templates/` o `docs/architecture/ADR/` → `docs/adr/` puede invalidar referencias que apunten a las rutas heredadas.
- **Renombrado solo-de-mayúsculas en Windows:** `ADR/` → `adr/` puede no detectarse por Git en sistemas insensibles a mayúsculas; requiere procedimiento explícito (rename en dos pasos) y verificación.
- **Directorios de trabajo de la app:** `projects/Fago/`, `outputs/`, `prompts/`, `Agents/` podrían ser **generados o usados por la app** (relación con `PROJECT_NAME="Fago"`); moverlos/eliminarlos podría afectar a la ejecución. Conviene confirmar su origen antes de tocarlos.
- **Pérdida de carpetas vacías:** al versionar, `Agents/`, `prompts/`, `outputs/` (sin `.gitkeep`) se perderían si no se añade marcador o se ignoran deliberadamente.
- **Plantilla Review huérfana:** consolidar plantillas sin decidir el destino de `Review-template.md` la dejaría fuera.
- **Divergencia de cabeceras:** unificar el front matter implica decidir entre el estándar de 10 campos y la cabecera ligera de ARCH-0002; afecta a documentos ya aprobados (no deben modificarse sin instrucción).
- **`.gitignore`:** `Agents/`, `prompts/`, `outputs/`, `projects/` no están listados; cualquier decisión de versionarlos o ignorarlos debe ser explícita.

---

## 7. Recomendación de consolidación

> Recomendaciones **descriptivas** para el Principal Architect. No se ejecutan aquí (mover/renombrar/modificar está fuera del alcance de este documento).

1. **Plantillas — hogar único:** designar `templates/` (DS-0001) como ubicación canónica y **deprecar** `docs/architecture/templates/`; decidir el destino de `Review-template.md` (incorporarla como `templates/review/` o descartarla).
2. **ADR — hogar único:** designar `docs/adr/` como canónico y deprecar `docs/architecture/ADR/`; resolver el conflicto de mayúsculas con un renombrado controlado.
3. **Directorios fuera de estructura:** decidir el papel de `Agents/`, `prompts/`, `outputs/`, `projects/` — si son áreas de **trabajo/runtime**, añadirlas a `.gitignore` y documentarlas; si son estructura permanente, integrarlas en la estructura oficial y documentarlas en `docs/README.md`.
4. **Anomalía `docs/PROJECT.md`:** resolver el directorio vacío con nombre `.md` (eliminar o convertir en archivo), de forma deliberada.
5. **Estándar de cabecera:** reconciliar el front matter (estándar de 10 campos vs cabecera ligera de ARCH-0002) y fijar uno único en `Document-Header-Standard.md`.
6. **Nomenclatura:** adoptar una convención de nombres única para documentos nuevos (sin renombrar los existentes salvo decisión expresa).
7. **Índices:** actualizar `Architecture-Index.md` para reflejar la estructura actual (DS-0001, ARCH-0002, este audit) y aclarar su relación con `DISCOVERY-INDEX.md`.
8. **Navegabilidad:** si se desea, convertir las referencias de ruta en enlaces Markdown relativos.
9. **Secuencia segura:** ejecutar la consolidación en pasos pequeños, cada uno como WP propio aprobado, verificando referencias tras cada paso y cuidando el historial de Git.

> Estas recomendaciones requieren acciones que **mueven/renombran/modifican** archivos; por tanto, quedan sujetas a aprobación explícita del Principal Architect en un Work Package posterior.

---

_Fin de la auditoría. Documento exclusivamente descriptivo: no mueve, renombra ni modifica archivos, no crea arquitectura nueva y no interpreta el dominio._
