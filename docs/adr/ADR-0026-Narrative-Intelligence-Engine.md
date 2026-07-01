# ADR-0026 — Narrative Intelligence Engine (foundation)

- **Status:** Accepted
- **Date:** 2026-07-01
- **Sprint:** NAR-001 (foundation)
- **Relates:** ADR-0016 (EAE/Evidence), ECE (correlation/coverage), ADR-0021 (Knowledge Bridge),
  ADR-0022 (Production Context), VIS/VAI/Composer (consumidores aguas abajo)

## Contexto

DocumentaryAI ya aprende documentales, entiende el lenguaje audiovisual, investiga casos,
adquiere y correlaciona evidencias, detecta huecos y genera storyboard. Pero **nadie decidía
cómo contar la historia**: qué contar primero, qué ocultar, cuándo revelar, cuándo crear
tensión, cuándo respirar, cuándo usar un mapa o una fotografía y por cuánto tiempo. La
auditoría de capacidad real (2026-06-30) lo señaló como el bloqueante **#1 (MUY ALTO)** para
acercarse a calidad de documental profesional: *"no existe motor de narración/guion"*
(KBG narration 0/5, storytelling structure/narrative_type = UNKNOWN).

## Decisión 1 — Un director narrativo, no un escritor

El NAR decide **CÓMO** se cuenta la historia; **nunca la escribe**. Sin LLM, sin prompts, sin
plantillas de texto, sin OpenAI/Claude, sin generación de lenguaje. Piensa como un director
documental (Netflix/HBO/BBC/NatGeo) **antes** de escribir una sola palabra: 100% determinista,
a base de reglas objetivas, contratos y **estructuras narrativas reales**. El texto (guion/voz)
es un sprint posterior y un motor distinto.

## Decisión 2 — Salida: un plano, no un guion

La salida es un `NarrativeBlueprint`: estructura, actos, segmentos (propósito/emoción/tensión/
narración/evidencia/duración), curva emocional, decisiones de timeline, mecanismos
(hook/foreshadow/reveal/cliffhanger/payoff), preguntas abiertas estructuradas y estado
narrativo. Todo son **símbolos enumerables**, nunca prosa. Lo consumen VIS → VAI → Composer.

## Decisión 3 — Estrategias auto-puntuadas, sin `if` gigantes

Cada **estructura narrativa real** es una estrategia independiente (LINEAR, THREE_ACT, FIVE_ACT,
HERO_JOURNEY, MYSTERY_INVESTIGATION, INVESTIGATION_DRIVEN, EVIDENCE_DRIVEN, INTERVIEW_DRIVEN,
REVERSE_CHRONOLOGY, NON_LINEAR) que (1) se **auto-puntúa** según señales objetivas del caso y
(2) propone su **esqueleto de beats**. El `StructureSelector` solo ordena puntuaciones (desempate
determinista). Los **dispositivos** (cold open, flashback, flashforward, documentary reveal,
parallel narratives) son composables y también deciden su aplicabilidad de forma objetiva.
Añadir una estructura o dispositivo = una clase más; el orquestador no cambia.

## Decisión 4 — Frontera estricta de responsabilidades

El NAR **no decide** tamaño/composición de plano (VIS), cámara/color/iluminación (VAI),
tipo de corte/transiciones/mezcla (Composer), ni texto/música (motores futuros). Lo expresa como
intención en un `NarrativeDirective` y delega. La frontera está declarada como dato auditable
(`contracts.NAR_DECIDES` / `NAR_DELEGATES`) e incrustada en cada directive.

## Decisión 5 — Evidencia real primero; UNKNOWN sobre inventar

Reglas de colocación de material, en orden: (1) si la dimensión tiene **evidencia real**, se
coloca; (2) si falta y el ECE detectó un **candidato de recreación**, se justifica una recreación
explícita y trazable; (3) si no hay ni una ni otra, el hueco se convierte en una **pregunta
abierta** para el espectador. El NAR nunca fabrica material ni conocimiento; cada decisión lleva
su razón objetiva.

## Decisión 6 — Desacoplado por composición; capa anticorrupción

El NAR **no importa** las clases internas de EAE/ECE/KBG/PCX: lee sus JSON ya persistidos y los
traduce a un `NarrativeContext` (`inputs.py`). No modifica ningún motor existente (DLE, DKS, YIE,
VUE, EAE, ECE, KBG, PCX, DCA, VIS, VAI, Composer). Persistencia en `output/narrative/`, nunca en
`knowledge/`. Sin red, sin azar, sin IA; reproducible (sort_keys, sin timestamps).

## Consecuencias

- **Positivo:** cierra el bloqueante #1 de la auditoría con una arquitectura limpia, modular y
  extensible pensada para años; convierte huecos de cobertura y conflictos en decisiones
  narrativas observables; entrega a VIS un contrato de intención claro; cero riesgo para el
  pipeline en ejecución; totalmente testeable offline (22/22).
- **Limitaciones aceptadas (foundation):** los dispositivos **anotan** (énfasis + segmentos
  objetivo) y registran su decisión, sin reescritura estructural profunda (reservada a NAR-002);
  un segmento por beat (sub-segmentación futura); INTERVIEW_DRIVEN usa un proxy honesto mientras
  no exista una dimensión de cobertura de entrevistas; aún no integrado en el runner de producción
  (integración VIS por composición en un sprint posterior). Todo intencional para la fundación.

## Prueba real

`python -m app.cli.design_narrative --case-id madeleine_mccann …` sobre datos reales del caso
produce: estructura **MYSTERY_INVESTIGATION** (score 0.90, elegida sobre 9 alternativas con
razones), 12 segmentos / 4 actos / ~425 s, arco **STEADY_BUILD** con pico **PEAK** en la
revelación (narración en **silencio**), cold open que adelanta el pico, documentary reveal
dosificando la evidencia, 11 colocaciones de evidencia real, 11 recreaciones justificadas (donde
faltaba lo real) y 2 preguntas abiertas; `narration`/`music` del corpus declarados UNKNOWN, no
inventados.
