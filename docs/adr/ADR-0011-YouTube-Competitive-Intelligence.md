# ADR-0011 — YouTube Competitive Intelligence (YIE)

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** YIE-001
- **Relates:** ADR-0002 (knowledge accumulation is the core value), ADR-0008 (DLE: observe-only learning), ADR-0009 (batch learning pipeline)

## Context

The DLE learns *how* documentaries are made (cinematography). It says nothing about *why*
they perform on YouTube. DocumentaryAI targets a competitive platform, so we want a permanent
knowledge base about video performance, channels, SEO, thumbnails and popularity — to later
answer questions like which durations/titles/thumbnails/channels/cases work best. This sprint
builds the acquisition infrastructure only; it does NOT change generation.

## Decision 1 — Independent, additive subsystem `app/yie/`

The YIE is a self-contained subsystem with its own models, analyzers, provider, orchestrator
and persistence. It does not modify VIS/CRE/CCE/ERE/VAI/VSC/VPL/ALR/SDE/CME/Composer/FFmpeg
nor the DLE. It only reads a URL and writes knowledge.

## Decision 2 — Provider-agnostic and deterministic

A `YouTubeProvider` resolves metadata + thumbnail; the analysis is identical regardless of
source and fully deterministic (rules + Pillow). The provider (yt-dlp runner + HTTP) is
injectable, so all network is mockable and tests run offline. Same URL → same JSON.

## Decision 3 — Never invent, no AI, no scores

Missing data is `UNKNOWN` (text) or `None` (numeric); nothing is fabricated or inferred. SEO
uses deterministic rules only (no AI). The thumbnail is analyzed with Pillow for **objective**
attributes only (resolution, brightness, contrast, saturation, color temperature, dominant
color, edge-density text estimate, histograms) — no face/person detection, no CLIP, no models.
Popularity stores **derived metrics only** (views_per_day, likes_per_view, comments_per_view,
engagement_rate, age_days); no weighted score is created in this sprint.

## Decision 4 — Reproducibility of time-derived metrics

Some metrics depend on "now" (age_days, views_per_day). To keep "same URL → same JSON", the
engine takes an explicit injectable `reference_date` (default: today). The chosen reference is
stored in `popularity.json`; nothing else carries a timestamp.

## Decision 5 — Separate persistence, shared doc dir

YIE writes `youtube.json`, `seo.json`, `thumbnail.json`, `popularity.json` into the same
`knowledge/documentaries/<doc_id>/` used by the DLE, but in **separate files** — each
subsystem owns its own data and the DLE JSONs are never touched. `doc_id` uses the DLE's
`doc_yt_<video_id>` convention so both subsystems align on the same documentary.

## Decision 6 — Integration is Queue → YIE → DLE (best-effort)

The `LearningJob` runs the YIE for YouTube sources before the DLE, as an optional, injected
dependency. It is best-effort: any YIE failure is swallowed and the DLE still runs. The DLE is
unchanged. `learn_queue` wires a real YIE automatically; the offline tests inject fakes.

## Decision 7 — DKS contract only

The Documentary Knowledge Synthesizer is NOT modified. The YIE only establishes the file/schema
contracts (`youtube/seo/thumbnail/popularity.json`); a later sprint will have the DKS consume them.

## Consequences

- Permanent, reproducible competitive-intelligence knowledge accrues alongside cinematographic
  knowledge, with the same observe-only discipline.
- No recommendations, scoring or generation changes yet — purely infrastructure.
- Real metadata/thumbnail fetching needs yt-dlp + network; without them the YIE degrades to
  `UNKNOWN` and never breaks the pipeline.
