# ADR-0017 — Case Discovery Engine & Project Workspace (EAE)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** EAE-003
- **Relates:** ADR-0016 (Evidence Acquisition Engine), ADR-0010 (temporary assets vs permanent knowledge), ADR-0002 (knowledge accumulation)

## Context

The EAE planner (EAE-002) decides *what* evidence a documentary needs. Before acquiring
anything, DocumentaryAI must answer *where* that material could exist, and organise the case
into a temporary workspace — without downloading terabytes. This sprint builds the definitive
architecture for discovery and workspace lifecycle; it does NOT download binaries.

## Decision 1 — Discovery, not acquisition

The Case Discovery Engine turns an `InvestigationPlan` into a `DiscoveryPlan`: per need it
resolves candidate sources (where the material could be) and, for *available* providers,
discovers rich pointers (`DiscoveredEvidence`: url/provider/type/license/resolution/duration/
language/format/size/hash/reliability/date/availability/restrictions/priority). It never
downloads. Deterministic; `UNKNOWN` over invent.

## Decision 2 — Capability-driven Source Registry; no hardcoded decisions

Every provider declares `available()/supported_media()/supported_licenses()/priority()/cost()/
rate_limits()/capabilities()/reliability()`. A public `SourceRegistry` lists/sorts/filters
them and the `SourceResolver` picks candidates by capability. The orchestrator hardcodes
nothing. Providers ship as contracts (Wikimedia Commons, Internet Archive, Europeana, Flickr
Commons, Library of Congress, National Archives, BBC/Reuters/AP archives, Google Books,
OpenStreetMap, Wikidata, Wikipedia, government & public-court repositories, YouTube). Only
official APIs / defined sources — never scraping, Selenium, Playwright or HTML parsing.

## Decision 3 — Project Workspace: temporary binaries, permanent metadata

`output/projects/<case>/workspace/{downloads,photos,videos,documents,audio,maps,news,cache}`
holds downloaded material **temporarily**. The `WorkspaceManager` creates it, controls size,
cleans cache, and on `finalize()` deletes the entire `workspace/` subtree (binaries) while
**never** touching the permanent metadata at the project root (`manifest/timeline/sources/
verification/report.json`, `discovery_report.md`). Permanent = hashes, references, URLs,
licenses, metadata, knowledge, statistics, relationships — never the binaries.

## Decision 4 — Extremely rich, auditable manifest

Each discovered evidence becomes a `ManifestEntry` with origin, chain of custody, status,
duplicates, hash, license, permitted use, provider, downloaded/validated flags, cross
references and related people/places/events. The manifest records everything for a full audit
trail before acquisition begins.

## Decision 5 — Additive, deterministic, decoupled

New code lives under `app/eae/discovery/` + `app/eae/workspace.py` + a CLI
(`app.cli.case_discovery`). The DLE and the learning/generation pipelines are untouched. Same
input → same output; no `random`, no AI, no inference.

## Consequences

- DocumentaryAI can plan the full material-gathering for a case ("I need N evidences; I have
  located X; Y pending; candidate sources per category") before downloading anything.
- Wiring a real provider is a drop-in (`DiscoveryProvider` + register). Injected catalog
  providers give deterministic discovery for tests/demos.
- Storage stays tiny: only metadata persists; workspaces are disposable.
