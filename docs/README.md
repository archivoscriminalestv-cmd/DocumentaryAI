# Documentation — DocumentaryAI

Punto de entrada a la organización documental del proyecto. Este documento es **organizativo**: no introduce arquitectura ni interpreta el dominio.

## Organización de `docs/`

| Carpeta | Contenido |
|---|---|
| `docs/architecture/` | Documentos de arquitectura (**ARCH-NNNN**), estándares, índices y material de arquitectura. |
| `docs/adr/` | Architecture Decision Records (**ADR-NNNN**). |
| `docs/rfc/` | Request for Comments (**RFC-NNNN**). |
| `docs/spec/` | Especificaciones (**SPEC-NNNN**). |
| `docs/governance/` | Documentación de gobernanza (p. ej. `PROJECT-CHARTER.md`). |
| `docs/research/` | Investigación y evidencia (fase Discovery; ver `docs/research/DISCOVERY-INDEX.md`). |

## Otras carpetas del repositorio

| Carpeta | Contenido |
|---|---|
| `templates/` | Plantillas oficiales por tipo (`architecture/`, `adr/`, `rfc/`, `spec/`). |
| `.github/` | Configuración de GitHub (plantillas de PR/issue, workflows). |
| `scripts/` | Scripts de automatización puntual. |
| `tools/` | Herramientas internas de desarrollo. |

## Tipos de documento

- **ARCH** — describe la arquitectura (componentes, relaciones, vistas).
- **ADR** — registra una decisión de arquitectura ya tomada (inmutable una vez aprobada).
- **RFC** — propuesta abierta a discusión (el "qué" y el "porqué").
- **SPEC** — especifica qué construir y cómo verificarlo.

## Reglas básicas

- El **repositorio es la única fuente de verdad** (ver `CONTRIBUTING.md`).
- **Ningún documento derivado puede adelantarse a su fuente normativa.**
- El front matter sigue `docs/architecture/Document-Header-Standard.md` (tabla Markdown, sin YAML).
- La numeración de identificadores la asigna el Principal Architect (secuencial, cuatro dígitos).

## Notas de estado (divergencias conocidas, sin resolver aquí)

> Observaciones descriptivas para el Principal Architect; este documento no las modifica.

- Existen ubicaciones heredadas anteriores a esta estructura: `docs/architecture/templates/` (plantillas previas) y `docs/architecture/ADR/` (carpeta previa con `.gitkeep`). Conviven con `templates/` y `docs/adr/`; su consolidación corresponde al Principal Architect.
- Índices existentes: `docs/architecture/Architecture-Index.md` (arquitectura) y `docs/research/DISCOVERY-INDEX.md` (investigación).
