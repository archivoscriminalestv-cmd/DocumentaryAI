# ADR-0019 — Evidence Correlation, Coverage & Recreation Candidates (ECE)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** ECE-001
- **Relates:** ADR-0017/0018 (Case Discovery), ADR-0016 (Evidence Acquisition Engine), ADR-0010 (temporary assets vs permanent knowledge)

## Context

After discovery, DocumentaryAI has a set of evidence pointers but still reasons file-by-file.
It must reason like a professional documentary investigator: relate evidence, measure coverage,
flag conflicts, and know where the documentary has gaps — strictly before any production. This
sprint adds the Evidence Correlation Engine (`app/ece/`); it does NOT generate anything.

## Decision 1 — A typed EvidenceGraph from observable facts only

Nodes: Person, Event, Location, Evidence, Timeline, Organization. Relations: SAME_EVENT,
SAME_LOCATION, SAME_PERSON, REFERENCES, SUPPORTS, CONTRADICTS, MENTIONS, DERIVED_FROM. Every
relation is backed by an observable fact (the evidence's target, its date, literal name
mentions in its title/description) and carries the supporting evidence ids. Relations are
**never inferred** without evidence.

## Decision 2 — Conflicts are recorded, never decided

Contradictory data (e.g. different dates for the same subject) is captured as a `Conflict`
with all candidate values and `requires_verification = True`. The ECE does not choose a winner.

## Decision 3 — Coverage analysis by dimension

Chronology, People, Locations, Photographs, Videos, Documents, Audio, Maps, News are each
classified COMPLETE / PARTIAL / MISSING from discovered evidence vs the plan's minimums (and,
for people/locations/chronology, from per-entity coverage). Deterministic; no inference.

## Decision 4 — Recreation candidates: detect, never generate

The ECE only lists where a recreation *might* be needed: required needs (minimum > 0) not
covered by real evidence. Each `RecreationCandidate` records the story segment, reason, existing
coverage, available/missing evidence, a suggested recreation type (scene/animated_map/3d/
illustration/…) and the factual basis it must rely on. **No images, videos or models are
produced.**

## Decision 5 — Real evidence has absolute priority

A recreation is never proposed when sufficient real evidence exists (COVERED needs are skipped).
Recreations complement only documentary gaps and never substitute for or mix with originals.
Everything is traced and auditable (evidence ids on relations, candidates and conflicts).

## Decision 6 — Additive, deterministic, decoupled

`app/ece/` consumes the EAE `InvestigationPlan` + `DiscoveryPlan` and writes
`evidence_graph.json`, `coverage_report.json`, `conflicts.json`, `recreation_candidates.json`
into the project dir (wired into `case_discovery`). It does not touch DLE/YIE/VUE/VIS/VAI/
Composer. Same input → same output; no AI, no network.

## Consequences

- DocumentaryAI now distinguishes verified facts, real evidence, pending conflicts, documentary
  gaps and fact-based recreation candidates — the foundation for a future AI Recreation Engine
  that may only fill gaps, never replace evidence.
