# YOUTUBE DOCUMENTARY PRODUCTION — CAPABILITY MAP (WP-0012)

| Campo | Valor |
|---|---|
| **Document ID** | RES-YT-CAPABILITY-MAP |
| **Title** | YouTube Documentary Production Capability Map — DocumentaryAI |
| **Status** | Draft (research) |
| **Version** | 1.0 |
| **Author** | Claude Code (Architecture Research & Implementation Engineer) |
| **Created** | 2026-06-28 |
| **Last Updated** | 2026-06-28 |
| **Owner** | Principal Architect |
| **Reviewers** | Principal Architect |
| **Related Documents** | `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md` |

> **Documento de investigación (Sprint A-02 — MVP Definition).** Mapea las **capacidades** del proceso de producción de un documental para YouTube, de la idea al aprendizaje post-publicación.
> **No** diseña DocumentaryAI, **no** define arquitectura, Bounded Contexts, Aggregate Roots, entidades, ontologías, modelos de dominio ni workflows internos del sistema; **no** prioriza tecnologías ni elige herramientas; **no** decide.
> Describe el **proceso observado** en la producción de documentales para YouTube. Servirá de evidencia para que el Principal Architect defina el MVP.

---

## 1. Objetivo

Identificar y describir, de forma exhaustiva y **descriptiva**, las capacidades que intervienen en producir un documental para YouTube: qué hace cada capacidad, qué consume y produce, qué artefactos genera, su dependencia de otras, su potencial de automatización por IA, su necesidad de supervisión humana y su valor para el aprendizaje.

El foco es el **proceso** (capacidades), no el sistema. No se propone cómo construir DocumentaryAI.

---

## 2. Alcance

- Cubre el ciclo completo: ideación → investigación → análisis → narrativa → guion → visuales → producción → edición → publicación → distribución → métricas → aprendizaje.
- Documenta las **24 capacidades mínimas** requeridas por el WP más capacidades **adicionales recurrentes** en la producción para YouTube (empaquetado, metadatos/SEO, derechos, control de calidad, comunidad).
- Para cada capacidad: los **10 atributos** indicados por el WP.
- Fuera de alcance: diseño, arquitectura, modelo de datos, elección de herramientas o decisiones de dominio.

---

## 3. Metodología

- **Descomposición en capacidades independientes** siguiendo el flujo estándar de producción audiovisual (pre-producción / producción / post-producción / publicación / post-publicación) adaptado a las particularidades de YouTube (empaquetado, algoritmo, métricas).
- **Rejilla uniforme de 10 atributos** por capacidad para comparabilidad.
- **Escalas cualitativas** (solo descriptivas):
  - *Automatización IA potencial:* **Alta / Media / Baja**.
  - *Supervisión humana:* **Crítica / Recomendada / Ligera**.
- **Neutralidad tecnológica:** no se nombran herramientas ni proveedores concretos.
- **Fuentes:** conocimiento de proceso de la industria audiovisual y de creación en YouTube (ver §10), citado de forma general.

---

## 4. Capacidades identificadas

> Codificadas C-01…C-29. Atributos: Objetivo · Descripción · Entradas · Salidas · Artefactos · Dependencias · Actividades · Automatización IA · Supervisión humana · Valor para el aprendizaje.

### C-01 · Ideación
- **Objetivo:** generar ideas candidatas de documental.
- **Descripción:** exploración divergente de temas posibles y ángulos.
- **Entradas:** intereses, tendencias, catálogo de casos, vacíos de contenido.
- **Salidas:** lista de ideas candidatas.
- **Artefactos:** banco de ideas; notas de ideación.
- **Dependencias:** ninguna (origen); se realimenta de C-29 (Aprendizaje).
- **Actividades:** brainstorming, escaneo de tendencias, registro de ideas.
- **Automatización IA:** Alta (generación y expansión de ideas).
- **Supervisión humana:** Recomendada (criterio editorial).
- **Valor para el aprendizaje:** qué tipos de idea surgen y cuáles se eligen; patrones de interés.

