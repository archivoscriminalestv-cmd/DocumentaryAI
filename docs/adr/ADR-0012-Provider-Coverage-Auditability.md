# ADR-0012 — Provider Coverage & Competitive Intelligence Auditability (YIE)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** YIE-002
- **Relates:** ADR-0011 (YouTube Competitive Intelligence), ADR-0002 (knowledge accumulation), ADR-0008 (observe-only learning)

## Context

YIE-002 turns the YIE into a competitive-intelligence + audience-analytics system, pulling
data from several **independent, optional** providers (yt-dlp now; vidIQ when an official
public source exists; SocialBlade/Google Trends/Wayback/TubeBuddy in the future). Some fields
will frequently be `UNKNOWN` (e.g. channel totals are not in a per-video dump). When the
knowledge base grows to hundreds/thousands of documentaries, the future DKS must be able to
trust and audit *where each value came from* to discover real correlations.

## Decision 1 — Per-documentary `provider_coverage.json`

Every YIE-002 inspection writes a `provider_coverage.json` next to the other knowledge files.
It records, per tracked field, which provider supplied it (`yt-dlp`, `vidiq`, `pillow`, …) or
`UNKNOWN`, plus the list of available/unavailable providers and a coverage ratio. This makes
the knowledge base **fully auditable**: at any point we can answer "what did we actually know,
and from where?" for each documentary.

## Decision 2 — Providers are independent and optional; degrade to UNKNOWN

No provider is ever a hard dependency. Each implements `EnrichmentProvider`
(`available()`/`fetch()`); if unavailable it is skipped and its fields stay `UNKNOWN`. vidIQ is
included but disabled by default (no official client injected). Future providers ship as
prepared contracts only. Providers never automate a browser, never depend on HTML, and never
break the pipeline.

## Decision 3 — Additive; reuse YIE-001, never modify existing files

The new `app/yie/intelligence/` reuses YIE-001's pure functions to produce the base files
(`youtube/seo/thumbnail/popularity.json`) unchanged, and adds new files
(`channel/audience/engagement/competitive.json` + `provider_coverage.json`). The DLE and DKS
are not modified; the DKS will consume these files in a later sprint.

## Decision 4 — Only structured extraction + math; no AI, no scores

All derived metrics are pure formulas (views/day, likes/view, engagement_rate, uploads/month,
views/subscriber, velocities…). The thumbnail analysis stays objective (Pillow only: palette,
edge density, color temperature, histograms — no faces, no emotions, no CLIP, no models). No
weighted score and no recommendations are produced. `UNKNOWN` over estimating.

## Decision 5 — Reproducibility

Same URL → same JSON. The only time-dependent input is an explicit, injectable
`reference_date` (stored where it is used). The thumbnail is analyzed in a temp dir and
**discarded** (no image is persisted).

## Consequences

- The knowledge base is auditable and trustworthy as it scales; the DKS can later weight or
  filter correlations by coverage.
- Adding a real provider (e.g. an official vidIQ/SocialBlade client) is a drop-in: implement
  `EnrichmentProvider` and inject it — no orchestrator/persistence changes.
- Many fields remain `UNKNOWN` until enrichment providers are wired; this is explicit and
  measured, not hidden.
