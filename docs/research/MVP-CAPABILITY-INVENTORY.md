# MVP CAPABILITY INVENTORY — DocumentaryAI (WP-0013)

| Campo | Valor |
|---|---|
| **Document ID** | RES-MVP-CAPABILITY-INVENTORY |
| **Title** | MVP Capability Inventory — DocumentaryAI |
| **Status** | Draft (synthesis) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | WP-0007, WP-0009, WP-0010, WP-0011, WP-0012 (ver §8) |

> **Documento de síntesis (Sprint A-02 — MVP Definition).** Inventario de capacidades del MVP derivado **exclusivamente** de la evidencia aprobada del Sprint A-01.
> **No** diseña arquitectura, componentes, servicios, agentes, Bounded Contexts, Aggregate Roots, entidades, modelos de dominio, ni workflows; **no** elige tecnologías; **no** propone implementación ni prioridades de implementación; **no** decide el alcance final (eso corresponde al Principal Architect en **ARCH-0003**).
> La clasificación MVP es una **lectura funcional** de apoyo, no una decisión.

---

## 1. Objetivo

Consolidar, a partir de la evidencia existente, el **inventario completo de capacidades** que el MVP de DocumentaryAI podría necesitar, descritas de forma homogénea y clasificadas funcionalmente, para facilitar al Principal Architect la definición de ARCH-0003 — MVP Capability Architecture.

No se diseña el sistema: se **enumera y clasifica** qué debe ser capaz de hacer.

---

## 2. Alcance

- Fuente única: WP-0007, WP-0009, WP-0010, WP-0011 (Domain Discovery) y WP-0012 (Production Capability Map). **Sin investigación nueva.**
- Cada capacidad se describe con **11 atributos**: Identificador · Nombre · Objetivo · Descripción · Entradas · Salidas · Artefactos utilizados · Artefactos producidos · Dependencias funcionales · Valor para el usuario · Valor para el aprendizaje.
- Backbone: las 29 capacidades de producción de WP-0012 (C-01…C-29), reexpresadas como capacidades del sistema, **más** capacidades transversales derivadas del Domain Discovery (procedencia, afirmaciones/evidencia, incertidumbre, contenedor de proyecto/caso).
- Clasificación funcional: **Esencial para el MVP / Importante pero aplazable / Fuera del alcance del MVP**.
- Fuera de alcance: arquitectura, dominio, tecnologías, implementación.

**Criterio de clasificación (solo funcional):** se considera *Esencial* lo necesario para completar **un primer ciclo extremo-a-extremo** (producir → publicar → medir → aprender) coherente con la naturaleza del producto (investigación basada en evidencia); *Importante pero aplazable* lo que mejora calidad/profundidad pero no impide ese ciclo; *Fuera del MVP* lo que no participa en el primer ciclo de aprendizaje. No implica orden ni prioridad de implementación.

---

## 3. Capacidades identificadas

> Trazabilidad: *(src: …)* indica el/los WP de origen. Campos abreviados por concisión; el detalle de proceso está en WP-0012.

### Bloque investigación

**MVP-CAP-01 · Ideación** *(src: WP-0012 C-01)*
- Objetivo: generar ideas candidatas. Descripción: exploración divergente de temas/ángulos.
- Entradas: intereses, tendencias, lecciones previas → Salidas: ideas candidatas.
- Artefactos usados: lecciones aprendidas. Producidos: banco de ideas.
- Dependencias: — (realimentada por CAP-29). 
- Valor usuario: opciones de contenido. Valor aprendizaje: patrones de interés.

**MVP-CAP-02 · Selección de tema** *(src: WP-0012 C-02)*
- Objetivo: elegir el tema a producir. Descripción: filtrado por interés/viabilidad/demanda.
- Entradas: banco de ideas, señales históricas → Salidas: tema seleccionado.
- Artefactos usados: banco de ideas, métricas históricas. Producidos: ficha de tema.
- Dependencias: CAP-01.
- Valor usuario: foco del proyecto. Valor aprendizaje: criterios de selección que rinden.