### C-02 · Selección del tema
- **Objetivo:** elegir el tema concreto a producir.
- **Descripción:** filtrado de ideas por interés, viabilidad y potencial de audiencia.
- **Entradas:** banco de ideas; criterios de selección; señales de demanda.
- **Salidas:** tema seleccionado.
- **Artefactos:** ficha de tema; justificación de selección.
- **Dependencias:** C-01; señales de C-27 (Métricas históricas).
- **Actividades:** evaluación comparativa, priorización, decisión.
- **Automatización IA:** Media (scoring/estimación de potencial).
- **Supervisión humana:** Crítica (decisión editorial y ética).
- **Valor para el aprendizaje:** criterios que predicen buen rendimiento; aciertos/errores de selección.

### C-03 · Definición de objetivos
- **Objetivo:** fijar qué debe lograr el vídeo (audiencia, mensaje, resultado).
- **Descripción:** establecer objetivos editoriales y de canal.
- **Entradas:** tema; objetivos del canal; público objetivo.
- **Salidas:** objetivos del proyecto.
- **Artefactos:** documento de objetivos; definición de audiencia.
- **Dependencias:** C-02.
- **Actividades:** definir mensaje, público, métricas de éxito esperadas.
- **Automatización IA:** Media (propuesta de objetivos y audiencias).
- **Supervisión humana:** Crítica (alineación con la estrategia).
- **Valor para el aprendizaje:** correlación entre objetivos planteados y resultados.

### C-04 · Planificación de la investigación
- **Objetivo:** planificar cómo se investigará el tema.
- **Descripción:** definir preguntas, líneas y alcance de la investigación.
- **Entradas:** tema; objetivos.
- **Salidas:** plan de investigación.
- **Artefactos:** preguntas de investigación; plan/cronograma.
- **Dependencias:** C-03.
- **Actividades:** formular preguntas, definir alcance, asignar tiempo.
- **Automatización IA:** Media (generación de preguntas y planes).
- **Supervisión humana:** Recomendada.
- **Valor para el aprendizaje:** qué planes resultan realistas; desviaciones plan↔real.

### C-05 · Descubrimiento de fuentes
- **Objetivo:** localizar fuentes relevantes.
- **Descripción:** identificar documentos, testimonios, archivos, datos.
- **Entradas:** plan de investigación; preguntas.
- **Salidas:** lista de fuentes candidatas.
- **Artefactos:** lista de fuentes; metadatos de fuente.
- **Dependencias:** C-04.
- **Actividades:** búsqueda, cribado, registro de fuentes.
- **Automatización IA:** Alta (búsqueda y recuperación).
- **Supervisión humana:** Recomendada (fiabilidad de la fuente).
- **Valor para el aprendizaje:** qué tipos de fuente son productivos por tema.

### C-06 · Recolección de información
- **Objetivo:** obtener el contenido de las fuentes.
- **Descripción:** recopilar y registrar material de las fuentes seleccionadas.
- **Entradas:** lista de fuentes.
- **Salidas:** material recopilado.
- **Artefactos:** documentos, transcripciones, capturas, notas, observaciones.
- **Dependencias:** C-05.
- **Actividades:** descarga/extracción, transcripción, toma de notas.
- **Automatización IA:** Alta (extracción, transcripción, resumen).
- **Supervisión humana:** Recomendada (exactitud).
- **Valor para el aprendizaje:** rendimiento de recolección; lagunas de información.

### C-07 · Organización de materiales
- **Objetivo:** estructurar el material recopilado.
- **Descripción:** clasificar, etiquetar y relacionar materiales.
- **Entradas:** material recopilado.
- **Salidas:** material organizado.
- **Artefactos:** índice de materiales; etiquetas; carpetas/colecciones.
- **Dependencias:** C-06.
- **Actividades:** clasificación, etiquetado, vinculación.
- **Automatización IA:** Alta (clasificación, etiquetado, deduplicación).
- **Supervisión humana:** Ligera.
- **Valor para el aprendizaje:** esquemas de organización que funcionan; reutilización.

