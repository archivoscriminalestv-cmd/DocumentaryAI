# Documentation Linter — Design (WP-0005)

> **Documento de diseño.** Describe *qué* haría una herramienta de validación de la estructura documental y *cómo* se organizaría. **No es una implementación**: no contiene código ni scripts. La construcción se abordará en un Work Package posterior, previa aprobación del Arquitecto.

---

## Objetivo

Diseñar una herramienta —el **Documentation Linter**— capaz de **validar de forma automática la coherencia y la integridad de la documentación oficial** del proyecto (los documentos bajo `docs/`, con foco en `docs/architecture/`).

El linter debe:

- comprobar que los documentos cumplen los estándares acordados (p. ej. el estándar de cabecera),
- detectar inconsistencias estructurales (IDs duplicados, referencias rotas, documentos huérfanos o sin estado),
- verificar las relaciones esperadas entre tipos de documento (RFC, ADR, ARCH, SPEC),
- y emitir un **informe accionable** con la severidad de cada hallazgo.

**Principio rector:** el linter es **dirigido por configuración**. No codifica de forma fija el catálogo de estados, el esquema de identificadores ni la política de relaciones entre documentos — esos valores los define el Arquitecto y se le suministran como entrada. Así la herramienta no invade decisiones de gobierno documental y se adapta cuando estas cambien.

---

## Arquitectura

Arquitectura modular en *pipeline*, con una clara separación de responsabilidades. El núcleo (descubrimiento, parseo, motor de reglas) es independiente del formato de entrada/salida y de las reglas concretas.

| Componente | Responsabilidad |
|---|---|
| **Config Loader** | Carga la configuración del linter (reglas activas, severidades, catálogo de estados, esquema de IDs, política de relaciones, rutas a analizar). |
| **Discovery** | Recorre el árbol documental y produce la lista de documentos candidatos, respetando inclusiones/exclusiones (p. ej. ignorar `.gitkeep`, plantillas, etc.). |
| **Parser** | Para cada documento, extrae su **cabecera** (metadatos), sus **referencias** (enlaces/rutas a otros documentos) y su **tipo** inferido. Produce un modelo normalizado en memoria. |
| **Document Model** | Representación interna y homogénea de cada documento (ruta, tipo, campos de cabecera, referencias salientes). Base sobre la que operan las reglas. |
| **Rule Engine** | Ejecuta el conjunto de reglas activas sobre el modelo (documento a documento y a nivel global del corpus). Cada regla devuelve cero o más hallazgos. |
| **Findings Collector** | Agrega los hallazgos, les asigna severidad y los normaliza. |
| **Reporter** | Formatea la salida (texto legible y/o formato máquina) y determina el código de salida. |

**Flujo:** `Config Loader → Discovery → Parser → Document Model → Rule Engine → Findings Collector → Reporter`.

Dos ámbitos de validación:
- **Por documento** (reglas locales): p. ej. cabecera obligatoria, estado presente.
- **Por corpus** (reglas globales): p. ej. IDs duplicados, referencias rotas, relaciones RFC/ADR/SPEC/ARCH (requieren ver todos los documentos a la vez).

---

## Entradas

1. **Árbol documental**: directorio raíz a analizar (por defecto `docs/`, con foco configurable en `docs/architecture/`).
2. **Configuración del linter** (suministrada, no inventada por la herramienta):
   - conjunto de **reglas activas** y su **severidad** asignada,
   - **catálogo de estados** válidos (definido por el Arquitecto),
   - **esquema de identificadores** (patrón de Document ID por tipo),
   - **campos de cabecera obligatorios** (según el estándar de cabecera vigente),
   - **política de relaciones** entre tipos (qué exige cada tipo: p. ej. SPEC→RFC, ARCH→ADR),
   - **inclusiones/exclusiones** de rutas y archivos.
3. **Estándares de referencia existentes** como fuente de verdad de las reglas: el estándar de cabecera y el catálogo de tipos documentales.

> Mientras el Arquitecto no defina estados, IDs y política de relaciones, esas reglas quedan **inactivas o en modo aviso**, configurables, sin bloquear al linter.

---

## Salidas

1. **Informe legible para humanos**: lista de hallazgos agrupados por severidad (Crítico / Importante / Menor) y por documento, indicando regla, ubicación y descripción.
2. **Informe en formato máquina** (estructurado, p. ej. orientado a integración en CI): un registro por hallazgo con campos como `regla`, `severidad`, `documento`, `detalle`.
3. **Resumen agregado**: recuentos por severidad y por regla.
4. **Código de salida**: éxito si no hay hallazgos por encima del umbral configurado; fallo en caso contrario (para poder integrarse en validaciones automáticas en el futuro).

