# ADR-0007 — Documentary Runtime & Motion Executor (Composer)

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** COMP-001
- **Relates:** ADR-0004 (assets permanent), ADR-0005 (SDE), ADR-0006 (CME motion plan)

## Context

Every planning subsystem exists (CRE→…→CME) but the documentary was still a set of
manifests + static images. COMP-001 must produce the first real end-to-end MP4, executing
the plans, without modifying any planning subsystem.

## Decision 1 — The Composer executes, it does not decide

All cinematographic decisions already exist (identity from CCE, composition from SDE,
camera motion from CME, assets from ALR, timeline durations). The Composer only consumes
those public contracts and renders. It contains no creative heuristics — if a behavior
isn't in a manifest, the Composer doesn't invent it.

## Decision 2 — `MotionExecutor` is a permanent provider boundary

Motion execution lives behind `MotionExecutor`. `FFmpegMotionExecutor` translates the CME
parameters into `zoompan` filters (push in/out, pan, tilt, dolly, parallax, locked,
handheld; ease in/out/in-out). Future engines (Runway/Veo/Kling/Luma/Pika/OpenAI Video)
implement the same interface without touching the Composer. Parameters come **only** from
the CME — the executor never picks its own move.

## Decision 3 — Exact A/V sync via per-scene narration fitting

`timeline_audio == timeline_video` is a hard requirement. Rather than hope the TTS length
matches, the Composer fits each scene's narration to that scene's video span (speed up with
`atempo` when over, pad with silence when under). The concatenation therefore equals the
video duration exactly — no early end, no trailing silence. Music is mixed underneath the
voice (voice priority) with fades.

## Decision 4 — Non-overlapping transitions to preserve sync

Transitions are baked as per-clip fades (fade-in on the first clip, fade-out on the last,
short fade-out+fade-in between clips = dissolve). They do **not** overlap/shorten clips, so
`sum(clip durations)` stays exact and audio sync holds. True overlapping `xfade` is left as
a future option that would require recomputing the timeline.

## Decision 5 — Generated music bed when no track exists

No music asset is in the repo. The Composer generates a low ambient bed (filtered brown
noise + fades) so the mix path is real and testable; `MUSIC_TRACK=<path>` swaps in a real
track with the same mixing code. This keeps the deliverable honest (music present) without
faking a missing asset.

## Consequences

- **Positive:** first end-to-end documentary — `output/documentary/documentary.mp4` (Coquito,
  78s, 1280×720@25, H.264+AAC), 26 motion clips, synced narration, music, transitions,
  produced with one command and no manual steps. Planning subsystems untouched. Ready to
  plug AI video executors later.
- **Accepted limitations:** narration is SAPI (local TTS) because no ElevenLabs key is set —
  set `ELEVENLABS_API_KEY` for channel voice; music is a generated bed; transitions are
  non-overlapping fades; rack-focus is rendered as locked (no true focus pull in ffmpeg).
  All are swappable without architectural change.