### C-08 · Verificación
- **Objetivo:** comprobar la veracidad y fiabilidad del material.
- **Descripción:** contrastar afirmaciones y validar fuentes.
- **Entradas:** material organizado; afirmaciones.
- **Salidas:** material verificado con estado de confianza.
- **Artefactos:** notas de verificación; afirmaciones marcadas; nivel de confianza.
- **Dependencias:** C-07.
- **Actividades:** corroboración cruzada, evaluación de fuentes, marcado de incertidumbre.
- **Automatización IA:** Media (asistencia; señalar inconsistencias).
- **Supervisión humana:** Crítica (rigor y responsabilidad).
- **Valor para el aprendizaje:** patrones de afirmaciones no verificables; fuentes poco fiables.

### C-09 · Análisis
- **Objetivo:** interpretar el material verificado.
- **Descripción:** detectar relaciones, contradicciones, cronologías y vacíos.
- **Entradas:** material verificado.
- **Salidas:** resultados de análisis.
- **Artefactos:** cronologías; contradicciones; relaciones; hallazgos (findings).
- **Dependencias:** C-08.
- **Actividades:** correlación, construcción de cronología, detección de contradicciones.
- **Automatización IA:** Media-Alta (correlación, cronología, detección de contradicciones).
- **Supervisión humana:** Crítica (interpretación).
- **Valor para el aprendizaje:** qué análisis aportan más valor narrativo.

### C-10 · Construcción de conocimiento
- **Objetivo:** consolidar el conocimiento del caso.
- **Descripción:** derivar hipótesis y conclusiones justificadas del análisis.
- **Entradas:** resultados de análisis.
- **Salidas:** base de conocimiento del proyecto.
- **Artefactos:** hipótesis; conclusiones; mapa de conocimiento; preguntas abiertas.
- **Dependencias:** C-09.
- **Actividades:** formulación de hipótesis, justificación, síntesis.
- **Automatización IA:** Media (propuesta de hipótesis/síntesis).
- **Supervisión humana:** Crítica (validez y ética).
- **Valor para el aprendizaje:** conocimiento reutilizable entre proyectos; hipótesis recurrentes.

### C-11 · Diseño narrativo
- **Objetivo:** definir el enfoque y el arco narrativo.
- **Descripción:** decidir el ángulo, el tono y la promesa narrativa.
- **Entradas:** base de conocimiento; objetivos; audiencia.
- **Salidas:** concepto narrativo.
- **Artefactos:** ángulo/tesis; tono; arco narrativo.
- **Dependencias:** C-10, C-03.
- **Actividades:** definición de ángulo, tono, gancho.
- **Automatización IA:** Media (propuestas de ángulo/tono).
- **Supervisión humana:** Crítica (voz autoral).
- **Valor para el aprendizaje:** qué ángulos/tonos conectan con la audiencia.

### C-12 · Estructura del documental
- **Objetivo:** organizar el contenido en una estructura.
- **Descripción:** secuenciar el material en actos/secciones/capítulos.
- **Entradas:** concepto narrativo; conocimiento.
- **Salidas:** estructura/escaleta.
- **Artefactos:** outline; escaleta; capítulos.
- **Dependencias:** C-11.
- **Actividades:** definición de secciones, orden, ritmo.
- **Automatización IA:** Media-Alta (generación de outlines).
- **Supervisión humana:** Recomendada.
- **Valor para el aprendizaje:** estructuras con mejor retención.

### C-13 · Escritura del guion
- **Objetivo:** redactar el guion del documental.
- **Descripción:** convertir la estructura en texto narrado/dialogado.
- **Entradas:** estructura; conocimiento.
- **Salidas:** guion.
- **Artefactos:** guion; referencias a fuentes por afirmación.
- **Dependencias:** C-12.
- **Actividades:** redacción, citación, revisión de estilo.
- **Automatización IA:** Alta (redacción asistida).
- **Supervisión humana:** Crítica (exactitud, estilo, ética).
- **Valor para el aprendizaje:** patrones de guion eficaces; trazabilidad afirmación↔fuente.

