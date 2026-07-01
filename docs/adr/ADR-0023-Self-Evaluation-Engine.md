# ADR-0023 — Self Evaluation Engine (Generation → Learning Feedback)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** DCA-003
- **Relates:** ADR-0020 (DCA), ADR-0021 (KBG), ADR-0022 (Production Context), ADR-0002 (knowledge accumulation)

## Context

DocumentaryAI can learn, synthesize knowledge, produce generation decisions and use them during
generation (KBG → ProductionContext → VIS). The loop is still open: nothing measures how the
generated documentary compares to the learned corpus, nor which engine should improve next. We
want to close the cycle objectively — not with AI, not with subjective scoring, and never by
saying "this documentary is good/bad".

## Decision 1 — A new DCA capability, not a new engine

The Self Evaluation Engine lives in `app/dca/evaluation/` and is exposed via
`DocumentaryChiefArchitect.evaluate(...)`. The DCA remains the architectural brain; it gains the
ability to evaluate generation against the corpus. No existing subsystem is modified.

## Decision 2 — Public contracts only, read-only, deterministic

Inputs are public contracts: ProductionContext (corpus knowledge), VisualPlan (generated
storyboard), Evidence Coverage and Recreation Candidates (ECE), GenerationKnowledge (KBG). No
internal state, no code introspection, no LLM/AI. Same inputs → same output. `UNKNOWN` over
invent.

## Decision 3 — Measure, never interpret

The comparator reports, per dimension (pacing, average shot duration, movement, color, lighting,
evidence coverage, recreation usage, chronology): corpus value, generated value, deviation and
status. The gap analyzer turns differences into facts ("shot duration differs 72%") — never
opinions — and maps each to the responsible subsystem (shot_duration→VIS, movement/color→VAI,
lighting→VUE, coverage→EAE, chronology→ECE, …).

## Decision 4 — Objective roadmap & health, no subjective scoring

The roadmap orders improvements by objective signals only: number of consumers affected (from the
DCA capability graph), gap magnitude and architectural gaps (non-integrated engines). System
Health is computed only from data (knowledge utilization, generation coverage, corpus alignment,
evidence coverage, unknown decisions, integrated/missing capabilities).

## Decision 5 — Outputs to `output/dca/` only

`evaluation.json`, `generation_vs_corpus.json`, `improvement_plan.json`, `system_health.json`,
`evaluation_report.md`. Never writes to `knowledge/`.

## Consequences

- The full cycle closes: Corpus → DLE → DKS → KBG → ProductionContext → VIS → Storyboard → DCA
  Self Evaluation → Gap Analysis → Improvement Plan → Roadmap.
- DocumentaryAI can answer, objectively and auditably: what already matches the corpus, what still
  differs, which capabilities are unused, which engine owns each difference, and which next sprint
  has the most impact. It can begin to direct its own evolution.
