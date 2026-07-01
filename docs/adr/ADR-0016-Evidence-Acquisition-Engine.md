# ADR-0016 — Evidence Acquisition Engine (foundation)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** EAE-001 (foundation) + EAE-002 (investigation planner)
- **Relates:** ADR-0002 (knowledge accumulation), ERE (evidence research), ADR-0014 (Advisor),
  ADR-0015 (VUE)

## Context

DocumentaryAI can generate cinematic images, but a credible documentary needs **real,
verifiable evidence** (photos, video, documents, news, maps, court records, official
publications…), each with a traceable origin. Today there is no permanent engine to locate,
acquire, organize and verify that evidence. We need its architecture now — built decoupled,
while a learning run executes in the background — without downloading anything yet.

## Decision 1 — A documentary library before generating video

Before narrating or generating, a case must have an **evidence library** with chain of
custody. The EAE owns this: it gathers and verifies evidence and exposes it to later phases.
Generation consuming unverified/unsourced material would undermine credibility.

## Decision 2 — Strict separation of responsibilities

```
Acquisition  →  Verification  →  Organization  →  Narrative  →  Generation
   (EAE)          (EAE)            (EAE)          (later)       (existing pipeline)
```

These never mix. The EAE does not narrate, does not decide story, does not generate. Each
concern is a separate interface (`EvidenceProvider`/`EvidenceVerifier`/`EvidenceStorage`/…)
so any can evolve independently.

## Decision 3 — Origin is mandatory; evidence ≠ generated asset

Every `Evidence` carries an `EvidenceSource` (provider + URL/ID + publisher) and a
`ChainOfCustody`. A generated AI image is **not** evidence (it lives in the ALR). Data
without a traceable source is not evidence. Verification status defaults to `UNVERIFIED`
and confidence to `UNKNOWN` — never invented.

## Decision 4 — Foundation only: contracts, no acquisition

EAE-001 ships models + Protocols + contract-only providers/verification/deduplication/
storage + a coordination-only orchestrator. **No network, no scraping, no browser
(Selenium/Playwright/BeautifulSoup), no AI/LLM.** Providers `search()→[]` and
`fetch()→NotImplementedError`; the verifier/deduplicator return `UNVERIFIED`/`UNKNOWN`;
storage only *plans* paths (no binaries). Deterministic, serializable, versioned, no
timestamps. Writes only to `output/eae/`, never `knowledge/`.

## EAE-002 addendum — Investigation Planning, Manifest, temporary workspace, coverage

Before acquiring anything, the EAE plans the investigation (`app/eae/planner/`):

- **Investigation Planning:** `EvidenceInvestigationPlanner` takes only a `CaseProfile` and
  deterministically derives `EvidenceNeed`s (category + priority + min/ideal coverage) from
  genre templates + per-entity rules (person→photo, location→map/scene-photo, event→news).
  No network, no AI. It emits a search task and an acquisition task per need.
- **Evidence Manifest:** a full project description (people, locations, timeline, expected
  material, desired coverage, priority sources, constraints, licenses, coverage status,
  pending/acquired). No binaries — planning only.
- **Documentary coverage:** each need declares minimum + ideal; `acquired` is 0 in planning
  (never invented) so everything starts `PENDING` and `% = acquired/minimum`. Acquisition
  targets the **minimum** to minimize downloads (never "download 200 photos").
- **Temporary workspace:** acquired material will live only in the project's workspace and be
  deleted automatically when the documentary is finished. Only metadata, references, hashes,
  licenses, chain of custody and knowledge persist. The binary is a means; knowledge is the
  source of truth (same principle as the DLE storage policy, ADR-0010).

Persistence: `output/eae/plans/<case_id>/plan.json` (reproducible, no timestamps).

## Consequences

- **Positive:** a stable, growable foundation for an auditable evidence library; clean
  separation lets acquisition/verification/storage grow independently behind contracts;
  zero risk to the running pipeline; fully offline-testable.
- **Accepted limitations:** no real acquisition/verification/deduplication yet; providers
  are stubs; storage stores no binaries; not integrated with ERE/CRE/Composer. All
  intentional for the foundation sprint.
