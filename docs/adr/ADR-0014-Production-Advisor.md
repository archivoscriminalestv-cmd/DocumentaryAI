# ADR-0014 — Production Advisor (decoupled knowledge analysis)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** ADV-001 (scaffold) + ADV-002 (gap analyzer)
- **Relates:** ADR-0002 (knowledge accumulation), ADR-0008 (DLE), DKS-001, ADR-0013 (DLM)

## Context

We need a subsystem that later answers strategic questions about DocumentaryAI: what is
missing to reach the corpus's quality, where our pipeline differs from successful
documentaries, which capabilities would have most impact, what to build next. Crucially,
this work must start **while a long learning run is writing `knowledge/`**, so it must be
completely decoupled and must not interfere.

## Decision 1 — Read-only, decoupled consumer of public artifacts

The Advisor only **reads public `knowledge/` artifacts** (e.g. `learning_statistics.json`,
`styles/`). Reads are defensive: a missing or half-written file (concurrent writer) is
treated as unavailable and never raises. The Advisor never imports or depends on
DLE/Queue/YIE/DKS/DLM internals at runtime — it consumes their persisted public output.

## Decision 2 — Never write into `knowledge/`

All Advisor output goes to `output/advisor/` (`advisor_report.json` + `.md`). This keeps the
learning run's data untouched and avoids any contention or format risk in `knowledge/`.

## Decision 3 — Pluggable interfaces; scaffold logic only

`KnowledgeSource`, `GapAnalyzer`, `Recommender`, `ReportSink` are Protocols. This sprint
ships minimal deterministic baselines (capability-gap enumeration + 1:1 recommendations)
with clear extension points. No complex corpus↔pipeline comparison or impact scoring yet —
those land in later sprints by swapping the analyzer/recommender, not the orchestrator.

## Decision 4 — Never invent; UNKNOWN by default

Capability coverage in the corpus (interviews/maps/documents/…) is `UNKNOWN` until the
corpus exposes a public signal for it. `pipeline_supported` records known facts about our
own generation pipeline (narration/music yes; real footage no). Determinism throughout
(no `random`).

## ADV-002 addendum — real corpus↔pipeline gap analyzer

Status upgraded from scaffold to **Accepted**. The Advisor now compares the corpus's
*measured* distributions (DKS `styles/*.json`: movement/lighting/color/pacing/cuts·min)
against known pipeline capabilities, still **read-only** and **deterministic**:

- **Capability Coverage Matrix** (`capability_matrix.json`): per dimension/capability →
  corpus observed?, pipeline yes/no/UNKNOWN, status SUPPORTED/MISSING/UNKNOWN.
- **Gap Analyzer** (`gap_report.json`): blind-spots (dimensions the corpus can't measure,
  e.g. shot_size/composition 100% UNKNOWN), measured categories the pipeline lacks, and
  production capabilities missing from the pipeline.
- **Impact ranking** strictly by **observed frequency** (no arbitrary weights); gaps
  without corpus evidence are listed as `frequency = UNKNOWN` after the quantified ones.
- **Corpus completeness**: under-represented categories by a pure data rule (< half the
  mean share) → which documentary types to keep learning.
- **Confidence** classified **only** by sample size (shots/docs thresholds).
- **Top discoveries** (`discoveries.json`): deterministic aggregates (dominant category per
  dimension, numeric extremes), no generative AI.
- Main human report: `production_advisor.md`.

## Consequences

- **Positive:** strategic, evidence-based analysis runs safely in parallel with a live
  learning run; fully decoupled, deterministic, offline-testable; honest UNKNOWN where the
  corpus has no signal.
- **Accepted limitations:** production-capability coverage (interviews/maps/documents/real
  footage) stays UNKNOWN until the corpus exposes those signals (so those gaps are
  unquantified); recommendation impact/effort are not subjectively scored (priority =
  observed frequency); still no CLI (programmatic orchestrator + persistence).
