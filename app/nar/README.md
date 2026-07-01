# NAR — Narrative Intelligence Engine (NAR-001)

El **director narrativo** de DocumentaryAI. Decide **CÓMO** contar una historia documental;
**nunca la escribe**. No hay LLM, no hay prompts, no hay plantillas de texto, no hay OpenAI ni
Claude, no hay generación de lenguaje. 100% determinista, a base de **reglas objetivas,
contratos y estructuras narrativas reales**.

> El texto (guion/voz) llegará en un sprint posterior. Este motor diseña la **inteligencia
> narrativa** que decide cómo debe contarse cualquier historia documental.

## Qué decide (y qué NO)

**Decide:** estructura narrativa, orden de actos/capítulos y de beats, orden temporal, propósito
de cada segmento, emoción, tensión, curva emocional, qué evidencia aparece y por qué, uso de
recreaciones, calendario de revelaciones (hook/foreshadow/reveal/cliffhanger/payoff), preguntas
abiertas para el espectador, modo e intención de narración, **dónde callar**, intención de ritmo
y duración sugerida por segmento.

**NO decide** (lo delega por contrato — ver [`contracts.py`](contracts.py)):

| Decisión | Motor responsable |
|---|---|
| tamaño/composición/secuencia de plano | VIS |
| movimiento de cámara, color, iluminación, estilo | VAI |
| tipo de corte, transiciones, mezcla de audio | Composer |
| texto de narración | futuro: NarrationEngine |
| música | futuro: MusicEngine |

Si una decisión pertenece a otro motor, el NAR **no la toma**: la expresa como intención en el
`NarrativeDirective` y deja la responsabilidad a su motor.

## Entrada → Salida

```
CaseProfile + Evidence Manifest + Evidence Graph + Coverage Report +
Recreation Candidates + Production Context + Generation Knowledge
        │   (capa anticorrupción: inputs.py → NarrativeContext)
        ▼
   NarrativeIntelligenceEngine.design()
        ▼
   NarrativeBlueprint   →   VIS → VAI → Composer
```

La salida es un **plano de la historia** (no un guion). Ejemplo de segmento (estructurado, sin
prosa):

```
Segment 09  beat=REVELATION  purpose=REVEAL
  emotion=SHOCK  tension=PEAK  duration≈25s  narration=SILENCE/LET_BREATHE
  evidence=[videos:REVEAL]  recreation=⟲  question_for_viewer=WHY·<sujeto>
```

## Arquitectura (extensible por diseño)

- **`vocabulary.py`** — la gramática cerrada del motor (estructuras, beats, emociones, tensión,
  propósitos, usos de evidencia, modos de narración, tipos de pregunta, arcos).
- **`beats.py`** — `BeatCatalog`: la semántica objetiva de cada beat (emoción/tensión/narración/
  ritmo/duración base) como DATO, no como `if` repartidos.
- **`models.py`** — todas las estructuras de salida + `NarrativeContext` (entrada normalizada).
- **`contracts.py`** — `NarrativeDirective` (NAR → VIS) y la frontera de responsabilidades.
- **`inputs.py`** — capa anticorrupción: traduce los JSON de EAE/ECE/KBG a `NarrativeContext`
  (el NAR no importa las clases internas de otros motores).
- **`strategies/`** — una **estrategia por estructura narrativa real**. Cada una se auto-puntúa
  (`fitness`) y propone su esqueleto de beats (`build_skeleton`). Añadir una = una clase más.
  - LINEAR, THREE_ACT, FIVE_ACT, HERO_JOURNEY, MYSTERY_INVESTIGATION, INVESTIGATION_DRIVEN,
    EVIDENCE_DRIVEN, INTERVIEW_DRIVEN, REVERSE_CHRONOLOGY, NON_LINEAR.
- **`devices/`** — dispositivos composables: COLD_OPEN, FLASHBACK, FLASHFORWARD,
  DOCUMENTARY_REVEAL, PARALLEL_NARRATIVES. Cada uno decide objetivamente si procede.
- **`selection.py`** — `StructureSelector`: ordena las estructuras por su propia puntuación
  (desempate determinista). **Sin `if` gigantes**: la lógica vive en cada estrategia.
- **`emotion.py`** — curva emocional + ajuste por género.
- **`pacing.py`** — duración/ritmo (usa pacing del corpus; UNKNOWN → base, lo declara).
- **`placement.py`** — qué evidencia y por qué: **real > recreación justificada > pregunta**.
- **`reveals.py`** — mecanismos de suspense + preguntas (conflictos / beats de incógnita).
- **`engine.py`** — orquestador (no contiene reglas narrativas: coordina).
- **`persistence.py`** — `output/narrative/<case_id>/blueprint.json` (reproducible, sin
  timestamps; **nunca** `knowledge/`).
- **`report.py`** — render Markdown auditable del plano.

## Reglas inquebrantables

1. **Evidencia real primero.** Si la dimensión tiene material, se coloca.
2. **Recreación solo donde falta evidencia real** y el ECE detectó un candidato (explícita y
   trazable, nunca encubierta).
3. **UNKNOWN sobre inventar.** Si no hay ni evidencia ni recreación, el hueco se convierte en una
   **pregunta abierta**. El NAR nunca fabrica material ni conocimiento.
4. **Todo trazable.** Cada decisión lleva su `reason`; la selección de estructura guarda el
   ranking completo con razones.

## CLI

```bash
python -m app.cli.design_narrative --case-id madeleine_mccann --genre true_crime \
    --title "Madeleine McCann" --subject "Disappearance of Madeleine McCann" \
    --person "Madeleine McCann" --location "Praia da Luz" --event disappearance
```

Lee `output/projects/<case>/` (EAE/ECE) + `output/kbg/GenerationKnowledge.json` y escribe
`output/narrative/<case>/blueprint.json` + `blueprint_report.md`.

## Tests

`tests/test_nar.py` (22): completitud, selección por género, evidencia real > recreación >
pregunta, recreación solo donde falta lo real, curva emocional y picos, silencio como decisión,
foreshadow→reveal→payoff, progresión del estado narrativo, frontera de responsabilidades,
procedencia (UNKNOWN no inventado), determinismo, persistencia fuera de `knowledge/`, sin
red/azar/IA.

Ver `docs/adr/ADR-0026-Narrative-Intelligence-Engine.md`.
