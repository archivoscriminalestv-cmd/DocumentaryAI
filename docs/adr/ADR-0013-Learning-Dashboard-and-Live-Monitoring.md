# ADR-0013 — Learning Dashboard & Live Monitoring (DLM)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** DLM-001
- **Relates:** ADR-0008/0009 (DLE + batch), DLE-003 (public ProgressEvent + LearningMonitor)

## Context

Learning can run for hours/days over hundreds of documentaries. The user needs a permanent
"control center" to see, at a glance and in real time, what is being learned, how much is
left, which engines are working, whether anything failed, and how the corpus grows —
without altering any pipeline decision or coupling to subsystem internals.

## Decision 1 — Consume public events only; compose, never inspect

The dashboard subscribes to the existing public `ProgressEvent` stream (DLE-003) and reads
public `knowledge/` artifacts (`learning_statistics.json`, per-doc `statistics.json`). It
**composes** the tested `LearningMonitor` for global %/ETA and adds engine health,
throughput, events and errors. It never imports private state from DLE/Queue/YIE/DKS and
never changes a contract. This keeps it 100% additive and decoupled.

## Decision 2 — Engine health at stage granularity (honest)

Public events are per *stage* (downloading/analyzing/learning/storing), not per engine. The
dashboard maps each engine to the stage that exercises it and derives a non-ambiguous status
(RUNNING/WAITING/FINISHED/FAILED/SKIPPED) from the current document's reached stage. We do
not fabricate per-engine signals that don't exist.

## Decision 3 — Deterministic with an injectable clock

All throughput/ETA/speed math takes an injectable clock; the same event stream + the same
clock produce the same state and the same rendered text (`render_dashboard` returns plain
text). This makes the dashboard fully testable offline.

## Decision 4 — Reuse the screen (ANSI) with a clean fallback

When ANSI is available (Windows Terminal/PowerShell/VSCode/CMD), the renderer clears and
re-homes the cursor to refresh in place (no flood of lines). When stdout is not a TTY, it
falls back to printing the block. Rates are suppressed below 1s elapsed to avoid absurd
startup transients; session video-hours are tracked as a delta over the cumulative baseline
(not corpus-cumulative ÷ session-elapsed).

## Consequences

- **Positive:** a permanent learning control center; `python -m app.cli.learn_dashboard`
  runs Dashboard→Queue→YIE→DLE→Knowledge→final summary in one command; nothing in the
  pipeline changes; deterministic and offline-testable; persists `dashboard_history.json`
  (cumulative) + `session_statistics.json`.
- **Accepted limitations:** engine health is stage-level (the only public signal); corpus
  fields without a public source (channels/views/likes/comments) show 0 until such an
  artifact exists; "top words/channels/countries" in the final summary await a DKS public
  API and are not fabricated.