**MVP-CAP-03 · Definición de objetivos** *(src: WP-0012 C-03)*
- Objetivo: fijar metas (audiencia, mensaje, éxito). Descripción: objetivos editoriales/de canal.
- Entradas: tema, audiencia → Salidas: objetivos del proyecto.
- Artefactos usados: ficha de tema. Producidos: documento de objetivos.
- Dependencias: CAP-02.
- Valor usuario: claridad de propósito. Valor aprendizaje: objetivos↔resultados.

**MVP-CAP-04 · Planificación de investigación** *(src: WP-0012 C-04)*
- Objetivo: planear la investigación. Descripción: preguntas, líneas y alcance.
- Entradas: tema, objetivos → Salidas: plan de investigación.
- Artefactos usados: objetivos. Producidos: preguntas, plan.
- Dependencias: CAP-03.
- Valor usuario: investigación enfocada. Valor aprendizaje: realismo de planes.

**MVP-CAP-05 · Descubrimiento de fuentes** *(src: WP-0012 C-05; WP-0009 Source)*
- Objetivo: localizar fuentes. Descripción: identificar documentos/testimonios/datos.
- Entradas: plan, preguntas → Salidas: lista de fuentes.
- Artefactos usados: plan. Producidos: lista de fuentes + metadatos de fuente.
- Dependencias: CAP-04.
- Valor usuario: materia prima del documental. Valor aprendizaje: fuentes productivas por tema.

**MVP-CAP-06 · Recolección de información** *(src: WP-0012 C-06)*
- Objetivo: obtener contenido de las fuentes. Descripción: recopilar/registrar material.
- Entradas: lista de fuentes → Salidas: material recopilado.
- Artefactos usados: fuentes. Producidos: documentos, transcripciones, notas, observaciones.
- Dependencias: CAP-05; CAP-30 (procedencia).
- Valor usuario: base documental. Valor aprendizaje: rendimiento de recolección.

**MVP-CAP-07 · Organización de materiales** *(src: WP-0012 C-07)*
- Objetivo: estructurar material. Descripción: clasificar, etiquetar, relacionar.
- Entradas: material recopilado → Salidas: material organizado.
- Artefactos usados: material. Producidos: índice, etiquetas, colecciones.
- Dependencias: CAP-06.
- Valor usuario: material manejable. Valor aprendizaje: esquemas de organización reutilizables.

**MVP-CAP-08 · Verificación** *(src: WP-0012 C-08; WP-0010 justificación; WP-0011)*
- Objetivo: comprobar veracidad/fiabilidad. Descripción: corroboración y evaluación de fuentes.
- Entradas: material organizado, afirmaciones → Salidas: material verificado con confianza.
- Artefactos usados: afirmaciones, fuentes. Producidos: notas de verificación, estado de confianza.
- Dependencias: CAP-07; CAP-31 (afirmaciones), CAP-32 (confianza).
- Valor usuario: credibilidad. Valor aprendizaje: afirmaciones no verificables / fuentes poco fiables.

**MVP-CAP-09 · Análisis** *(src: WP-0012 C-09; WP-0007; WP-0011)*
- Objetivo: interpretar el material. Descripción: relaciones, contradicciones, cronologías, vacíos.
- Entradas: material verificado → Salidas: resultados de análisis.
- Artefactos usados: material verificado. Producidos: cronologías, contradicciones, relaciones, hallazgos.
- Dependencias: CAP-08.
- Valor usuario: comprensión del caso. Valor aprendizaje: análisis con más valor narrativo.

**MVP-CAP-10 · Construcción de conocimiento** *(src: WP-0012 C-10; WP-0007/09/10/11)*
- Objetivo: consolidar conocimiento. Descripción: hipótesis y conclusiones justificadas.
- Entradas: resultados de análisis → Salidas: base de conocimiento del proyecto.
- Artefactos usados: hallazgos. Producidos: hipótesis, conclusiones, preguntas abiertas.
- Dependencias: CAP-09.
- Valor usuario: tesis sólida. Valor aprendizaje: conocimiento reutilizable entre proyectos.

