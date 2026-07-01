# ADR-0004 — Assets are Permanent & Content-Addressed (ALR)

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** ALR-001
- **Relates:** ADR-0002 (Knowledge accumulation is the core value), ADR-0003 (CCE)

## Context

The VPL writes rendered images to `output/documentary/images/` with documentary-relative
names (`S01.png`…). Every render recreates that folder, so previous images are
overwritten or lost. This contradicts the project's core value (ADR-0002): DocumentaryAI
must *accumulate* an audiovisual knowledge base, not behave like a throwaway renderer.

We need a permanent library where no generated asset is ever lost, without modifying any
existing subsystem (CRE/CCE/ERE/VIS/VAI/VSC/VPL/Composer/Motion/FFmpeg).

## Decision 1 — Assets are permanent and content-addressed

Every generated image becomes an `Asset` with a stable `asset_id = asset_<sha256[:8]>`,
derived from its **content**. Consequences:

- **Permanent:** never deleted, never overwritten (storage refuses to rewrite an existing
  `asset_id` file), never renamed.
- **Render-independent:** the id does not depend on the documentary, the scene, the shot
  or the temporary filename.
- **Natural deduplication:** identical bytes resolve to the same id, so re-rendering the
  same content adds a *reference*, not a copy.

Perceptual near-duplicates (close pHash) are **flagged** (`possible_duplicates`) but never
deleted or merged — that is a later, human/embedding decision.

## Decision 2 — The render references assets; it does not own them

`output/documentary/images/` is demoted to a temporary scratch directory. The source of
truth is `library/`. A `documentary_manifest.json` maps `project → scene → shot →
asset_id`; it never points at render-temporary image paths as truth. Re-rendering a
documentary produces new *references* to existing assets.

## Decision 3 — Additive integration after the VPL

The ALR is a separate layer. The orchestration CLI calls `AssetLibrary.ingest_render()`
**after** the VPL produces the manifest: it hashes each image, deduplicates, copies new
content into `library/`, updates `asset_registry.json`, and returns `asset_id`s + permanent
paths. The VPL and all other subsystems are unchanged.

### Alternatives considered

- *Make the VPL write to the library directly.* Rejected: would modify the VPL and couple
  generation to storage policy.
- *Sequential ids (`asset_000001`).* Rejected as the identity: not content-addressed, so
  no natural dedup and order-dependent. (Used only illustratively; the real id is the
  content hash.)

## Decision 4 — Durability per ingest

Each `ingest_asset` persists both the per-asset metadata file and the registry index, so a
crash mid-render never loses already-ingested assets.

## Consequences

- **Positive:** no asset is ever lost; re-renders only grow the library and increase reuse;
  the library becomes a permanent, searchable audiovisual knowledge base; pipeline
  unchanged; ready for versioning (`parent_asset`) and future embedding-based dedup.
- **Accepted limitation:** because the VPL cache reuses the original `shot_id` for
  within-render reuse shots, per-render *reference* counts collapse those duplicates; the
  `documentary_manifest` still records every shot position → asset_id. Acceptable and not
  worth modifying the VPL.
- **Disk growth:** the library only grows. `library/` is git-ignored (binaries); pruning,
  if ever needed, is an explicit future tool — never an automatic deletion.
