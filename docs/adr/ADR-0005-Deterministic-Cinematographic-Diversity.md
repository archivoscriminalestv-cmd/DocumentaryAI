# ADR-0005 — Deterministic Cinematographic Diversity (SDE)

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** SDE-001
- **Relates:** ADR-0003 (CCE identity lock), VAI/VSC contracts

## Context

The VAI assigns composition per shot from shot type/role, so over a documentary many
shots collapse to the same look: on Coquito's 26 shots only **9 distinct compositions**
existed (avg diversity 0.21), every composition carried "clear foreground-background
separation", and lead phrases repeated 4–5×. The documentary loses cinematographic
language. We need a "director of photography" that remembers every shot and varies the
next — **without** introducing randomness (which would make the visual plan depend on
luck and the image model) and **without** modifying any existing subsystem.

## Decision 1 — Diversity is rule-based and deterministic (no `random`)

The SDE never chooses randomly. When a free dimension's base value repeats within the last
N shots, it picks the **least-recently-used** alternative from a fixed-order catalogue,
breaking ties by catalogue order. Same documentary → same visual plan, independent of the
image provider. This is essential for reproducibility (re-rendering must be stable) and is
verified by tests (two runs produce byte-identical plans; the package imports no `random`).

## Decision 2 — Integrate as VAI → SDE → VSC, additively

The SDE takes a `ShotExecutionRequest` (VAI) and returns an enriched one, modifying only
the **structured** fields the VSC already consumes (`specification.camera_language`,
`specification.composition`, and the representative `lens`/`angle`/`composition`). It does
not write full prompts, call the VPL, or touch Motion/Composer/ALR/CCE. Integration is at
the CLI compilation boundary (`build_requests`), so VIS/VAI/VSC/VPL source are unchanged.

### Alternatives considered

- *Modify the VAI to diversify.* Rejected: VAI is a protected subsystem and lacks
  documentary-wide memory.
- *Random/seeded jitter.* Rejected: non-reproducible and provider-dependent; violates the
  sprint's explicit determinism requirement.

## Decision 3 — Narrative, character and scene awareness

Not everything should differ. A **narrative mode** (interview→continuity, intimate/
observational/reflective→moderate, reconstruction/b-roll→maximum, chase→dynamic) selects
which dimensions are *free*. The SDE may change angle/size/lens/height/composition/position/
gaze/movement, but **never** identity (age/appearance/clothing — owned by the CCE) nor the
scene look (location/palette/time/weather/lighting). `continuity.py` asserts this invariant
on every shot.

## Consequences

- **Positive:** Coquito went from 9→26 distinct compositions and 0.21→0.75 average
  diversity, with lenses/sizes/angles/heights spread across the full catalogue; identity
  and scene continuity intact; VPL and ALR unchanged; the plan is fully reproducible.
- **Accepted limitation:** diversity is measured on a discrete attribute fingerprint, not
  on pixels. It enriches *planning*; perceptual variety still depends on the model. A future
  comparator could score rendered images, but that is out of scope and not required here.
- **Note:** because the SDE changes compositions, re-rendering produces new content, so the
  ALR correctly registers new permanent assets (the library grows) — consistent with
  ADR-0004.
