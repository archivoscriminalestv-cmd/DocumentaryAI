# Architecture Audit — WP-0001

> Auditoría **solo de observación** de la documentación del proyecto DocumentaryAI.
> No modifica la arquitectura, no mueve archivos, no propone cambios de diseño del sistema.
> Fecha: 2026-06-27 · Alcance: carpeta `docs/`.

---

# Resumen

La documentación de DocumentaryAI se encuentra en una fase temprana y, en líneas generales, es **coherente con el estado del proyecto** (Fase 1 cerrada, Fase 2 sin iniciar). Existen dos cuerpos documentales claros:

1. **Documentación de gobierno** (`docs/DEVELOPMENT_GUIDE.md`, `docs/TEAM_CHARTER.md`): completa, sustancial y vigente.
2. **Documentación de arquitectura** (`docs/architecture/`): estructura recién creada, con todos sus archivos **vacíos** a la espera de la especificación oficial.

**No se han detectado enlaces rotos, documentos duplicados ni referencias circulares.** Los problemas encontrados son de **higiene y navegabilidad documental**, no de contenido contradictorio. El hallazgo más relevante es una **anomalía estructural**: `docs/PROJECT.md` es un *directorio* vacío en lugar de un archivo. El resto son documentos vacíos esperables, ausencia de índices/README y una nomenclatura mixta.

Inventario auditado:

| Ruta | Tipo | Tamaño | Estado |
|---|---|---|---|
| `docs/DEVELOPMENT_GUIDE.md` | Archivo | 4.265 B | Con contenido |
| `docs/TEAM_CHARTER.md` | Archivo | 2.733 B | Con contenido |
| `docs/VISION.md` | Archivo | 0 B | Vacío |
| `docs/PROJECT.md` | **Directorio** | — | Anomalía (vacío) |
| `docs/architecture/RFC-0001-Architecture.md` | Archivo | 0 B | Vacío (reservado) |
| `docs/architecture/glossary.md` | Archivo | 0 B | Vacío |
| `docs/architecture/ADR/.gitkeep` | Archivo | 0 B | Placeholder |
| `docs/architecture/diagrams/.gitkeep` | Archivo | 0 B | Placeholder |

---

# Hallazgos

## Críticos

### C-1 · `docs/PROJECT.md` es un directorio, no un archivo
`docs/PROJECT.md` existe como **directorio vacío**, pese a que su nombre (`.md`) indica que debería ser un documento Markdown. Es una anomalía estructural casi con certeza accidental.

- **Evidencia:** `find docs -mindepth 1` lista `docs/PROJECT.md` como `DIR`, sin contenido.
- **Por qué es crítico:** rompe la expectativa de cualquier persona o herramienta que intente abrir/enlazar `PROJECT.md` como archivo; puede provocar fallos silenciosos en generadores de documentación, índices automáticos o enlaces; y deja un "hueco" donde se esperaría documentación de proyecto.

## Importantes

### I-1 · Documentos clave vacíos (0 bytes)
`docs/VISION.md`, `docs/architecture/RFC-0001-Architecture.md` y `docs/architecture/glossary.md` están a 0 bytes.

- **Matiz:** `RFC-0001-Architecture.md` y `glossary.md` están vacíos **por diseño** (reservados para la especificación oficial del Arquitecto), por lo que su vacío es esperado a corto plazo. `VISION.md`, en cambio, lleva vacío desde el `Initial commit` y es el documento que daría contexto de producto.
- **Por qué importa:** archivos vacíos "aparentan existir" pero no aportan; cualquier futura referencia a ellos apuntaría a contenido inexistente, y dificultan distinguir "pendiente intencional" de "olvido".

### I-2 · No existe índice ni README en `docs/` ni en `docs/architecture/`
No hay ningún punto de entrada que enumere y describa los documentos.

- **Evidencia:** no existe `docs/README.md` ni `docs/architecture/README.md`; la búsqueda de enlaces Markdown (`](`) en todo `docs/` devuelve **cero** resultados.
- **Por qué importa:** sin índice, **todos los documentos son efectivamente huérfanos** (ninguno enlaza a otro de forma navegable). A medida que crezca `docs/architecture/` (RFC, ADR, diagramas, glosario), la falta de un índice hará difícil saber qué existe, su estado y cómo se relacionan.

### I-3 · Relación RFC ↔ ADR sin definir (riesgo de conflicto futuro)
Coexisten `RFC-0001-Architecture.md` y la carpeta `ADR/` (ambos vacíos), pero no hay ningún documento que establezca qué tipo de decisión vive en cada sitio, cómo se numeran ni cómo se referencian entre sí.

- **Por qué importa:** es el momento previo a que surja el conflicto clásico RFC/ADR/SPEC: solapamiento de responsabilidades (¿una decisión de arquitectura es una sección del RFC o un ADR independiente?), numeración divergente y referencias ambiguas. Hoy **no hay conflicto activo** porque están vacíos; el hallazgo es **preventivo**.

## Menores

### M-1 · Nomenclatura inconsistente entre documentos
Conviven tres convenciones de nombre:
- `UPPER_SNAKE_CASE`: `DEVELOPMENT_GUIDE.md`, `TEAM_CHARTER.md`, `VISION.md`.
- `Prefijo-Número-PascalCase`: `RFC-0001-Architecture.md`.
- `minúsculas`: `glossary.md`.