### C-14 · Storyboard
- **Objetivo:** planificar visualmente el guion.
- **Descripción:** asociar cada parte del guion a un plano/visual.
- **Entradas:** guion.
- **Salidas:** storyboard.
- **Artefactos:** storyboard; lista de planos.
- **Dependencias:** C-13.
- **Actividades:** desglose por escena, bocetado, anotación visual.
- **Automatización IA:** Media-Alta (generación de storyboards).
- **Supervisión humana:** Recomendada.
- **Valor para el aprendizaje:** correspondencia guion↔visual que funciona.

### C-15 · Planificación visual
- **Objetivo:** definir el estilo y los recursos visuales necesarios.
- **Descripción:** establecer estética y plan de obtención de recursos.
- **Entradas:** storyboard.
- **Salidas:** plan visual.
- **Artefactos:** guía de estilo; lista de recursos a obtener/crear.
- **Dependencias:** C-14.
- **Actividades:** definición de estilo, inventario de recursos, plan.
- **Automatización IA:** Media.
- **Supervisión humana:** Recomendada.
- **Valor para el aprendizaje:** estilos visuales con mejor desempeño.

### C-16 · Producción de recursos
- **Objetivo:** crear/obtener los recursos visuales y sonoros.
- **Descripción:** generar imágenes, vídeo, gráficos, música, efectos.
- **Entradas:** plan visual; guía de estilo.
- **Salidas:** recursos (assets).
- **Artefactos:** imágenes, clips, gráficos, música, SFX; registro de licencias.
- **Dependencias:** C-15; C-23 (Derechos).
- **Actividades:** generación/creación, adquisición, organización de assets.
- **Automatización IA:** Alta (generación de imagen/vídeo/audio/gráficos).
- **Supervisión humana:** Recomendada (calidad y derechos).
- **Valor para el aprendizaje:** qué tipos de recurso rinden; reutilización de assets.

### C-17 · Locución
- **Objetivo:** producir la voz narrativa.
- **Descripción:** grabar o sintetizar la narración del guion.
- **Entradas:** guion.
- **Salidas:** pista de locución.
- **Artefactos:** audio de narración; timing.
- **Dependencias:** C-13.
- **Actividades:** grabación/síntesis, edición de audio, sincronía.
- **Automatización IA:** Alta (voz sintética/TTS).
- **Supervisión humana:** Recomendada (naturalidad, pronunciación).
- **Valor para el aprendizaje:** estilos de locución con mejor retención.

### C-18 · Edición
- **Objetivo:** ensamblar el documental.
- **Descripción:** montar locución, recursos y ritmo en una pieza coherente.
- **Entradas:** locución; recursos; storyboard.
- **Salidas:** vídeo editado (máster).
- **Artefactos:** proyecto de edición; versión máster; subtítulos.
- **Dependencias:** C-16, C-17, C-14.
- **Actividades:** montaje, sincronización, corrección de color/sonido, subtitulado.
- **Automatización IA:** Media-Alta (ensamblaje asistido, subtítulos).
- **Supervisión humana:** Crítica (calidad final).
- **Valor para el aprendizaje:** decisiones de ritmo/montaje que retienen audiencia.

### C-19 · Control de calidad *(adicional, recurrente)*
- **Objetivo:** revisar la pieza antes de exportar.
- **Descripción:** verificar exactitud, calidad técnica, derechos y coherencia.
- **Entradas:** vídeo editado.
- **Salidas:** vídeo aprobado o lista de correcciones.
- **Artefactos:** checklist de QA; informe de revisión.
- **Dependencias:** C-18, C-08.
- **Actividades:** revisión editorial/técnica/legal, corrección.
- **Automatización IA:** Media (detección de errores, comprobaciones).
- **Supervisión humana:** Crítica.
- **Valor para el aprendizaje:** errores recurrentes; checklist mejorable.

