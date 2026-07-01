# ADR-0018 — Real Discovery Providers & Injectable HTTP (EAE)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** EAE-004
- **Relates:** ADR-0017 (Case Discovery & Project Workspace), ADR-0016 (Evidence Acquisition Engine)

## Context

EAE-003 shipped the Discovery architecture with provider *contracts* only. EAE-004 brings the
first five providers to life (Wikimedia Commons, Internet Archive, OpenStreetMap, Wikidata,
Wikipedia) using official JSON APIs — no scraping, Selenium, Playwright, BeautifulSoup or HTML
navigation. The discovery must stay deterministic, offline-testable, and acquisition-ready.

## Decision 1 — Injectable HTTP, never hardcoded in providers

`app/eae/discovery/http.py` defines `HttpClient` (Protocol), `Response`, `RetryPolicy`,
`RateLimiter`, and `RealHttpClient` (requests, timeout, retry, backoff, rate limit) plus a
`MappingHttpClient` for deterministic offline tests. Providers receive an `HttpClient`; they
never import `requests` or open sockets themselves.

## Decision 2 — Real providers degrade to contracts without a client

A real provider with no `HttpClient` reports `available() == False` and `discover() == []`.
The default registry built without HTTP therefore behaves exactly like the EAE-003 contracts,
so all offline tests stay green; injecting a client (real in production, fake in tests)
activates discovery.

## Decision 3 — Deterministic cache; never cache errors

`DiscoveryCache` keys on provider + category + target + sorted(terms) + language +
sorted(filters), with configurable TTL and injectable clock. Identical queries are not
repeated. Failures raise → caught → `[]` and are **never** cached.

## Decision 4 — Capability-driven resolver, no hardcoded decisions

`SourceResolver.select()` chooses providers by media, license, cost, reliability and capability,
returning ordered selections (priority → reliability → cost → name) plus discarded providers
*with reasons*. The orchestrator hardcodes nothing.

## Decision 5 — Acquisition-ready, auditable evidence

Each `DiscoveredEvidence` is self-contained (url + license + format + `extra` with coordinates/
qid/identifier/mime/api-urls) so the future Acquisition Engine downloads without re-querying.
The manifest records, per evidence, the query used and selection reason; per provider, results,
search time and cost (`provider_audit`). Determinism note: search timings live in the manifest
only and are excluded from `DiscoveryPlan.to_dict()` (same query → same results).

## Decision 6 — Documentary mindset: quality over quantity

Providers and the resolver prioritise documentary quality, source reliability, license,
reproducibility and auditability over the number of results. `UNKNOWN` over invent; no AI, no
inference.

## Consequences

- `python -m app.cli.case_discovery` produces, per case, what is needed, what was located (by
  provider) and coverage per category — with a workspace and zero binaries downloaded.
- Wiring more providers (Europeana, Flickr, LoC, …) is a drop-in once an official client exists.
- In a no-network environment the real providers degrade gracefully to `UNKNOWN`/empty.