### Bloque narrativa

**MVP-CAP-11 · Diseño narrativo** *(src: WP-0012 C-11)*
- Objetivo: definir ángulo/tono/arco. Descripción: enfoque y promesa narrativa.
- Entradas: conocimiento, objetivos → Salidas: concepto narrativo.
- Artefactos usados: base de conocimiento. Producidos: ángulo, tono, arco.
- Dependencias: CAP-10, CAP-03.
- Valor usuario: narrativa atractiva. Valor aprendizaje: ángulos que conectan.

**MVP-CAP-12 · Estructura** *(src: WP-0012 C-12)*
- Objetivo: secuenciar el contenido. Descripción: actos/secciones/capítulos.
- Entradas: concepto narrativo → Salidas: estructura/escaleta.
- Artefactos usados: concepto narrativo. Producidos: outline, escaleta.
- Dependencias: CAP-11.
- Valor usuario: documental coherente. Valor aprendizaje: estructuras con mejor retención.

**MVP-CAP-13 · Guion** *(src: WP-0012 C-13)*
- Objetivo: redactar el guion. Descripción: convertir estructura en texto narrado.
- Entradas: estructura, conocimiento → Salidas: guion.
- Artefactos usados: escaleta, conocimiento. Producidos: guion + referencias afirmación↔fuente.
- Dependencias: CAP-12; CAP-30 (trazabilidad).
- Valor usuario: contenido del vídeo. Valor aprendizaje: patrones de guion eficaces.

**MVP-CAP-14 · Storyboard** *(src: WP-0012 C-14)*
- Objetivo: planificar visualmente el guion. Descripción: plano/visual por sección.
- Entradas: guion → Salidas: storyboard.
- Artefactos usados: guion. Producidos: storyboard, lista de planos.
- Dependencias: CAP-13.
- Valor usuario: claridad visual. Valor aprendizaje: correspondencia guion↔visual.

**MVP-CAP-15 · Planificación visual** *(src: WP-0012 C-15)*
- Objetivo: definir estilo/recursos. Descripción: estética y plan de recursos.
- Entradas: storyboard → Salidas: plan visual.
- Artefactos usados: storyboard. Producidos: guía de estilo, lista de recursos.
- Dependencias: CAP-14.
- Valor usuario: identidad visual. Valor aprendizaje: estilos con mejor desempeño.

### Bloque producción / post

**MVP-CAP-16 · Producción de recursos** *(src: WP-0012 C-16)*
- Objetivo: crear/obtener recursos. Descripción: imágenes, vídeo, gráficos, música, SFX.
- Entradas: plan visual → Salidas: recursos (assets).
- Artefactos usados: guía de estilo. Producidos: assets + registro de licencias.
- Dependencias: CAP-15; CAP-23 (derechos).
- Valor usuario: material audiovisual. Valor aprendizaje: recursos reutilizables.

**MVP-CAP-17 · Locución** *(src: WP-0012 C-17)*
- Objetivo: producir la voz narrativa. Descripción: grabar/sintetizar narración.
- Entradas: guion → Salidas: pista de locución.
- Artefactos usados: guion. Producidos: audio de narración, timing.
- Dependencias: CAP-13.
- Valor usuario: narración. Valor aprendizaje: estilos de locución con mejor retención.

**MVP-CAP-18 · Edición** *(src: WP-0012 C-18)*
- Objetivo: ensamblar el documental. Descripción: montaje de locución+recursos+ritmo.
- Entradas: locución, recursos, storyboard → Salidas: vídeo editado (máster).
- Artefactos usados: assets, locución, storyboard. Producidos: máster, subtítulos.
- Dependencias: CAP-16, CAP-17, CAP-14.
- Valor usuario: pieza final. Valor aprendizaje: montaje que retiene audiencia.

**MVP-CAP-19 · Control de calidad** *(src: WP-0012 C-19)*
- Objetivo: revisar antes de exportar. Descripción: exactitud, calidad, derechos, coherencia.
- Entradas: vídeo editado → Salidas: vídeo aprobado / correcciones.
- Artefactos usados: máster, verificación. Producidos: checklist QA, informe.
- Dependencias: CAP-18, CAP-08.
- Valor usuario: calidad y rigor. Valor aprendizaje: errores recurrentes.