### C-20 · Exportación
- **Objetivo:** generar el archivo final para publicación.
- **Descripción:** renderizar en formato/calidad adecuados.
- **Entradas:** vídeo aprobado.
- **Salidas:** archivo final de vídeo.
- **Artefactos:** fichero de vídeo; archivos derivados (subtítulos, miniatura base).
- **Dependencias:** C-19.
- **Actividades:** render, comprobación de formato, generación de derivados.
- **Automatización IA:** Baja (proceso técnico).
- **Supervisión humana:** Ligera.
- **Valor para el aprendizaje:** ajustes de exportación óptimos.

### C-21 · Empaquetado (título y miniatura) *(adicional, recurrente)*
- **Objetivo:** crear el "packaging" que dispara el clic.
- **Descripción:** diseñar título y miniatura (clave en YouTube).
- **Entradas:** concepto narrativo; vídeo final.
- **Salidas:** título + miniatura.
- **Artefactos:** variantes de título; miniaturas; notas de A/B.
- **Dependencias:** C-11, C-20.
- **Actividades:** ideación de títulos, diseño de miniaturas, pruebas.
- **Automatización IA:** Alta (generación de títulos/miniaturas).
- **Supervisión humana:** Crítica (no clickbait engañoso; ética).
- **Valor para el aprendizaje:** qué packaging maximiza CTR.

### C-22 · Optimización de metadatos / SEO *(adicional, recurrente)*
- **Objetivo:** optimizar descubribilidad en la plataforma.
- **Descripción:** redactar descripción, etiquetas, capítulos, categoría.
- **Entradas:** tema; guion; objetivos.
- **Salidas:** metadatos de publicación.
- **Artefactos:** descripción; tags; marcas de capítulo; cards/end screens.
- **Dependencias:** C-13, C-20.
- **Actividades:** redacción SEO, definición de capítulos, enlaces.
- **Automatización IA:** Alta (generación de metadatos).
- **Supervisión humana:** Ligera-Recomendada.
- **Valor para el aprendizaje:** metadatos que mejoran impresiones/descubrimiento.

### C-23 · Gestión de derechos y cumplimiento *(adicional, recurrente)*
- **Objetivo:** asegurar el uso lícito de materiales y el cumplimiento de la plataforma.
- **Descripción:** gestionar licencias, atribución, copyright y políticas.
- **Entradas:** recursos; fuentes.
- **Salidas:** estado de cumplimiento.
- **Artefactos:** registro de licencias/atribuciones; comprobaciones de políticas.
- **Dependencias:** C-05, C-16.
- **Actividades:** verificación de derechos, atribución, comprobación de políticas.
- **Automatización IA:** Media (detección de riesgos).
- **Supervisión humana:** Crítica (responsabilidad legal).
- **Valor para el aprendizaje:** fuentes/recursos problemáticos a evitar.

### C-24 · Publicación
- **Objetivo:** publicar el vídeo en YouTube.
- **Descripción:** subir el vídeo y su packaging/metadatos y programar.
- **Entradas:** archivo final; packaging; metadatos.
- **Salidas:** vídeo publicado.
- **Artefactos:** registro de publicación; URL; programación.
- **Dependencias:** C-20, C-21, C-22, C-23.
- **Actividades:** subida, configuración, programación, estreno.
- **Automatización IA:** Media (automatización del proceso).
- **Supervisión humana:** Recomendada.
- **Valor para el aprendizaje:** horarios/formatos de publicación óptimos.

### C-25 · Distribución
- **Objetivo:** ampliar el alcance fuera de la página del vídeo.
- **Descripción:** promoción en otras superficies y formatos (p. ej. clips cortos).
- **Entradas:** vídeo publicado; recursos.
- **Salidas:** acciones de distribución.
- **Artefactos:** clips/cortes; publicaciones en redes; calendario de difusión.
- **Dependencias:** C-24.
- **Actividades:** generación de clips, difusión multicanal, enlaces.
- **Automatización IA:** Alta (cortes automáticos, adaptaciones).
- **Supervisión humana:** Ligera-Recomendada.
- **Valor para el aprendizaje:** canales de distribución más efectivos.

