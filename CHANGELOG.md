# Harness Rig Changelog

This file is the append-only progressive change and source-consolidation ledger for Harness Rig.

## Role of this file

Until milestone **M11**, `CHANGELOG.md` is the required migration/provenance trace for source-derived Harness Rig changes.

Every material source-derived change should record:

- source project/capability;
- source location or supplied snapshot;
- checked/reconciled date;
- Harness Rig target owner;
- disposition (`KEEP`, `ADAPT`, `REPLACE`, `DELETE_AFTER_MIGRATION`, `HISTORICAL_ONLY`);
- material semantic change;
- verification/evidence reference when available.

This is intentionally simpler than requiring object-complete Git history before implementation.

Full Git-history preservation/reconciliation is **deferred to M11**, where this ledger must be reconciled against the actual
source histories before final 1.0 qualification.

`CHANGELOG.md` is therefore the near-term audit ledger, not a permanent substitute for release/source provenance.

---


## r8.4 — 2026-09-25 — Core promotion and module-boundary convergence

### M4 dispositions

- `AuthorityRef`: `SPLIT_STABLE_INVARIANT_FROM_EXPERIMENTAL_PROVIDER_FIELDS`. Stable v1 now contains only schema, provider, subject and provider-computed authority identity; Direct file path/content canonicalization stays provider-local.
- `AuthorizationGrant`: `PROMOTE_STABLE` as bounded `harness-rig/authorization-grant/v1`. The unused Experimental `origin` field was retired; Stable v1 remains nondelegable and does not embed provider credentials/revocation infrastructure.
- `StateIdentity`: `PROMOTE_STABLE` as `harness-rig/state-identity/v1`, preserving exact revision/index/tracked/untracked/submodule identity and adding strict load/migration/integrity semantics plus an executable golden vector.
- `EvidenceReceipt`: `KEEP_EXPERIMENTAL_SHARED`; one real Harness Rig gate provider is insufficient to freeze the common envelope ahead of M9.
- `AcceptanceVerdict`: `KEEP_EXPERIMENTAL_SHARED`; the direct CLI is not a second independent consequential lifecycle consumer.
- `AssurancePlan`, direct `ExecutionPlan`/Topology shape, Context internals, `RuntimeResolution`, recurrence state, `CapabilitySet`, and `ContextManifest` remain module/adapter-owned or Experimental.

### Compatibility and failure behavior

- Added deterministic migration from the exact M3 AuthorityRef direct-file shape, Experimental AuthorizationGrant v1 and Experimental StateIdentity v1.
- Stable grant/state migrations re-key IDs when schema identity changes; AuthorityRef preserves the provider-computed authority ID while dropping provider-local source fields.
- Unknown versions, extra/missing Stable fields, invalid digests, integrity mismatch, malformed grant lifetimes and unsupported delegation fail closed.
- Provider-native evidence remains referenced rather than flattened.

### Boundary verification

- Assurance has no worker/host/model/principal selection field.
- Missing required evidence remains `BLOCKED` regardless of topology.
- An action-mismatched grant remains invalid regardless of topology.
- Technical direct formation does not satisfy missing authorization.
- Stable contracts expose no provider escape bags.

### Verified

- Re-ran all 22 M3 regression tests: PASS.
- Added and ran 15 M4 adversarial/promotion tests: PASS.
- Total unittest cases: 37/37 PASS.
- M4-V01 through M4-V05: PASS.
- Direct CLI smoke: command-gate `PASS` -> merge `ACCEPTED`.
- Canonical KB integrity: 38 references, 38 deterministic manifest rows, 0 broken local/`llms.txt` links, byte-identical manifest regeneration.

### Complexity

No registry, dependency-injection framework, central contract/evidence service, IAM system, plugin SDK, recurrence platform, generic telemetry platform, vector/RAG infrastructure, or new orchestration framework was added.

---


## r8.3 — 2026-09-25 — Experimental direct vertical slice

### Implemented

- Direct file-backed Authority.
- Single-requirement Assurance path.
- Direct/single-process Topology.
- One argv-based command/test gate with exact before/after state and bounded timeout.
- Experimental EvidenceReceipt.
- Experimental action-qualified AcceptanceVerdict.
- Git-backed StateIdentity covering revision, index, tracked/untracked content, and submodule state.
- Protected-path traversal/symlink checks.

### Verified

- 22/22 executable tests PASS.
- All M1-F01 through M1-F16 PASS.
- Required NOT_RUN cannot become PASS.
- Authority/state/input changes invalidate applicable evidence.
- Wrong-run/replayed receipt is rejected.
- Missing/expired/mismatched authorization blocks.
- Merge verdict cannot be reused as deploy verdict.
- Direct CLI smoke produces PASS receipt and ACCEPTED merge verdict.

### Maturity

All trust contracts remain **Experimental**. M4 owns promotion decisions.

---

## r8.2 — 2026-09-25 — CHANGELOG-backed source consolidation baseline