**MVP-CAP-20 · Exportación** *(src: WP-0012 C-20)*
- Objetivo: generar el archivo final. Descripción: render en formato/calidad.
- Entradas: vídeo aprobado → Salidas: archivo final.
- Artefactos usados: máster. Producidos: fichero de vídeo, derivados.
- Dependencias: CAP-19.
- Valor usuario: vídeo listo. Valor aprendizaje: ajustes de exportación.

### Bloque publicación

**MVP-CAP-21 · Empaquetado (título/miniatura)** *(src: WP-0012 C-21)*
- Objetivo: crear el packaging del clic. Descripción: título + miniatura.
- Entradas: concepto narrativo, vídeo final → Salidas: título + miniatura.
- Artefactos usados: concepto narrativo. Producidos: variantes de título, miniaturas.
- Dependencias: CAP-11, CAP-20.
- Valor usuario: atractivo/CTR. Valor aprendizaje: packaging que maximiza CTR.

**MVP-CAP-22 · Metadatos / SEO** *(src: WP-0012 C-22)*
- Objetivo: optimizar descubribilidad. Descripción: descripción, tags, capítulos.
- Entradas: tema, guion → Salidas: metadatos de publicación.
- Artefactos usados: guion. Producidos: descripción, tags, capítulos.
- Dependencias: CAP-13, CAP-20.
- Valor usuario: descubrimiento. Valor aprendizaje: metadatos que mejoran impresiones.

**MVP-CAP-23 · Derechos y cumplimiento** *(src: WP-0012 C-23)*
- Objetivo: uso lícito y cumplimiento. Descripción: licencias, atribución, políticas.
- Entradas: recursos, fuentes → Salidas: estado de cumplimiento.
- Artefactos usados: assets, fuentes. Producidos: registro de licencias/atribuciones.
- Dependencias: CAP-05, CAP-16.
- Valor usuario: seguridad legal. Valor aprendizaje: fuentes/recursos a evitar.

**MVP-CAP-24 · Publicación** *(src: WP-0012 C-24)*
- Objetivo: publicar en YouTube. Descripción: subir vídeo + packaging + metadatos.
- Entradas: archivo final, packaging, metadatos → Salidas: vídeo publicado.
- Artefactos usados: fichero, título/miniatura, metadatos. Producidos: registro de publicación, URL.
- Dependencias: CAP-20, CAP-21, CAP-22, CAP-23.
- Valor usuario: contenido en vivo. Valor aprendizaje: formatos/horarios de publicación.

**MVP-CAP-25 · Distribución** *(src: WP-0012 C-25)*
- Objetivo: ampliar alcance externo. Descripción: clips y difusión multicanal.
- Entradas: vídeo publicado → Salidas: acciones de distribución.
- Artefactos usados: assets, vídeo. Producidos: clips, publicaciones, calendario.
- Dependencias: CAP-24.
- Valor usuario: más alcance. Valor aprendizaje: canales más efectivos.

### Bloque post-publicación / aprendizaje

**MVP-CAP-26 · Métricas** *(src: WP-0012 C-26)*
- Objetivo: medir desempeño. Descripción: recoger métricas de plataforma/audiencia.
- Entradas: vídeo publicado → Salidas: conjunto de métricas.
- Artefactos usados: registro de publicación. Producidos: panel de métricas.
- Dependencias: CAP-24.
- Valor usuario: visibilidad de resultados. Valor aprendizaje: desempeño real medible (núcleo).

**MVP-CAP-27 · Retroalimentación** *(src: WP-0012 C-27)*
- Objetivo: interpretar métricas/respuesta. Descripción: señales accionables.
- Entradas: métricas, comentarios → Salidas: insights de desempeño.
- Artefactos usados: métricas, comentarios. Producidos: informe de desempeño.
- Dependencias: CAP-26, CAP-28.
- Valor usuario: comprensión de resultados. Valor aprendizaje: decisión→resultado.

