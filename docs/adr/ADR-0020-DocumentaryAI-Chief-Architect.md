# ADR-0020 — DocumentaryAI Chief Architect (DCA)

- **Status:** Accepted
- **Date:** 2026-06-30
- **Sprint:** DCA-001
- **Relates:** all subsystem ADRs (0003–0019); ADR-0002 (knowledge accumulation)

## Context

DocumentaryAI has grown into a large ecosystem (DLE, DKS, YIE, VUE, EAE, ECE, ERE, Advisor,
CRE, CCE, VIS, VAI, SDE, VSC, VPL, ALR, CME, MGL, Composer, DLM, RDA…). Architectural
knowledge lived in conversations and scattered docs. We need a permanent, objective,
auditable model of the whole system — a "digital twin" that future decisions can query.

## Decision 1 — A read-only architectural subsystem `app/dca/`

The DCA understands the architecture and nothing else: it does not generate, learn, download,
call AI, execute the pipeline or modify any subsystem. It is deterministic and read-only, and
writes only to `output/dca/`.

## Decision 2 — Public contracts, no auto-discovery, no introspection

Engines are described in a hand-authored public `registry` (name, domain, responsibility,
inputs/outputs/artifacts, dependencies, produced/consumed capabilities, status, docs). The
`architecture_reader` lists only public docs (ADR/RFC/SPEC/README). No private code is
imported or introspected. `UNKNOWN` over invent.

## Decision 3 — Capability & dependency graphs

A capability graph (who produces/consumes each capability) and a dependency graph (direct +
transitive, cycles, isolated, leaves) are derived purely from the registry. This exposes,
objectively, what produces/consumes/needs each capability and how engines relate.

## Decision 4 — Rule-based analysis & roadmap, never subjective

The analyzer detects gaps by fixed rules: capabilities consumed but never produced,
not-integrated engines, duplicated producers, engines with no consumers, and knowledge not yet
leveraged by generation. The roadmap orders improvements by objective signals only (gap kind,
number of affected consumers, engine status) — no AI, no subjective scoring, no inference.

## Decision 5 — The DCA is the architectural source of truth

From now on, "what does DocumentaryAI know / what's missing / what to improve first" is
answered by querying the DCA, not by recalling past conversations. Advanced intelligence
(impact simulation, improvement forecasting) is deferred to later sprints; DCA-001 builds the
complete architectural model.

## Consequences

- A reproducible `architecture.json` + capability/dependency graphs + roadmap +
  recommendations + a readable report, regenerated on demand.
- The model immediately surfaces the system's key gap: learned knowledge (DLE/DKS/YIE/VUE) is
  not yet consumed by the generation pipeline.
- The registry must be kept in sync by hand as engines evolve (intentional: contracts are
  explicit and reviewed, not guessed).
