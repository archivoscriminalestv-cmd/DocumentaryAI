# ADR-0025 — Real Provider Adapters (Production Ready)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** AIM-002
- **Relates:** ADR-0024 (API Integration Manager)

## Context

AIM-001 created the API Integration Manager (registry, secrets, health, capability matrix,
readiness). Now we turn that architecture into a working production integration layer: the
first real provider adapters, on a single contract, so any future provider is added with
minimal work and without touching any engine.

## Decision 1 — One adapter contract, no duplicated logic

`app/aim/adapters/base.py` (`AdapterBase`) implements the shared contract once: `health()`,
`capabilities()`, `authenticate()`, `execute()`, `cost()`, `limits()`, `provider_name()`,
`version()`, plus error handling, retries, circuit breaker and metrics. Concrete adapters only
define `_auth_headers`, `_health_request` and `_execute`.

## Decision 2 — Centralized, classified error handling

Adapters never raise uncontrolled exceptions: every failure becomes an `AIMError` with a class
(AUTH / TIMEOUT / QUOTA / RATE_LIMIT / SERVICE_DOWN / INVALID_RESPONSE / UNAVAILABLE). The AIM
decides retry vs fallback. On failure the result is `UNKNOWN` — never invented.

## Decision 3 — Common retry policy + circuit breaker

Bounded exponential retries (never infinite) for transient errors only; a simple per-provider
circuit breaker stops hammering a down service. Both are shared across adapters via the registry.

## Decision 4 — Provider resolution by capability, never by `if`

Engines ask for a capability (`image`, `voice`, `llm`, `evidence`); `AIM.execute(capability,
operation, ...)` resolves the provider chain (primary → alternatives) from the registry
priorities and falls back automatically. The capability matrix exposes primary/alternative/status
per capability.

## Decision 5 — Injectable HTTP; secrets never leak; real health opt-in

HTTP is injectable (`app/aim/http.py`) so all tests are offline and deterministic. Credentials
are only read by the `SecretManager` and used in request headers at call time — never printed,
persisted or logged. Metrics record provider/operation/time/success/retries/cost only — never
prompts, data or credentials. `system_check --probe` makes a minimal real call (when a key
exists) to verify connectivity; without `--probe` it is offline.

## Decision 6 — Production outputs

`output/system/{production_readiness, provider_status, provider_capabilities, provider_metrics}.json`.
Deterministic; never writes to `knowledge/`.

## Consequences

- DocumentaryAI now has a working integration layer: evidence adapters (Wikipedia/Wikidata/
  Wikimedia/Internet Archive/OpenStreetMap) and generation adapters (OpenAI/ElevenLabs/Runway/
  Replicate) on one contract, with resolution, fallback, retries and metrics.
- Adding any new provider = one adapter + one `ProviderSpec`, with no changes to DLE/DKS/VIS/VAI/
  Composer/PCX/KBG/DCA/EAE or any pipeline.