### C-26 · Métricas
- **Objetivo:** medir el desempeño del vídeo.
- **Descripción:** recoger métricas de la plataforma y de audiencia.
- **Entradas:** vídeo publicado.
- **Salidas:** conjunto de métricas.
- **Artefactos:** panel de métricas (CTR, retención, vistas, watch time, etc.).
- **Dependencias:** C-24.
- **Actividades:** recogida, agregación, visualización.
- **Automatización IA:** Alta (recogida y análisis).
- **Supervisión humana:** Ligera.
- **Valor para el aprendizaje:** **núcleo del aprendizaje**: desempeño real medible.

### C-27 · Retroalimentación
- **Objetivo:** interpretar las métricas y la respuesta de la audiencia.
- **Descripción:** convertir métricas y comentarios en señales accionables.
- **Entradas:** métricas; comentarios.
- **Salidas:** insights de desempeño.
- **Artefactos:** informe de desempeño; puntos fuertes/débiles.
- **Dependencias:** C-26, C-28.
- **Actividades:** análisis de retención, comparación con objetivos, identificación de causas.
- **Automatización IA:** Media-Alta (análisis, correlación).
- **Supervisión humana:** Recomendada.
- **Valor para el aprendizaje:** relación entre decisiones de producción y resultados.

### C-28 · Interacción con la comunidad *(adicional, recurrente)*
- **Objetivo:** gestionar la conversación con la audiencia.
- **Descripción:** moderar y responder comentarios; captar feedback cualitativo.
- **Entradas:** vídeo publicado; comentarios.
- **Salidas:** feedback cualitativo; interacción.
- **Artefactos:** comentarios destacados; temas recurrentes; correcciones de la audiencia.
- **Dependencias:** C-24.
- **Actividades:** moderación, respuesta, síntesis de feedback.
- **Automatización IA:** Media (clasificación/resumen de comentarios).
- **Supervisión humana:** Recomendada (tono y reputación).
- **Valor para el aprendizaje:** demandas y objeciones de la audiencia; ideas para C-01.

### C-29 · Aprendizaje
- **Objetivo:** capitalizar el proyecto para mejorar los siguientes.
- **Descripción:** consolidar lecciones del ciclo completo.
- **Entradas:** insights; informe de desempeño; feedback.
- **Salidas:** lecciones aprendidas.
- **Artefactos:** lecciones aprendidas; buenas prácticas; antipatrones.
- **Dependencias:** C-27, C-28.
- **Actividades:** retrospectiva, registro de lecciones, actualización de criterios.
- **Automatización IA:** Media (síntesis de lecciones).
- **Supervisión humana:** Recomendada.
- **Valor para el aprendizaje:** **cierra el bucle**; mejora C-01…C-25 en el siguiente proyecto.

---

## 5. Mapa de capacidades

> Secuencia **lógica y funcional** (no implementación, no componentes, no arquitectura). Las flechas indican flujo de proceso; el bucle final realimenta la ideación.

```
PRE-PRODUCCIÓN / INVESTIGACIÓN
  C-01 Ideación → C-02 Selección tema → C-03 Objetivos → C-04 Plan investigación
   → C-05 Descubrimiento fuentes → C-06 Recolección → C-07 Organización
   → C-08 Verificación → C-09 Análisis → C-10 Construcción de conocimiento

DISEÑO NARRATIVO
  → C-11 Diseño narrativo → C-12 Estructura → C-13 Guion → C-14 Storyboard
   → C-15 Planificación visual

PRODUCCIÓN / POST-PRODUCCIÓN
  → C-16 Producción de recursos
  → C-17 Locución
        ↘
         C-18 Edición → C-19 Control de calidad → C-20 Exportación

PUBLICACIÓN
  → C-21 Empaquetado (título+miniatura)
  → C-22 Metadatos / SEO
  → C-23 Derechos y cumplimiento
        ↘
         C-24 Publicación → C-25 Distribución

POST-PUBLICACIÓN / APRENDIZAJE
  → C-26 Métricas → C-28 Comunidad → C-27 Retroalimentación → C-29 Aprendizaje
                                                                   │
   └───────────────── (realimenta) ─────────────────────────────► C-01
```

