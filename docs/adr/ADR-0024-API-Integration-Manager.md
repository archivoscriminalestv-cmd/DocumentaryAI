# ADR-0024 — API Integration Manager & Production Readiness (AIM)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** AIM-001
- **Relates:** ADR-0011/0012 (YIE providers), ADR-0018 (EAE discovery HTTP), ADR-0020 (DCA)

## Context

DocumentaryAI is approaching its first end-to-end documentary. Several engines already touch
external services (yt-dlp, Wikimedia, Internet Archive, image/voice providers) but each does so
on its own. Before running a real documentary we need one place that manages, verifies and
monitors every external integration — and a production-readiness check.

## Decision 1 — One central manager; engines request capabilities, not providers

A new subsystem `app/aim/` is the single entry point for all external APIs. Engines never talk
to a provider directly: they ask the AIM for a capability (`image`, `voice`, `llm`, `evidence`,
…) and the AIM resolves the provider chain (primary → alternative) from the registry. No giant
`if`s, no provider hardcoded inside engines. This is built now; providers are integrated later
one by one without touching any engine.

## Decision 2 — Declarative public registry + capability Protocols

Each provider is a declarative `ProviderSpec` (name, category, status, version, docs,
capabilities, requires_api_key, limits, cost, timeout, retries, priority, alternative). Capability
Protocols (LLM/Image/Video/Voice/Music/OCR/Embedding/Translation/Evidence/Maps) decouple engines
from concrete providers.

## Decision 3 — Centralized secrets; never hardcode, print or persist

`SecretManager` looks up credentials in environment → `.env` → project config. It never allows
hardcoded keys, never prints them and never persists them; it only reports whether a credential
is configured.

## Decision 4 — Health Check without downloading content

Each provider implements `health()` returning available/authenticated/reachable/latency/quota/
errors. By default it is deterministic and offline (based on credentials + integration status);
a real connectivity probe is opt-in (injectable `prober`) and never downloads content.

## Decision 5 — Production Readiness Checker + JSON outputs

`python -m app.cli.system_check` reports readiness across learning/evidence/generation/knowledge
(tools, local resources, providers) and writes `output/system/{production_readiness, providers,
health_report, capability_matrix}.json`. Deterministic; never writes to `knowledge/`.

## Consequences

- DocumentaryAI has a single, auditable place to manage every external API and to see what is
  ready, what has credentials, what responds, what capabilities exist, the alternatives and what
  is still pending to integrate.
- New providers (OpenAI, ElevenLabs, Runway, Wikimedia, …) plug in via a `ProviderSpec` + adapter
  without modifying any engine.
