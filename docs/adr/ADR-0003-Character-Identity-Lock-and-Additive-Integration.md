# ADR-0003 — Character Identity Lock & Additive Integration (CCE)

- **Status:** Accepted
- **Date:** 2026-06-29
- **Sprint:** CCE-001
- **Supersedes / relates:** ADR-0001 (Research is the operational unit), ADR-0002
  (Knowledge accumulation is the core value)

## Context

The pipeline (CRE/ERE → VIS → VAI → VSC → VPL → providers) already renders 26 images,
but each shot can depict a slightly different person: there is no permanent notion of
*who* the character is, independent of the scene or the provider. We need visual
**identity continuity** — the same person across every shot — without modifying the
existing subsystems (VIS/VAI/VSC/VPL/Motion/Composer/FFmpeg), and without yet using
embeddings, LoRA, IP-Adapter or fine-tuning.

Two decisions had material architectural impact and are recorded here.

## Decision 1 — Identity is a permanent, provider-independent contract

We introduce `CharacterProfile`: a serializable, versioned, deterministic description of
the character's **visual identity only**. It carries a `visual_identity_id` derived as a
stable hash of the canonical name, so the same character always resolves to the same id,
on any provider. Identity is **derived once** from the `CharacterBible` (and optionally
the `EvidenceGraph`) by the `IdentityLockEngine` and never changes between shots or
scenes. We **never invent** attributes: a sparse source (e.g. Coquito) yields a *partial*
profile whose prompt block contains only identity-stability directives.

Continuity rules and the identity prompt block are **derived from the profile**, not
hand-written, so they stay in sync with the data and remain provider-agnostic (no Imagen/
Flux/SDXL syntax — the VPL adapters translate later).

## Decision 2 — Integration is additive, via a contract applied after the VSC

The brief says "the VSC consumes `CharacterProfile` transparently" but also "do not
modify the VSC". We resolve this tension by **not editing the VSC**. Instead the CCE
exposes a stable contract — `apply_identity(request, profile)` — that returns a *new*
`VisualGenerationRequest` with the fixed identity block prepended to the prompt and the
identity negatives merged. The orchestration CLI (`generate_documentary`) invokes it
right after the VSC compiles the shots. The VSC and the VPL source remain byte-for-byte
unchanged; the only observable difference is that every request now describes the same
person.

### Alternatives considered

- *Edit the VSC to accept a `CharacterProfile`.* Rejected: violates the "do not modify
  VSC" constraint and couples the VSC to the CCE.
- *Inject identity via `GlobalStyle`.* Rejected: `GlobalStyle` is channel-level styling,
  not per-character identity; overloading it would blur responsibilities.
- *Post-process inside the VPL.* Rejected: the VPL is the execution boundary and must
  stay provider-only; identity is a planning concern.

## Decision 3 — Consistency scoring is pluggable (embedding-ready)

`IdentityConsistencyScore` compares two `CharacterProfile`s by attribute today, behind a
`ProfileComparator` interface. A future `EmbeddingProfileComparator` (facial embeddings)
can replace it without touching the rest of the system. `reference_images`
(id/provider/license/url/hash/quality) are modelled now but not downloaded.

## Consequences

- **Positive:** identity is permanent and provider-independent; the pipeline is unchanged;
  the system is generic for any public figure; the architecture is ready for embeddings/
  LoRA/IP-Adapter with no redesign (swap the comparator, fill the references).
- **Negative / accepted:** with only a text identity block (no seed-lock, no reference
  conditioning yet), consistency for data-poor characters is *directive-level*, not
  pixel-level. This is intentional for CCE-001 and the foundation the next sprint builds on.
- **Constraint:** the identity block lives at the front of the prompt; downstream prompt
  budgets must account for it (adapters already truncate/translate as needed).
