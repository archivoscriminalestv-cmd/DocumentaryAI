# ADR-0015 — Visual Understanding Engine (foundation)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** VUE-001 (foundation) + VUE-002 (classical CV) + VUE-003 (layout & localization)
- **Relates:** ADR-0008 (DLE), DKS-001, ADR-0014 (Production Advisor)

## Context

The corpus learner (DLE) cannot yet detect several visual facts (shot size, composition,
faces, text, evidence, scene type, objects, maps, documents) — they are stored as
`UNKNOWN`, and the Production Advisor confirms these are the biggest blind spots. We need a
permanent engine to *understand* a shot's visual content. This will be built over many
sprints; VUE-001 lays the foundation only, fully decoupled, while a learning run executes
in the background.

## Decision 1 — Modular architecture: one detector = one responsibility

Each visual capability is an independent `VisualDetector` (Protocol). The orchestrator
(`VisualUnderstandingEngine`) **only coordinates** — it runs detectors and collects their
observations; it never implements detection logic. New capabilities are added as new
detectors without touching the orchestrator or the models.

## Decision 2 — Facts only; never interpretation; UNKNOWN over invention

Detectors return objective `VisualObservation`s. No inference, no opinions, no generative
AI, no invented scores (`confidence = None` when unmeasured). When a fact cannot be
established, the value is `UNKNOWN`. Detection and interpretation are kept strictly
separate — interpretation belongs to downstream consumers (DKS/Advisor/VAI), not the VUE.

## Decision 3 — Provider-agnostic & deterministic

A frame is referenced by `FrameRef` (path + index + timestamp), independent of how it was
obtained; the package imports no CV/ML/`random` (enforced by a test). Same inputs → same
analysis. The persistence contract is reproducible (`sort_keys`, no write-time stamps).

## Decision 4 — No heavy backends yet; stable contracts first

This sprint deliberately ships **no** OpenCV/YOLO/Florence/GroundingDINO/Gemini/GPT Vision.
The skeleton detectors return `UNKNOWN`. Swapping in a real backend later must not change
models, the persistence contract, or the orchestrator — only the detector body.

## Decision 5 — Decoupled; writes never touch knowledge/

The VUE does not integrate with any subsystem in VUE-001 and never writes to `knowledge/`
(the writer targets `output/vue/` and refuses a `knowledge/` path). This keeps it safe to
develop alongside a live learning run.

## VUE-002 addendum — classical computer-vision detectors (no AI)

The first real detectors use **classical CV only** — deterministic, reproducible,
objective measurements:

- `CompositionDetector` (geometry: visual mass centroid, left/right & top/bottom balance,
  thirds offset, negative space), `ColorAnalysisDetector` (dominant color, palette,
  temperature, saturation, contrast, brightness, exposure clipping, RGB histogram),
  `EdgeDensityDetector` (edge density / texture / 3×3 detail grid), `MotionEnergyDetector`
  (abs-diff / % changed pixels / intensity from two frames), `FrameGeometryDetector`
  (resolution, aspect, orientation, letterbox/pillarbox, black margins).
- **No AI/Deep Learning/OpenCV/YOLO/Florence/SAM/GPT/Gemini.** OpenCV/numpy are not
  installed and are forbidden by the package guard; classical CV is implemented with Pillow
  + math (edge filter + threshold instead of Canny). Same input → same facts.
- Detectors measure facts but do not interpret: composition/edge/motion keep
  `value = UNKNOWN` (no categorical classification) with measurements in `facts` and
  `method = "classical_cv"`; `confidence` is always `None` (never invented).
- The orchestrator is unchanged: it only registers the new detectors. Models and the
  persistence contract are unchanged (only the `CAPABILITIES` reference list is appended,
  additively). Still writes only to `output/vue/`, never `knowledge/`.

Not implemented yet (later sprints): shot size, face detection, OCR, object detection,
maps, documents, scene classification — these remain UNKNOWN skeletons.

## VUE-003 addendum — geometry first, classification later

VUE-003 adds four classical layout/localization detectors (Pillow + math): subject
localization (salient-region bbox/center/occupancy/distances/free-margin/position),
layout balance (h/v distribution, symmetry, concentration, dispersion), visual weight
(left/right/top/bottom + center of gravity) and empty space (% empty, largest empty
region, negative-space distribution).

**Decision: the system first learns the objective GEOMETRY of the shot; cinematic
CLASSIFICATION comes later.** The subject is found by classical saliency (edges/contrast),
not object recognition — `UNKNOWN` when nothing stands out. These facts are the substrate
on which future `ShotSizeDetector` (from occupancy/margins) and a real `CompositionDetector`
(from balance/weight/empty-space) will be built, without re-measuring pixels. Detection and
interpretation stay strictly separate; all additive (new payload models + appended
`CAPABILITIES`), models/contract/orchestrator architecture unchanged; writes only to
`output/vue/`.

## Consequences

- **Positive:** real, objective, deterministic visual measurements now available behind the
  stable VUE interfaces; future detectors (real shot-size/OCR/etc.) drop in without touching
  models/contract/orchestrator; zero risk to the running pipeline.
- **Accepted limitations:** classical CV only (no semantic categories like shot size yet);
  not integrated with DLE/DKS/Advisor/VAI/Composer; no CLI; OpenCV-specific algorithms
  (e.g. true Canny) deferred until/if the dependency is added.