El formato y los umbrales son **configurables**; el contenido de los hallazgos es independiente del formato.

---

## Reglas de validación

Cada regla tiene: identificador, descripción, ámbito (documento/corpus), severidad (configurable) y condición que la dispara. El mapeo de las comprobaciones requeridas:

| Regla | Ámbito | Qué comprueba | Severidad sugerida (configurable) |
|---|---|---|---|
| **Cabeceras obligatorias** | Documento | Que el documento incluye la cabecera y todos los campos obligatorios del estándar de cabecera vigente. | Importante |
| **IDs duplicados** | Corpus | Que no existan dos documentos con el mismo Document ID. | Crítico |
| **Documentos sin estado** | Documento | Que el campo de estado esté presente y, si hay catálogo definido, contenga un valor válido. | Importante |
| **Referencias rotas** | Corpus | Que toda referencia a otro documento apunte a un documento que **existe**. | Crítico |
| **RFC inexistentes** | Corpus | Que toda referencia a un RFC (por ID) corresponda a un RFC realmente presente. | Crítico |
| **ADR huérfanos** | Corpus | Que cada ADR esté vinculado a su contexto esperado según la política de relaciones (p. ej. asociado a un RFC/ARCH); detectar ADR sin vínculo. | Importante |
| **SPEC sin RFC asociado** | Corpus | Que cada SPEC referencie un RFC asociado válido. | Importante |
| **ARCH sin ADR asociado** | Corpus | Que cada ARCH referencie al menos un ADR que lo sustente. | Importante |

Reglas adicionales naturales (opcionales, para considerar por el Arquitecto): formato de fecha consistente, `Last Updated ≥ Created`, conformidad del Document ID con su esquema, detección de documentos vacíos/*Reserved*.

> Las reglas de **relación** (ADR huérfanos, SPEC→RFC, ARCH→ADR) dependen de la **política de relaciones** que defina el Arquitecto. El diseño las contempla, pero permanecen inactivas hasta que dicha política exista.

---

## Posibles errores

Errores **operativos** que la propia herramienta debe gestionar con elegancia (distintos de los *hallazgos* de validación):

- **Configuración ausente o inválida**: sin reglas/estados/IDs que aplicar → la herramienta debe avisar claramente y no asumir valores por defecto silenciosos.
- **Documento mal formado**: cabecera ausente o no parseable, tabla de metadatos corrupta → reportar como hallazgo, no como caída.
- **Archivo ilegible / permisos / codificación inesperada** → registrar el error y continuar con el resto del corpus.
- **Tipo de documento no reconocido**: un archivo que no encaja en el catálogo de tipos → marcar como advertencia, sin detener el análisis.
- **Referencias ambiguas**: una referencia que podría apuntar a varios documentos → reportar para resolución manual.
- **Corpus vacío**: ningún documento encontrado → informar, no fallar de forma opaca.

Principio: **un error en un documento no debe abortar el análisis del resto**; la herramienta agrega y reporta.

---

## Extensibilidad

- **Reglas como módulos independientes**: cada regla implementa un contrato común (recibe el modelo, devuelve hallazgos). Añadir una comprobación = añadir una regla, sin tocar el motor.
- **Dirigido por configuración**: activar/desactivar reglas, ajustar severidades y umbrales, y suministrar catálogos (estados, IDs, relaciones) sin modificar el código.
- **Catálogo de tipos abierto**: nuevos tipos de documento (p. ej. *Handbook*, *Glossary*) se incorporan por configuración, junto con sus reglas de relación.
- **Formatos de salida enchufables**: el Reporter admite nuevos formatos (texto, máquina, integración CI) sin afectar al motor de reglas.
- **Independencia del almacenamiento**: el Discovery/Parser aíslan el origen de los documentos, de modo que el núcleo no depende de detalles del sistema de ficheros.
- **Integrable en automatización futura**: el código de salida y la salida máquina permiten su uso en validaciones automáticas, cuando el Arquitecto lo decida.

---

## Dependencias de decisiones del Arquitecto

Este diseño queda **completo a nivel conceptual**, pero su puesta en marcha requiere que el Arquitecto defina previamente:

1. el **catálogo de estados** oficiales (para "Documentos sin estado"),
2. el **esquema de Document ID** por tipo (para "IDs duplicados" y validación de formato),
3. la **política de relaciones** entre RFC/ADR/SPEC/ARCH (para las reglas de orfandad y asociación),
4. los **campos obligatorios** definitivos del estándar de cabecera.

Hasta entonces, las reglas dependientes permanecen configurables e inactivas, sin bloquear al resto.

---

_Fin del documento de diseño. No incluye implementación, código ni scripts._
