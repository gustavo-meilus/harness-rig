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


## r8.10 — 2026-09-25 — Product CLI, migration completion, and release provenance

### Product surface

- Finalized the compact `init`, `doctor`, `spec status`, `spec archive`, `verify`, `status`, and `migrate` command surface.
- Added versioned `harness-rig/cli-envelope/v1` machine output and explicit PASS/BLOCKED/FAIL/INVALID/ERROR/TIMEOUT/CANCELLED exit categories while retaining the already-tested r8.9 raw JSON compatibility shapes.
- Added `harness-rig/config/v1` with defaults < user-global < project < CLI precedence. User-global config cannot define repository policy and malformed/unknown config fails before execution.
- Added bounded process-group cleanup for direct verifier timeout/cancellation; no process supervisor or orchestration framework was introduced.

### Migration

- Added atomic `harness-rig/migration-state/v1` for the supported r8.9 -> r8.10 product metadata/runtime migration and explicit rollback.
- Interrupted journals, mixed legacy/new state, duplicate hook ownership, unknown state schemas, and unsupported downgrade targets fail closed.
- Added deterministic synthetic `harness-rig/history-map/v1` lookup semantics without claiming real source commit maps.
- Full object-complete source-history qualification remains `PENDING_M11` and still blocks M12/1.0.

### Release provenance

- Added immutable `harness-rig/release-record/v1` binding source revision, accepted repository verdict, build workflow identity, artifact size/SHA-256, and optional attestation reference.
- A missing accepted repository verdict produces a BLOCKED release candidate; local verification does not impersonate hosted `ci / required`.
- Added `verification/release_provenance.py` for deterministic record/verify operations. No signing platform was added.

### Verified

- M10 focused adversarial suite: 18/18 PASS.
- Clean-process M3-M10 regression: 133/133 PASS (22 + 15 + 14 + 16 + 14 + 14 + 20 + 18).
- Canonical KB audit: 44 references / 44 manifest rows; root projection FRESH; manifest regeneration byte-identical.
- M10-V01 through M10-V06: PASS; retained counts and evidence are recorded in `verification/m10-verification-record.json`.

### Complexity

No package manager, daemon, migration service, signing platform, release service, config server, workflow engine, or new orchestration framework was introduced.

---


## r8.9 — 2026-09-25 — Gate platform, Playwright, architecture, and mutation verification

### Gate/provider boundary

- Added Experimental `GateClaim`/`GateOutcome` common semantics without promoting the broader evidence envelope.
- Added AST-based architecture fitness evaluation with fail-closed empty/malformed rule behavior and state-bound receipts.
- Added strict Playwright Test JSON/runtime provider: explicit required scenarios, missing/skip/no-run rejection, retry/flaky visibility, wrong-worktree/shared-data/console/network failures, native attachment references, `shell=False` execution, and explicit rejection of `--pass-with-no-tests`.
- Added bounded development mutation verification with baseline-green admission, exact text mutants, KILLED/SURVIVED sensitivity results, protected-oracle authority reopening, and retained invariant -> mutant -> detector mappings.
- Added the M9 gate/oracle modules to repository-governance-sensitive CI paths.

### Evidence boundary

- Current upstream Playwright Test 1.63.0 public CLI/reporter/retry semantics were rechecked on 2026-09-25.
- Local Node `@playwright/test` was unavailable; the local browser/Python Playwright CLI 1.57.0 is not treated as current Node Test qualification. Protocol/subprocess fixtures are retained without overclaiming a live project run.
- The supplied RigYard source snapshot still records harness-mutation-verification as planned/unimplemented source-side; Harness Rig implements a bounded analogous development gate without rewriting source history.

### Verified

- M9 focused adversarial suite: 20/20 PASS.
- M3-M9 regression is retained as clean-process-per-module evidence; final package verification records the aggregate.
- M9-V01 through M9-V06: PASS.

### Complexity

No gate registry, browser farm, mutation platform, telemetry service, plugin SDK, vector/RAG subsystem, or new orchestration framework was introduced.