**MVP-CAP-28 · Interacción con la comunidad** *(src: WP-0012 C-28)*
- Objetivo: gestionar la conversación. Descripción: moderar/responder comentarios.
- Entradas: vídeo publicado, comentarios → Salidas: feedback cualitativo.
- Artefactos usados: comentarios. Producidos: temas recurrentes, correcciones de la audiencia.
- Dependencias: CAP-24.
- Valor usuario: relación con la audiencia. Valor aprendizaje: demandas/objeciones; ideas para CAP-01.

**MVP-CAP-29 · Aprendizaje** *(src: WP-0012 C-29)*
- Objetivo: capitalizar el proyecto. Descripción: consolidar lecciones del ciclo.
- Entradas: insights, feedback → Salidas: lecciones aprendidas.
- Artefactos usados: informe de desempeño. Producidos: lecciones, buenas prácticas, antipatrones.
- Dependencias: CAP-27, CAP-28.
- Valor usuario: mejora continua. Valor aprendizaje: cierra el bucle hacia CAP-01.

### Bloque transversal (derivado del Domain Discovery)

**MVP-CAP-30 · Gestión de procedencia (provenance)** *(src: WP-0007, WP-0009, WP-0010, WP-0011 — consenso alto)*
- Objetivo: registrar origen e historia de cada material/afirmación. Descripción: trazabilidad de dónde viene y cómo cambió.
- Entradas: material, afirmaciones → Salidas: registro de procedencia.
- Artefactos usados: fuentes, materiales. Producidos: cadena de procedencia/custodia.
- Dependencias: CAP-06 (transversal a CAP-06…CAP-13).
- Valor usuario: confianza y auditabilidad. Valor aprendizaje: trazabilidad reutilizable.

**MVP-CAP-31 · Gestión de afirmaciones y evidencia** *(src: WP-0007, WP-0009, WP-0010, WP-0011)*
- Objetivo: registrar afirmaciones y su relación de evidencia. Descripción: evidencia como rol; separación hecho↔interpretación.
- Entradas: observaciones, material → Salidas: afirmaciones con su soporte.
- Artefactos usados: observaciones, hallazgos. Producidos: afirmaciones, vínculos de apoyo/contradicción.
- Dependencias: CAP-06; usada por CAP-08, CAP-09, CAP-10, CAP-13.
- Valor usuario: rigor de las afirmaciones. Valor aprendizaje: patrones de afirmación/contradicción.

**MVP-CAP-32 · Gestión de incertidumbre/confianza** *(src: WP-0010, WP-0011)*
- Objetivo: representar el grado de certeza. Descripción: confianza de fuentes/afirmaciones/conclusiones.
- Entradas: afirmaciones, fuentes → Salidas: niveles de confianza.
- Artefactos usados: afirmaciones, fuentes. Producidos: indicadores de confianza.
- Dependencias: CAP-31; usada por CAP-08, CAP-10.
- Valor usuario: matización honesta. Valor aprendizaje: calibración confianza↔realidad.

**MVP-CAP-33 · Gestión de proyectos/casos de investigación** *(src: WP-0009 Case/Investigation; visión del proyecto)*
- Objetivo: contener y organizar todo lo relativo a una investigación. Descripción: unidad de trabajo que agrupa materiales, conocimiento y salidas.
- Entradas: tema, objetivos → Salidas: proyecto/caso gestionado.
- Artefactos usados: ficha de tema, objetivos. Producidos: contenedor del proyecto (materiales+conocimiento+salidas).
- Dependencias: CAP-02 (contiene CAP-04…CAP-29).
- Valor usuario: trabajo organizado por investigación. Valor aprendizaje: comparación entre proyectos.

---

## 4. Clasificación para el MVP

> Lectura **funcional** (criterio de §2). No es prioridad ni orden de implementación. La decisión final corresponde al Principal Architect (ARCH-0003).