Notas del flujo (descriptivas):
- C-23 (Derechos) actúa de forma **transversal** sobre C-05 y C-16, además de ser puerta previa a C-24.
- C-16 y C-17 son **paralelas** y convergen en C-18.
- El bloque post-publicación forma un **bucle de aprendizaje** hacia C-01/C-02.

---

## 6. Artefactos producidos

> Identificación de artefactos por capacidad (sin definir modelo de datos).

| Capacidad | Artefactos principales |
|---|---|
| C-01 Ideación | Banco de ideas; notas de ideación |
| C-02 Selección tema | Ficha de tema; justificación |
| C-03 Objetivos | Documento de objetivos; definición de audiencia |
| C-04 Plan investigación | Preguntas de investigación; plan/cronograma |
| C-05 Descubrimiento fuentes | Lista de fuentes; metadatos de fuente |
| C-06 Recolección | Documentos; transcripciones; notas; observaciones |
| C-07 Organización | Índice de materiales; etiquetas; colecciones |
| C-08 Verificación | Notas de verificación; afirmaciones marcadas; niveles de confianza |
| C-09 Análisis | Cronologías; contradicciones; relaciones; hallazgos |
| C-10 Conocimiento | Hipótesis; conclusiones; mapa de conocimiento; preguntas abiertas |
| C-11 Diseño narrativo | Ángulo/tesis; tono; arco narrativo |
| C-12 Estructura | Outline; escaleta; capítulos |
| C-13 Guion | Guion; referencias afirmación↔fuente |
| C-14 Storyboard | Storyboard; lista de planos |
| C-15 Planificación visual | Guía de estilo; lista de recursos |
| C-16 Producción recursos | Imágenes; clips; gráficos; música; SFX; registro de licencias |
| C-17 Locución | Audio de narración; timing |
| C-18 Edición | Proyecto de edición; máster; subtítulos |
| C-19 Control de calidad | Checklist de QA; informe de revisión |
| C-20 Exportación | Archivo final; derivados |
| C-21 Empaquetado | Variantes de título; miniaturas; notas A/B |
| C-22 Metadatos/SEO | Descripción; tags; capítulos; cards/end screens |
| C-23 Derechos | Registro de licencias/atribuciones; comprobaciones |
| C-24 Publicación | Registro de publicación; URL; programación |
| C-25 Distribución | Clips; publicaciones en redes; calendario |
| C-26 Métricas | Panel de métricas (CTR, retención, watch time…) |
| C-27 Retroalimentación | Informe de desempeño; fortalezas/debilidades |
| C-28 Comunidad | Comentarios destacados; temas recurrentes |
| C-29 Aprendizaje | Lecciones aprendidas; buenas prácticas; antipatrones |

---

## 7. Oportunidades de automatización

> Resumen del atributo "Automatización IA" por capacidad (descriptivo, sin elegir herramientas).

- **Potencial Alto:** C-01 Ideación, C-05 Descubrimiento de fuentes, C-06 Recolección, C-07 Organización, C-13 Guion, C-16 Producción de recursos, C-17 Locución, C-21 Empaquetado, C-22 Metadatos/SEO, C-25 Distribución, C-26 Métricas.
- **Potencial Medio / Medio-Alto:** C-02, C-03, C-04, C-08, C-09, C-10, C-11, C-12, C-14, C-15, C-18, C-19, C-23, C-24, C-27, C-28, C-29.
- **Potencial Bajo:** C-20 Exportación (proceso técnico de render).

Observación transversal (descriptiva): las capacidades de **mayor automatización** tienden a concentrarse en recolección/organización, generación de contenido y publicación; las de **mayor criticidad humana** en verificación, análisis, conocimiento, guion, calidad, empaquetado y derechos (juicio editorial, ético y legal).

---

## 8. Oportunidades de aprendizaje

> Por capacidad: información reutilizable · decisiones registradas · conocimiento para futuros proyectos. (Solo identificación; no se proponen mecanismos.)