---


## r8.8 — 2026-09-25 — Host capability and topology qualification

### First Stable host candidate

- Added `harness_rig.host` with Experimental/module-owned `CapabilitySet` and `RuntimeResolution` plus a deliberately narrow Stable `local-subprocess` adapter.
- Native-qualified Stable claims are limited to clean process, process launch, runtime identity observation, and crash reconciliation.
- The execution environment had no `codex`, `claude`, or `copilot` executable; no external-agent adapter was promoted.
- Added `harness-rig doctor` as a fresh `-I -S`, `shell=False` native conformance probe.

### Topology and evidence boundaries

- Requested/resolved/observed runtime facts are represented separately.
- Fresh verifier eligibility requires distinct worker and context identities, non-ownership of the implementation batch, and enforced read-only access when Assurance requires it.
- Required read-only/isolation/unknown capabilities return `BLOCKED` before launch when unsupported.
- Stable isolated-writer claims require explicitly marked formal native evidence; retained RigYard implementation/local evidence remains insufficient because the formal packet is absent.
- Technical host capability does not create or broaden `AuthorizationGrant`.

### Verified

- M3 regression suite: 22/22 PASS.
- M4 adversarial suite: 15/15 PASS.
- M5 Context suite: 14/14 PASS.
- M6 OpenSpec suite: 16/16 PASS.
- M7 repository-enforcement suite: 14/14 PASS.
- M8 host-capability suite: 14/14 PASS.
- Combined unittest discovery: 95/95 PASS.
- M8-V01 through M8-V05: PASS.

### Complexity

No multi-host registry, worker scheduler, container sandbox, plugin SDK, model-routing layer, host telemetry service, or orchestration framework was added. Unsupported worker/isolation capabilities remain explicit non-claims.

---


## r8.7 — 2026-09-25 — Trusted repository enforcement

### Same-subject CI obligations

- Added `harness_rig.repository_ci` as application-level CI evidence, not a Stable core contract.
- Added deterministic `harness-rig/ci-obligation-artifact/experimental-v1` binding policy digest, evaluated SHA, event subject, trust mode, changed paths, affected modules, mandatory obligations and expected result identities.
- Added strict `ci / required` validation that recomputes mandatory obligations and rejects missing, skipped, failed, duplicate, wrong-SHA, wrong-event, wrong-subject, wrong-producer, wrong-identity or unexpected results.
- Added `governance/ci-policy.json` with always-required ordinary and KB-integrity obligations plus conditional governance obligations for CI/resolver/policy/trust-oracle/test-oracle changes.

### GitHub workflow and trust boundary

- Added `.github/workflows/ci-required.yml` for `pull_request`, main `push`, `workflow_dispatch` and `merge_group` (`checks_requested`).
- `ci / required` uses `if: ${{ always() }}` after every prerequisite job so prerequisite failure cannot silently skip the repository verdict.
- Fork PR execution uses `pull_request`, `permissions: contents: read`, no secret references and no privileged action path; `pull_request_target` is not used.
- Added `governance/github-enforcement-requirements.json` describing install-time required-check, merge-queue, fork and governance-review settings without fabricating a CODEOWNERS identity or claiming remote ruleset installation.

### Verified

- M3 regression suite: 22/22 PASS.
- M4 adversarial suite: 15/15 PASS.
- M5 Context suite: 14/14 PASS.
- M6 OpenSpec suite: 16/16 PASS.
- M7 repository-enforcement suite: 14/14 PASS.
- Combined unittest discovery: 81/81 PASS.
- M7-V01 through M7-V05: PASS.

### Complexity

No CI service, status database, plugin framework, remote attestation system, privileged fork workflow, general policy engine, vector/RAG subsystem, or new orchestration framework was added. Live GitHub branch/ruleset and real owner configuration remain deployment controls and are not claimed as observed by this package.

---


## r8.6 — 2026-09-25 — OpenSpec first-class external SpecEngine