| Capacidad | Clasificación | Justificación funcional |
|---|---|---|
| CAP-33 Proyecto/caso | **Esencial** | Contenedor mínimo para sostener un ciclo completo |
| CAP-02 Selección de tema | **Esencial** | Sin tema no hay vídeo |
| CAP-05 Descubrimiento de fuentes | **Esencial** | Materia prima del documental |
| CAP-06 Recolección | **Esencial** | Sin contenido no hay base |
| CAP-07 Organización | **Esencial** | Manejar el material para producir |
| CAP-08 Verificación | **Esencial** | Credibilidad: núcleo del producto (investigación real) |
| CAP-11 Diseño narrativo | **Esencial** | Necesario para un documental, no un volcado de datos |
| CAP-12 Estructura | **Esencial** | Secuencia mínima del documental |
| CAP-13 Guion | **Esencial** | Contenido narrado del vídeo |
| CAP-16 Producción de recursos | **Esencial** | Sin visuales no hay vídeo |
| CAP-17 Locución | **Esencial** | Narración del documental |
| CAP-18 Edición | **Esencial** | Ensamblaje de la pieza |
| CAP-20 Exportación | **Esencial** | Genera el archivo publicable |
| CAP-21 Empaquetado | **Esencial** | Título/miniatura imprescindibles para publicar en YouTube |
| CAP-23 Derechos | **Esencial** | Puerta legal: no se puede publicar con material ilícito |
| CAP-24 Publicación | **Esencial** | Sin publicación no hay métricas ni aprendizaje |
| CAP-26 Métricas | **Esencial** | Objetivo del MVP: obtener datos reales |
| CAP-27 Retroalimentación | **Esencial** | Convertir métricas en aprendizaje |
| CAP-29 Aprendizaje | **Esencial** | Cierra el bucle del MVP |
| CAP-30 Procedencia | **Esencial** | Consenso de dominio más alto; sostiene la credibilidad |
| CAP-31 Afirmaciones/evidencia | **Esencial** | Núcleo del valor (investigación basada en evidencia) |
| CAP-01 Ideación | **Importante aplazable** | Puede hacerse de forma manual/mínima en el primer ciclo |
| CAP-03 Objetivos | **Importante aplazable** | Útil para medir éxito; el ciclo puede completarse sin formalizarlos |
| CAP-04 Plan de investigación | **Importante aplazable** | Mejora el rigor; no impide producir un primer vídeo |
| CAP-09 Análisis | **Importante aplazable** | Aporta profundidad; un primer vídeo admite análisis ligero |
| CAP-10 Construcción de conocimiento | **Importante aplazable** | Hipótesis/conclusiones ricas mejoran, no bloquean |
| CAP-14 Storyboard | **Importante aplazable** | Mejora la planificación visual; sustituible por algo más simple |
| CAP-15 Planificación visual | **Importante aplazable** | Mejora estética; no imprescindible para un primer vídeo |
| CAP-19 Control de calidad | **Importante aplazable** | Recomendable; puede ser revisión mínima al inicio |
| CAP-22 Metadatos/SEO | **Importante aplazable** | Un título/descripción básicos bastan para publicar |
| CAP-32 Incertidumbre/confianza | **Importante aplazable** | Enriquece el rigor; puede empezar como nota simple |
| CAP-25 Distribución | **Fuera del MVP** | Difusión multicanal no es necesaria para el primer ciclo de aprendizaje |
| CAP-28 Comunidad | **Fuera del MVP** | La interacción posterior no condiciona producir/publicar/medir el primero |

Resumen: **21 Esenciales · 10 Importantes aplazables · 2 Fuera del MVP**.

---

## 5. Dependencias funcionales

> Prerrequisitos funcionales (qué necesita estar disponible para que una capacidad opere). No es workflow ni arquitectura.

Cadena principal (lineal):
```
CAP-33 ─ contiene ─► CAP-02 → CAP-04 → CAP-05 → CAP-06 → CAP-07 → CAP-08 → CAP-09 → CAP-10
        → CAP-11 → CAP-12 → CAP-13 → CAP-14 → CAP-15 → CAP-16 ┐
                                              CAP-17 ─────────┴► CAP-18 → CAP-19 → CAP-20
        → CAP-21, CAP-22, CAP-23 ─► CAP-24 → CAP-25
        → CAP-26 → CAP-28 → CAP-27 → CAP-29 ─(realimenta)► CAP-01/CAP-02
```