| Capacidad | Información reutilizable | Decisiones registradas | Conocimiento para el futuro |
|---|---|---|---|
| C-01–C-03 (Ideación→Objetivos) | Ideas, temas, audiencias | Qué idea/tema/objetivo se eligió y por qué | Qué tipos de tema/objetivo rinden |
| C-04–C-07 (Investigación→Organización) | Fuentes, materiales, esquemas de organización | Plan, fuentes seleccionadas, taxonomía | Fuentes y métodos productivos por tema |
| C-08–C-10 (Verificación→Conocimiento) | Afirmaciones, hallazgos, hipótesis | Qué se verificó/aceptó/descartó | Conocimiento de caso reutilizable; antipatrones de fiabilidad |
| C-11–C-15 (Narrativa→Visual) | Ángulos, estructuras, estilos | Decisiones narrativas y visuales | Estructuras/estilos con mejor retención |
| C-16–C-20 (Producción→Exportación) | Assets, locución, ajustes técnicos | Decisiones de montaje y QA | Recursos reutilizables; errores recurrentes |
| C-21–C-23 (Empaquetado→Derechos) | Títulos, miniaturas, metadatos, licencias | Variantes elegidas; comprobaciones | Packaging/metadatos que maximizan CTR/descubrimiento |
| C-24–C-25 (Publicación→Distribución) | Horarios, canales, clips | Configuración de publicación/difusión | Momentos y canales óptimos |
| C-26–C-29 (Métricas→Aprendizaje) | Métricas, feedback, lecciones | Insights y lecciones registradas | Relación decisión→resultado; mejora del ciclo completo |

Observación: el **bucle C-26→C-29→C-01** es la principal oportunidad de aprendizaje del proceso, al conectar resultados reales con decisiones futuras.

---

## 9. Observaciones

- El proceso es **mayoritariamente lineal con un bucle de aprendizaje** final; varias capacidades (derechos, calidad) actúan de forma transversal.
- Existe una **tensión recurrente** entre capacidades muy automatizables (generación, recolección, publicación) y capacidades de **alto juicio humano** (verificación, análisis, conocimiento, guion, ética/derechos): relevante para un MVP "orientado al aprendizaje".
- Muchos artefactos del bloque de investigación (observaciones, afirmaciones, hipótesis, conclusiones, procedencia) **coinciden** con los conceptos sintetizados en los WP de Domain Discovery; aquí solo se **identifican como artefactos del proceso**, sin modelarlos.
- Todo lo anterior es **descriptivo**: no implica ninguna decisión de alcance del MVP ni de arquitectura.

---

## 10. Referencias

> Conocimiento de proceso de la industria audiovisual y de creación en YouTube, citado de forma general para verificación por el Principal Architect. No se nombran herramientas ni proveedores.

- **Producción audiovisual:** modelo estándar de fases pre-producción / producción / post-producción (literatura general de cine documental y vídeo).
- **Narrativa documental:** estructuras narrativas (p. ej. estructura en tres actos; arco narrativo; "storytelling" documental).
- **Periodismo / verificación:** estándares de verificación y atribución (coherente con WP-0009/WP-0010; ver `DOMAIN-ONTOLOGY-RESEARCH.md` y `EPISTEMIC-DOMAIN-PATTERN-RESEARCH.md`).
- **Creación en YouTube:** prácticas divulgadas sobre empaquetado (título/miniatura/CTR), retención de audiencia, capítulos, SEO de vídeo y analítica de plataforma (p. ej. material tipo "YouTube Creator" / analítica de creadores).
- **Síntesis de dominio previa:** `docs/research/DOMAIN-EVIDENCE-SYNTHESIS-MATRIX.md` (para la correspondencia entre artefactos de investigación y conceptos del dominio).

---

_Fin del estudio. Documento descriptivo del proceso de producción de documentales para YouTube: no diseña DocumentaryAI, no define arquitectura, dominio, ontologías ni workflows del sistema, no prioriza tecnologías ni herramientas y no contiene decisiones. Sirve exclusivamente como evidencia para el diseño del MVP por parte del Principal Architect._