### Adapter and authority

- Added `DirectAuthorityProvider` vocabulary without changing Stable direct-file authority semantics.
- Added the minimum Experimental `SpecEngine` interface required by the first real spec-driven consumer.
- Added `OpenSpecAdapter` against the rechecked OpenSpec 1.13.2 public JSON CLI/agent contract; OpenSpec remains external and optional.
- Added `harness-rig/openspec-authority-profile/v1`: behavior-bearing planning artifacts, effective context/rules, custom non-task graph inputs and resolved referenced specs bind authority; default task bookkeeping, timestamps and engine version do not.
- Unresolved authority-bearing references and unsupported/incompatible versions fail closed.

### Health and archive

- Effective health now checks version compatibility, doctor/root health, planning completeness, strict validation, current apply/archive inputs and config/rule shapes rather than trusting exit zero alone.
- `skip_specs` is honored only as an OpenSpec planning state and does not waive Harness Rig verification or authorization.
- Added guarded `harness-rig spec archive`: pre-state `(A0,S0)`, bounded `spec_archive` authorization, readiness receipt, native OpenSpec archive, postcondition checks, transition receipt for `(A1,S1)`, and explicit stale-precondition reevaluation.
- Partial archive mutation, postcondition mismatch, missing authorization, required semantic-review failure and unreadable final affected specs return `BLOCKED`.
- Primary external Store roots remain unqualified for archive because current Stable StateIdentity observes the repository worktree; read-only referenced stores may contribute authority.

### Verified

- M3 regression suite: 22/22 PASS.
- M4 adversarial suite: 15/15 PASS.
- M5 Context suite: 14/14 PASS.
- M6 OpenSpec suite: 16/16 PASS.
- Combined unittest discovery before package finalization: 67/67 PASS.
- M6-V01 through M6-V06: PASS.

### Complexity

No OpenSpec source vendoring/parser, package dependency, registry, plugin SDK, general IAM system, central evidence database, vector/RAG subsystem, recurrence platform, generic telemetry platform, or new orchestration framework was added.

---


## r8.5 — 2026-09-25 — Context convergence and canonical knowledge lifecycle

### Ownership convergence

- Canonical KB is the sole owner of durable project knowledge, stable IDs, provenance/source observations, reconciliation, material conflicts/gaps, canonical-content freshness, `llms.txt`, `manifest.jsonl`, and whole-collection integrity.
- Context lifecycle owns only root `AGENTS.md`/host projection behavior, projection freshness, onboarding/install behavior, and projection compression.
- No second factual knowledge store or duplicate freshness ledger remains.

### Stable IDs and provenance

- Added deterministic rename/move, split, merge, retirement, and retired-ID non-reuse semantics.
- Added optional lineage metadata only for non-obvious split/merge/retirement relationships.
- Added structured optional `source_observations` convention with source, checked date, and version/commit when available.
- Page `updated` remains canonical edit metadata and is not external-source freshness evidence.

### Reconciliation and integrity

- Added module-local source reconciliation that preserves conflicts/gaps and rejects unsupported conclusions.
- Added retained `verification/context_kb.py` using `yaml.safe_load` for deterministic manifest generation, full collection audit, canonical fingerprinting, and root projection freshness.
- Added a short generated/maintained root `AGENTS.md` projection; it is excluded from canonical manifest inventory.

### Verified

- M3 regression suite: 22/22 PASS.
- M4 adversarial suite: 15/15 PASS.
- M5 Context suite: 14/14 PASS.
- Combined unittest discovery: 51/51 PASS.
- M5-V01 through M5-V05: PASS.
- Canonical KB audit: 39 references, 39 manifest rows, fresh AGENTS projection, byte-identical manifest regeneration.

### Complexity

No embeddings, vector database, RAG service, semantic index, second canonical store, database, plugin SDK, or orchestration framework was introduced. The M5 implementation is one small module-local semantics file plus one deterministic repository-integrity tool.

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
