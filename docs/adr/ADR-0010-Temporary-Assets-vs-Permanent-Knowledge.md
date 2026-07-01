# ADR-0010 — Temporary Assets vs Permanent Knowledge

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** DLE-002A
- **Relates:** ADR-0002 (knowledge accumulation), ADR-0008 (DLE), ADR-0009 (batch learning)

## Context

To learn from thousands of documentaries we cannot keep every downloaded video — storage
would explode. But the analysis already produces everything we actually need (knowledge,
statistics, embeddings, reports). The video is only a means to an end.

## Decision

**Knowledge is permanent; the video is a temporary means to obtain it, not part of the
database.** The source of truth is the knowledge in `knowledge/` (URL, metadata, analysis,
statistics, embeddings, reports), which is reconstructable from its JSON alone and never
depends on the video file.

The video lifecycle is governed by a **decoupled storage policy** (`app/dle/storage_policy/`),
selected by `LEARNING_STORAGE_MODE`:

- **TEMPORARY (default):** download into a temporary workspace (`cache/learning/<key>/`),
  analyze, store knowledge, then delete the video automatically — on success *and* on error.
- **ARCHIVE:** keep the video (moved to `archive/videos/`) — only for reference material.
- **STREAM:** interface reserved, not implemented (raises `NotImplementedError`).

The Downloader never decides what happens to the file; the policy does. The policy is
injected into the DLE engine and manages the workspace context (the only thing this sprint
changes — the *video lifecycle*, not the analysis, queue, knowledge store, format,
statistics or embeddings).

## Safety

Deletion is strictly bounded: `safe_rmtree` removes only paths inside the policy's temporary
root and **refuses** `knowledge/`, `library/`, `output/`, `assets/`. Temporary videos are
never written under `knowledge/`.

## Consequences

- **Positive:** thousands of documentaries can be learned using only the space of the
  extracted knowledge; no manual cleanup; no residue (even on failure); knowledge remains
  permanent, reproducible, versioned and accumulative; new storage behaviors (e.g. STREAM)
  plug in without touching the engine.
- **Accepted limitations:** ARCHIVE is opt-in for reference videos and does grow disk;
  STREAM is only an interface for now; for local `--video` inputs the user's own file is the
  source and is never deleted (only downloaded temporaries are). Default behavior is
  backward-compatible (videos were already auto-deleted via a temp dir; now it is explicit,
  configurable, under `cache/`, and decoupled).
