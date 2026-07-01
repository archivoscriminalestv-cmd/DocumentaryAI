# ADR-0009 — Automatic Batch Learning Pipeline (DLE-002)

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** DLE-002
- **Relates:** ADR-0008 (DLE), ADR-0002 (knowledge accumulation)

## Context

The DLE learns one documentary per command. To learn at scale (hundreds/thousands), we
need an unattended, resumable batch system driven by a list of URLs — without improving
analysis quality, adding AI, or touching the generation pipeline.

## Decision 1 — Persistent, resumable queue as the unit of work

A `QueueStore` persists every item and its status with atomic writes. Each state
transition is flushed to disk, so a crash/close loses nothing: on restart the queue
resumes, and items left mid-flight (DOWNLOADING/ANALYZING/LEARNING/STORING) are recovered
to PENDING and re-run (idempotent thanks to the skip index). This makes "process 100 URLs,
stop, resume" safe by construction.

## Decision 2 — Never learn the same documentary twice

A `KnowledgeIndex` maps documentary_id / video_id / canonical_url → schema version. The
predicted id is computed from the URL/file **before** downloading, so an already-learned
documentary is `SKIPPED` without a download. Re-running the whole queue re-downloads
nothing.

## Decision 3 — Schema-gated incremental learning

The skip decision compares stored schema vs current DLE schema: equal → skip; older →
re-learn. With a single 1.0 schema today this means "skip identical"; the gate is the hook
where field-level incremental merge will live when a future schema adds fields.

## Decision 4 — Decoupled sources and jobs

A source registry (`downloader.py`) recognizes a URL, predicts its id without downloading,
and says how to invoke the DLE. New sources (Vimeo/Archive.org/RTVE/BBC/…) plug in via
`register()` without touching the engine. Each documentary is a `LearningJob`; the
`LearningQueueManager` only executes jobs and never lets one failure break the batch.

## Decision 5 — Operational reports separate from knowledge

`learning_report.md` / `learning_statistics.json` / `learning_history.json` summarize the
batch (totals, hours, shots, scenes, errors, pending, remaining). The per-documentary
knowledge remains the reproducible, versioned, accumulative source of truth from ADR-0008.

## Consequences

- **Positive:** DocumentaryAI can ingest a large URL list and learn unattended, surviving
  restarts and never duplicating work; sources and jobs are pluggable; generation pipeline
  untouched; everything deterministic and offline-testable (fake engine/providers).
- **Accepted limitations:** real YouTube ingestion still requires yt-dlp + network (the
  downloader degrades gracefully and marks FAILED otherwise); processing is sequential
  (no parallel workers yet) — adequate and simplest for correctness/resumability;
  incremental field-merge is gated but not exercised (only schema 1.0 exists). Validated by
  batch-learning local videos end-to-end.