- **Por qué importa:** dificulta predecir nombres, ordenar y automatizar; es de bajo impacto ahora pero crece con el número de archivos.

### M-2 · Referencia en texto plano, no enlace navegable
`docs/TEAM_CHARTER.md:19` menciona `docs/DEVELOPMENT_GUIDE.md` como **texto plano**, no como enlace Markdown.

- **Matiz:** el archivo destino **existe**, por lo que **no es un enlace roto**; simplemente no es clicable/navegable.

### M-3 · Carpetas de placeholders sin documentar su propósito
`docs/architecture/ADR/` y `docs/architecture/diagrams/` contienen solo `.gitkeep`. El uso de `.gitkeep` para preservar carpetas vacías es correcto, pero su propósito no está documentado en ningún sitio.

- **Por qué importa:** un nuevo colaborador no sabe qué debe ir en cada carpeta ni con qué formato/convención.

### M-4 · Desfase entre documentación y control de versiones
Varios documentos de `docs/` no están versionados todavía: `DEVELOPMENT_GUIDE.md`, `TEAM_CHARTER.md` y toda `docs/architecture/` figuran como *untracked*.

- **Matiz:** es una **decisión consciente** de arquitectura (pendiente de cuándo commitearlos), no un error. Se documenta solo por coherencia de la auditoría: el estado "en disco" y el estado "versionado" divergen actualmente.

---

# Recomendaciones

> Solo documentación de observaciones. **No se implementa ninguna** de estas recomendaciones en este Work Package. Ninguna altera la arquitectura ni el diseño del sistema.

### R-1 · Resolver la anomalía de `docs/PROJECT.md` (ref. C-1)
- **Problema:** `docs/PROJECT.md` es un directorio vacío con nombre de archivo Markdown.
- **Impacto:** confusión y posibles fallos en herramientas/enlaces; hueco de documentación inesperado.
- **Recomendación:** decidir deliberadamente su destino — eliminar el directorio si fue accidental, o sustituirlo por un archivo `PROJECT.md` real si se pretendía un documento de proyecto. (Acción fuera de alcance de este WP, que prohíbe eliminar/mover; requiere instrucción explícita posterior.)

### R-2 · Definir el estado de los documentos vacíos (ref. I-1)
- **Problema:** documentos a 0 bytes sin marca de estado.
- **Impacto:** no se distingue "pendiente intencional" de "olvido"; referencias futuras a contenido inexistente.
- **Recomendación:** cuando se decida darles contenido, registrar su estado de forma explícita (p. ej., una nota de "borrador/reservado" dentro del propio archivo o en el índice). Para `VISION.md`, decidir si se redacta o se mantiene vacío de forma documentada.

### R-3 · Crear un índice/README de documentación (ref. I-2)
- **Problema:** no hay punto de entrada ni navegación entre documentos.
- **Impacto:** documentos huérfanos; dificultad creciente para descubrir y relacionar la documentación según crezca.
- **Recomendación:** prever un `docs/README.md` (y/o `docs/architecture/README.md`) que liste cada documento, su propósito y su estado. (Creación fuera de alcance de este WP.)

### R-4 · Establecer una política RFC/ADR antes de poblar `docs/architecture/` (ref. I-3)
- **Problema:** no está definida la relación, responsabilidad y numeración entre RFC y ADR.
- **Impacto:** futuro solapamiento y referencias ambiguas entre RFC, ADR (y posibles SPEC).
- **Recomendación:** que el Arquitecto fije, en la especificación oficial, qué contiene un RFC frente a un ADR, su numeración y cómo se enlazan. (Es una decisión de gobierno documental que corresponde al Arquitecto; aquí solo se señala.)

### R-5 · Unificar la convención de nomenclatura (ref. M-1)
- **Problema:** tres estilos de nombre coexisten.
- **Impacto:** menor predictibilidad y automatización; crece con el número de archivos.
- **Recomendación:** acordar una convención única para la documentación y aplicarla a los archivos nuevos (sin renombrar los existentes, que está fuera de alcance de este WP).

### R-6 · Convertir referencias de ruta en enlaces navegables (ref. M-2)
- **Problema:** la referencia a `DEVELOPMENT_GUIDE.md` es texto plano.
- **Impacto:** menor navegabilidad (no es un enlace roto).
- **Recomendación:** cuando se editen esos documentos, expresar las referencias entre documentos como enlaces Markdown relativos.

### R-7 · Documentar el propósito de las carpetas de placeholders (ref. M-3)
- **Problema:** `ADR/` y `diagrams/` no explican qué contienen ni con qué convención.
- **Impacto:** ambigüedad para nuevos colaboradores.
- **Recomendación:** describir el propósito de cada carpeta en el futuro índice/README de `docs/architecture/`.

### R-8 · Alinear documentación y versionado (ref. M-4)
- **Problema:** documentos relevantes sin commitear.
- **Impacto:** divergencia entre el estado en disco y el versionado; riesgo de pérdida.
- **Recomendación:** decidir explícitamente el momento de versionar `DEVELOPMENT_GUIDE.md`, `TEAM_CHARTER.md` y `docs/architecture/` (decisión del Director/Arquitecto; no se ejecuta aquí).

---

_Fin del informe. Este documento es exclusivamente de observación; no implementa ninguna recomendación ni modifica la arquitectura del sistema._