Dependencias transversales:
- **CAP-30 Procedencia**: requerida desde CAP-06 y usada por CAP-08, CAP-09, CAP-10, CAP-13 (trazabilidad afirmación↔fuente).
- **CAP-31 Afirmaciones/evidencia**: nace en CAP-06; prerrequisito de CAP-08, CAP-09, CAP-10, CAP-13.
- **CAP-32 Incertidumbre**: depende de CAP-31; usada por CAP-08 y CAP-10.
- **CAP-23 Derechos**: transversal a CAP-05 y CAP-16, y puerta previa a CAP-24.
- **CAP-01 Ideación**: realimentada por CAP-29 (bucle de aprendizaje).

Prerrequisitos críticos (capacidades de las que dependen muchas otras): **CAP-33** (contenedor), **CAP-06** (origen de materiales/afirmaciones), **CAP-31** y **CAP-30** (sustrato de evidencia y procedencia), **CAP-13** (guion, del que parten producción y publicación).

---

## 6. Capacidades fuera del MVP

| Capacidad | Motivo funcional |
|---|---|
| **CAP-25 Distribución** | Ampliar alcance fuera de la página del vídeo no es necesario para completar producir→publicar→medir→aprender por primera vez. |
| **CAP-28 Interacción con la comunidad** | El feedback cualitativo posterior enriquece el aprendizaje pero no condiciona el primer ciclo; puede incorporarse después. |

> Nota: "Fuera del MVP" es una valoración **funcional** para un primer ciclo; no implica descarte permanente.

---

## 7. Observaciones

- El inventario muestra que un **ciclo extremo-a-extremo** requiere una franja de capacidades a lo largo de toda la cadena (no solo producción): de la selección de tema al aprendizaje, pasando por una **base mínima de evidencia/procedencia** coherente con la naturaleza del producto.
- Las capacidades **transversales del dominio** (CAP-30 procedencia, CAP-31 afirmaciones/evidencia) emergen como esenciales precisamente por el **consenso alto** identificado en WP-0011; se incluyen como capacidades (qué debe poder hacer), **sin** modelarlas.
- Existe **tensión** entre la "delgadez" deseable del MVP y la exigencia de **rigor** del producto (verificación, procedencia): se ha reflejado clasificando verificación/procedencia/evidencia como esenciales y dejando análisis/conocimiento profundo como aplazables.
- La clasificación es **funcional y revisable**; el Principal Architect puede reclasificar en ARCH-0003 según criterios adicionales (riesgo, esfuerzo, estrategia) que **no** se han considerado aquí por estar fuera de alcance.
- Toda la trazabilidad remite a los cinco WP fuente; **no** se ha añadido conocimiento nuevo.

---

## 8. Referencias

> Únicamente los Work Packages aprobados del Sprint A-01/A-02. Sin fuentes externas.

- **WP-0007** — Evidence-Centric Domain Research · `docs/architecture/Evidence-Centric-Domain-Research.md`
- **WP-0009** — Domain Ontology Research · `docs/research/DOMAIN-ONTOLOGY-RESEARCH.md`
- **WP-0010** — Epistemic Domain Pattern Research · `docs/research/EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md`
- **WP-0011** — Domain Evidence Synthesis Matrix · `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md`
- **WP-0012** — YouTube Documentary Production Capability Map · `docs/research/YOUTUBE-DOCUMENTARY-PRODUCTION-CAPABILITY-MAP.md`

---

_Fin del inventario. Documento de síntesis: no incorpora conocimiento nuevo, no diseña componentes, servicios, agentes, Bounded Contexts, Aggregate Roots, entidades, dominio ni arquitectura, no elige tecnologías y no propone implementación. Sirve exclusivamente para facilitar al Principal Architect la definición de ARCH-0003 — MVP Capability Architecture._
