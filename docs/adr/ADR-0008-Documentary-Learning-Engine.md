# ADR-0008 — Documentary Learning Engine (Knowledge Acquisition)

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** DLE-001
- **Relates:** ADR-0002 (knowledge accumulation is the core value), ADR-0004 (permanent stores)

## Context

DocumentaryAI can generate documentaries, but it has no way to *learn* from existing ones.
We want a permanent engine that observes real documentaries, extracts structured
cinematographic knowledge, and stores it to inform future decisions — without modifying the
generation pipeline and without depending on heavy ML or network at analysis time.

## Decision 1 — Observe-only, additive subsystem

The DLE only observes, analyzes and stores. It does not touch VIS/VAI/CRE/CCE/ERE/VSC/VPL/
ALR/SDE/CME/Composer/FFmpeg, and (this sprint) it does not feed them either. Future sprints
will consume `knowledge/`. This keeps acquisition cleanly separated from generation.

## Decision 2 — Provider-agnostic source, deterministic analysis

The video source (YouTube via yt-dlp, or a local file) is resolved to a local path by a
provider; the analysis is identical regardless of origin. All analysis is deterministic
(ffmpeg scene detection + Pillow frame statistics + ffmpeg silence detection) — same input
produces the same knowledge. No `random`.

## Decision 3 — Never invent: UNKNOWN over guessing

Only Pillow + ffmpeg are available (no numpy/cv2/whisper). So we compute what is reliably
derivable (shot durations, cuts/min, pacing, brightness/contrast, color temperature,
dominant color, motion intensity, audio presence) and mark everything that needs a model
(`shot_size`, `composition`, face/people, interior/exterior, music/effects, ambiguous
day/night, narrative category) as `UNKNOWN`. Honesty over fabrication; the schema is ready
for better detectors later.

## Decision 4 — Injectable network/ML; failures never break the pipeline

Whisper (`Transcriber`) and YouTube download (`YouTubeDownloader`) are injectable and
degrade gracefully when absent. Every stage is wrapped: a failure is recorded as an
`AnalysisError` and the pipeline continues. Tests run fully without ffmpeg/network by
injecting a fake probe + providers.

## Decision 5 — Permanent, versioned, non-duplicating knowledge store

`knowledge/documentaries/<id>/` with a stable id (content hash for local, video id for
YouTube). Re-running the same documentary is idempotent (skipped, not duplicated; `--force`
re-analyzes). Files are reproducible (`sort_keys`, no timestamps inside the knowledge).
`knowledge/` is git-ignored (generated).

## Consequences

- **Positive:** DocumentaryAI can now learn from any documentary into a permanent,
  comparable knowledge base (each doc carries a deterministic embedding for future
  comparison); the generation pipeline is untouched; analysis is reproducible and testable
  offline.
- **Accepted limitations (swappable):** no Whisper transcription and no yt-dlp present, so
  narration is `unavailable` and YouTube download needs those tools installed; semantic
  fields and narrative categories are `UNKNOWN` until a model is added. The local-video path
  is fully functional today and was validated by dogfooding on our own `documentary.mp4`.
