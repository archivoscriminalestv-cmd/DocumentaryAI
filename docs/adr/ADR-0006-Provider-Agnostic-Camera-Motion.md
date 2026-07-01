# ADR-0006 — Provider-Agnostic Cinematic Camera Motion (CME)

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** CME-001
- **Relates:** ADR-0004 (assets permanent), ADR-0005 (SDE deterministic diversity)

## Context

The documentary is still a sequence of static images. We want a "virtual camera
director" that plans how the camera moves for each shot — but **not** by generating
video, and **not** tied to any AI video provider (Runway/Veo/Pika/Kling/OpenAI). The plan
must be deterministic and reproducible, and must not modify any existing subsystem.

## Decision 1 — Motion is intention + physical parameters, never provider syntax

A `MotionShot` carries a `motion_type` from a structured Motion Grammar plus normalized
physical parameters (zoom %, pan/tilt °, translation as fraction of frame, roll, amplitude,
easing, duration) derived from real rates (push-in 0.3 m/s, pan 8°/s, zoom 4%/s…). It never
contains FFmpeg/Runway/Veo/Pika/Kling syntax. Any current or future engine can interpret
the same plan. This keeps the CME a planning layer, parallel to how the VSC keeps prompts
provider-agnostic.

## Decision 2 — Deterministic, rule-based, never random

Motion is chosen by narrative intent (role/style → base motion, justified), then refined by
the planner: it is constrained to the scene's camera *class* (continuity) and, if a motion
repeats within the last N shots, the least-recently-used compatible alternative is chosen
(diversity). No `random`, no Ken Burns by default. Same documentary → same camera plan,
independent of the image model — verified by tests (identical re-runs; package imports no
`random`).

## Decision 3 — Continuity, character safety, diversity as first-class constraints

- **Scene continuity:** a scene is `steady` or `handheld`; incompatible families are never
  mixed within a scene.
- **Character safety:** motion may never deform the subject. Parameters are clamped to
  identity limits (zoom ≤ 30%, pan ≤ 25°, roll ≤ 3°, translation ≤ 0.20 frame) and asserted
  on every shot.
- **Diversity:** a Motion Diversity Score (0..1) and LRU selection prevent "26 push-ins".

## Decision 4 — Additive integration; the Composer does not execute yet

The CME runs in the orchestration CLI after the VPL/ALR step (so each `MotionShot`
references a permanent `asset_id`), producing `motion_manifest.json` / `motion_history.json`
/ `motion_report.md`. VSC/VPL/ALR/Composer/FFmpeg source is unchanged. The Composer will
consume the plan in a later sprint; for now only a complete, deterministic, provider-agnostic
plan must exist.

## Consequences

- **Positive:** Coquito gets 26 motion shots, 17 distinct motion types, diversity 0.75, 0
  repetitions, identity-safe, fully reproducible; the plan is ready for FFmpeg or any AI
  video engine; nothing upstream changed.
- **Accepted limitation:** the plan is not executed/rendered in this sprint, and per-shot
  durations come from the documentary timing (scene/Nº shots) rather than from edited beats;
  a future Composer/edit pass can refine timing. Motion diversity is measured on a discrete
  motion fingerprint, not on rendered pixels.
