# ADR-0022 — Production Context (the Knowledge↔Generation contract)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** PCX-001
- **Relates:** ADR-0021 (KBG / GenerationKnowledge), ADR-0020 (DCA), ADR-0002 (knowledge accumulation)

## Context

KBG-001 produces `GenerationKnowledge`, but if each generation engine read KBG (or
`knowledge/`) directly we would create cross-dependencies and brittle refactors. We need a
single, permanent contract that every generation engine consumes, decoupling generation from
the origin of knowledge. This sprint starts DocumentaryAI's vertical integration.

## Decision 1 — `ProductionContext` is the single entry point for generation

A tiny, decoupled subsystem `app/pcx/` defines `ProductionContext`: everything a documentary
needs to know before being generated. Today it carries only the generation decisions; it is
designed to admit (without breaking contracts) evidence coverage, recreation policy, project
constraints, target platform, duration, audience, language, case metadata and preferences.
VIS, VAI, Composer, Narration, Music and future engines will consume **only** this contract.

## Decision 2 — Generation engines never know the knowledge source

VIS (and future engines) must not import KBG, `knowledge/`, DLE, DKS, YIE, EAE or ECE. All
communication happens through `ProductionContext`. The contract is a Protocol
(`ProductionContextLike`) so the concrete class can evolve without touching engines.

## Decision 3 — Builder constructs, never decides; UNKNOWN is filtered

`ProductionContextBuilder` loads `GenerationKnowledge` (object, JSON, or via KBG), drops every
`UNKNOWN` decision, and builds a deterministic context. It never invents and tolerates missing
artifacts (empty context). The context is in-memory only — no new persistence, nothing written
to `knowledge/` or `output/`.

## Decision 4 — Context has priority only when known and confident

A context decision overrides a generator heuristic only when it exists, is not `UNKNOWN` and
has sufficient confidence. Otherwise the engine behaves exactly as before. The context does not
replace heuristics; it prioritizes them when real knowledge is available.

## Decision 5 — VIS integrated by composition, behavior preserved

`build_visual_plan(..., context=None)` is additive: with no context (or only `UNKNOWN`
decisions) VIS produces an identical storyboard. Known decisions map to existing VIS levers
(shot duration → shot count, movement, lighting, color temperature, pacing).

## Consequences

- `Learning → … → KBG → GenerationKnowledge → ProductionContextBuilder → ProductionContext →
  VIS → Storyboard` works end-to-end; learned knowledge starts influencing generation.
- New generation engines plug into the same contract; no cross-dependencies.
- Future context fields (evidence/recreation/platform/…) extend the contract without breaking
  existing consumers.
