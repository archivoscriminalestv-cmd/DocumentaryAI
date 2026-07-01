# ADR-0021 — Knowledge Bridge (Knowledge → Generation)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** KBG-001
- **Relates:** ADR-0020 (DCA: surfaced the `knowledge_unused` gap), ADR-0002 (knowledge accumulation is the core value), ADR-0008 (DLE), DKS-001, YIE, ECE/ADR-0019

## Context

DocumentaryAI accumulates a lot of learned knowledge (DKS style patterns, corpus statistics,
YouTube intelligence, advisor gaps, ECE coverage) but the DCA showed it is **not yet consumed
by generation** (`knowledge_unused`). We need a deterministic boundary that turns that
knowledge into concrete generation decisions, without yet touching the generators.

## Decision 1 — KBG is the Learning↔Generation boundary

A new read-only subsystem `app/kbg/` answers exactly one question: *given everything learned,
how should THIS documentary be generated?* It produces decisions (`GenerationKnowledge`), never
content. It does not learn, analyze video, call AI, generate prompts/images or decide
subjective aesthetics, and it modifies no existing subsystem (composition + read-only).

## Decision 2 — Public artifacts only, never internal state

Inputs are public files (`knowledge/styles/`, optionally `output/ece/…`). Missing files yield
`UNKNOWN`. No engine is imported or introspected.

## Decision 3 — Deterministic translation, never invent

The Style Resolver merges, deterministically and by genre, the relevant DKS profiles. The
Decision Engine maps observed patterns to parameters by fixed rules: a distribution's dominant
value becomes the decision (but if `UNKNOWN` dominates ≥50%, the decision stays `UNKNOWN`);
numeric summaries yield a value plus a confidence derived only from the data (median/mean
ratio). No AI, no subjective scoring, no inference of unavailable facts.

## Decision 4 — Every decision is traceable

Each `Decision` carries `origin`, `confidence` (only from available knowledge),
`knowledge_sources` and `reason`. Confidence numbers are never invented — a distribution's
confidence is its observed fraction; a numeric's is a data-derived ratio.

## Decision 5 — Prepared for, not wired into, generation

`GenerationKnowledge` is written to `output/kbg/` for VIS/VAI/Composer to consume in later
sprints. This sprint does not modify generation; it closes the knowledge→decision half of the
gap.

## Consequences

- The learned corpus now yields concrete, auditable generation decisions (e.g. pacing,
  shot duration, color temperature, lighting, cuts/min) with `UNKNOWN` where the corpus has no
  signal (e.g. shot size, narration, music).
- Next sprints shift from building engines to making VIS/VAI/Composer consume
  `GenerationKnowledge` — the point where accumulated learning starts improving output quality.
- KBG depends on DKS output schemas; if those change, the resolver/engine mappings must follow.
