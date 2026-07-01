# Document Header Standard

> Estándar de cabecera documental (front matter en Markdown) para los documentos oficiales de DocumentaryAI.
> Este documento define **el estándar**, no valores concretos. No define estados oficiales ni workflow documental: eso corresponde al Arquitecto.

---

## Propósito

Todos los documentos oficiales del proyecto (RFC, ADR, ARCH, SPEC y Reviews) deben comenzar con una **cabecera homogénea** que identifique el documento y sus metadatos clave de forma uniforme.

Objetivos del estándar:

- **Homogeneidad:** todas las cabeceras tienen los mismos campos, en el mismo orden y formato.
- **Legibilidad directa en GitHub:** se usa una tabla Markdown, que GitHub renderiza de forma nativa (a diferencia del YAML front matter, que GitHub muestra como texto crudo o lo oculta).
- **Trazabilidad:** los campos permiten saber quién es responsable de cada documento, su versión y con qué otros documentos se relaciona.

Este estándar describe **qué campos existen y qué significan**. No fija qué valores son válidos, ni el ciclo de vida de los documentos.

---

## Formato

### Reglas

1. La cabecera es lo **primero** del documento, justo después del título de primer nivel (`# Título`).
2. Se expresa como una **tabla Markdown de dos columnas**: `Campo | Valor`.
3. **No se usa YAML Front Matter** (`---` con pares `clave: valor`). El formato es exclusivamente Markdown.
4. Los **diez campos** del estándar aparecen **siempre**, en el **orden** indicado más abajo. Si un campo no aplica todavía, se deja explícitamente vacío o con un marcador (p. ej. `—`), pero **no se omite la fila**.
5. Los nombres de campo se escriben **en inglés** y **en negrita**, tal como se listan en este estándar.

### Esqueleto reutilizable

<!-- Plantilla de cabecera. Los valores entre <...> son marcadores de posición, no valores concretos. -->

```markdown
# <Título del documento>

| Campo | Valor |
|---|---|
| **Document ID** | <...> |
| **Title** | <...> |
| **Status** | <...> |
| **Version** | <...> |
| **Author** | <...> |
| **Created** | <...> |
| **Last Updated** | <...> |
| **Owner** | <...> |
| **Reviewers** | <...> |
| **Related Documents** | <...> |
```

> El bloque anterior es solo el **formato**. Este estándar no asigna valores concretos a ningún campo.

---

## Significado de cada campo

| Campo | Significado | Notas de formato |
|---|---|---|
| **Document ID** | Identificador único del documento dentro del proyecto. Permite referenciarlo de forma inequívoca desde otros documentos. | El esquema de identificadores (prefijos, numeración) lo define el Arquitecto; queda fuera de este estándar. |
| **Title** | Título legible y descriptivo del documento. Puede coincidir con el título de primer nivel (`#`). | Texto libre, breve y claro. |
| **Status** | Estado actual del documento en su ciclo de vida. | El **catálogo de estados válidos** y su workflow **NO** se definen aquí; los establece el Arquitecto. Este estándar solo reserva el campo. |
| **Version** | Versión del documento, para distinguir revisiones sucesivas. | El esquema de versionado (p. ej. incremental o semántico) lo decide el Arquitecto. |
| **Author** | Persona o rol que ha redactado el documento. | Puede ser uno o varios. |
| **Created** | Fecha de creación del documento. | Recomendado un formato de fecha único y no ambiguo (p. ej. `YYYY-MM-DD`); la convención exacta la fija el Arquitecto. |
| **Last Updated** | Fecha de la última modificación relevante. | Mismo formato de fecha que `Created`. |
| **Owner** | Responsable actual del documento (quién decide sobre su contenido y mantenimiento). Puede diferir del autor original. | Persona o rol. |
| **Reviewers** | Personas o roles encargados de revisar/aprobar el documento. | Uno o varios; puede quedar vacío si aún no hay revisores asignados. |
| **Related Documents** | Referencias a otros documentos relacionados (RFC, ADR, ARCH, SPEC, Reviews) o recursos externos. | Preferiblemente como enlaces Markdown relativos para que sean navegables en GitHub. |

---

## Ámbito de aplicación

Este estándar es aplicable a los cinco tipos de documento oficial:

- RFC
- ADR
- ARCH
- SPEC
- Reviews

La adopción del estándar en documentos o plantillas existentes, así como cualquier decisión sobre estados, versionado, identificadores o workflow, corresponde al Arquitecto y **no** forma parte de este Work Package.

---

## Fuera de alcance (corresponde al Arquitecto)

- Definir los **valores** concretos de cualquier campo.
- Definir el **catálogo de estados** oficiales (`Status`).
- Definir el **workflow** documental (transiciones, aprobaciones).
- Definir el **esquema de identificadores** y de **versionado**.
- Modificar documentos o plantillas ya existentes para aplicar el estándar.