### Architecture decision

- Removed full Git-history import as an M2 progression requirement.
- M2 now establishes source baselines, migration surfaces, ownership, and capability dispositions through this CHANGELOG plus
  canonical source/provenance records.
- Full source-history import/reconciliation, old→new commit/tag mapping, import-only proof, and imported-prefix legacy checks
  move to **M11**.
- The already-built history migration tooling is retained and relabeled as M11 qualification tooling.
- M2 can therefore complete without `aiboarding.bundle`, `tacticswitch.bundle`, or `skill-kit.bundle`.

### Source consolidation ledger

| Source | Source baseline used in M2 | Harness Rig target | M2 disposition |
|---|---|---|---|
| AIBoarding | Public repository/source documentation and previously inspected project evidence, rechecked through 2026-09-25 | Context lifecycle / projections | `ADAPT` |
| TacticSwitch | Public repository/source documentation and previously inspected project evidence, rechecked through 2026-09-25 | Topology | `ADAPT` |
| Skill Kit `llm-knowledge-base-maintainer` | Canonical plugin source and project evidence, rechecked through 2026-09-25 | Context canonical knowledge base | `KEEP SEMANTICS / ADAPT` |
| Skill Kit `engineering-harness-adaptive` | Canonical plugin source and project evidence, rechecked through 2026-09-25 | Assurance | `ADAPT / REPLACE defective state-evidence path` |
| More With Less | Canonical `plugins/more-with-less/...` source, v1.0.2 baseline | Cross-cutting feature-admission doctrine | `KEEP AS GOVERNANCE SOURCE` |
| RigYard | User-supplied current source snapshot plus retained verification evidence | Product premise, host/topology/gate evidence and proposal reconciliation | `SELECTIVE ADMISSION` |

### AIBoarding → Context

Preserve/adapt:

- root agent-guidance lifecycle;
- drift/freshness lessons;
- onboarding/update/audit/compression;
- projection/distribution behavior.

Do not preserve as a second canonical knowledge source:

- duplicated factual knowledge ownership;
- duplicate freshness/state machinery after Context convergence.

### TacticSwitch → Topology

Preserve/adapt:

- minimum-sufficient topology;
- direct / one-agent default;
- fresh verification;
- one-writer ownership;
- fail-closed required worker/isolation semantics.

Move or replace:

- risk/evidence policy → Assurance;
- state identity → Harness Rig `StateIdentity`;
- evidence/acceptance → `EvidenceReceipt` / `AcceptanceVerdict`;
- host observations → HostAdapter evidence.

### Skill Kit KB maintainer → Context canonical knowledge

Preserve:

- canonical Markdown references;
- stable IDs;
- provenance;
- search-before-create;
- reconciliation;
- conflict/evidence-gap preservation;
- curated `llms.txt`;
- generated deterministic `manifest.jsonl`;
- whole-collection integrity.

Do not retain a runtime dependency on Skill Kit.

### Adaptive Engineering Harness → Assurance

Preserve/adapt:

- risk separate from reasoning difficulty;
- progressive verification ladder;
- executable oracle emphasis;
- independent review when risk requires it;
- prepared read-only specialist patterns where justified;
- verifier discovery;
- stop/completion gating where it enforces a real invariant.

Replace:

- legacy dirty-path/workspace snapshot semantics;
- evidence/state coupling superseded by the M1 trust protocol;
- duplicated Topology/routing ownership.

### Migration-surface inventory

M2 records the following source surfaces for later convergence and M11 history reconciliation:

- licenses/notices;
- state files;
- hooks;
- plugin/host manifests;
- install/update paths;
- generated distributions;
- schemas/contracts;
- tests/evals/fixtures;
- CI;
- OpenSpec material;
- agent/role definitions;
- legacy compatibility surfaces.

### Deferred to M11

M11 must perform the late source-history qualification:

- obtain/validate complete Git histories or equivalent object-complete repositories;
- preserve/import the required source histories;
- produce reproducible old→new commit/tag maps;
- verify tree equivalence and import-only commits;
- run relevant legacy deterministic checks from imported prefixes where tooling is available;
- reconcile licenses/state/hooks/install surfaces against the M2 inventory;
- reconcile this CHANGELOG against actual source history;
- resolve commit/tag signature or annotated-tag fidelity requirements.

---

## r8.1 — 2026-09-24 — Trust protocol ADR baseline

- Accepted Experimental `StateIdentity`, `AuthorizationGrant`, `EvidenceReceipt`, and `AcceptanceVerdict` semantics.
- Added the canonical security/trust boundary.
- Added stable known-bad trust fixtures.
- Deferred Stable promotion until real consumers exercise the contracts.

---

## r8.0 — 2026-09-24 — Corpus and source-baseline repair

- Repaired canonical YAML front matter.
- Made `manifest.jsonl` deterministic and generated from canonical references.
- Refreshed More With Less and OpenSpec provenance.
- Added the supplied RigYard source/evidence baseline.
