# Harness Rig r8.9 prototype

This directory contains the executable direct Harness Rig trust path, M5 Context lifecycle semantics, the M6 bounded OpenSpec integration, M7 repository-CI obligation enforcement, the M8 native local-process host qualification, and the M9 bounded gate platform.

```text
Direct Authority
    ↓
Stable AuthorityRef v1
    ↓
Stable AuthorizationGrant v1
    ↓
AssurancePlan (module-owned, one required claim)
    ↓
DirectTopology (module-owned, single process / one actor)
    ↓
CommandGate
    ↓
Experimental EvidenceReceipt
    ↓
Experimental AcceptanceVerdict
```

## Runtime

The prototype uses Python standard library plus the local Git executable.

M4 promotes only `AuthorityRef`, `AuthorizationGrant`, and `StateIdentity`. The command-gate receipt and final verdict remain
Experimental because their broader provider/lifecycle consumer shapes have not yet been proven.

## Run the tests

The M3/M4 trust path remains standard-library-only and may be run with `-S`:

```bash
PYTHONPATH=prototype python -S -m unittest prototype.tests.test_m3_vertical_slice prototype.tests.test_m4_core_promotion -v
```

M5 repository-integrity tests also load the retained standards-compliant YAML tooling and therefore use normal Python with PyYAML:

```bash
PYTHONPATH=prototype python -m unittest discover -s prototype/tests -v
```

## Direct CLI smoke

```bash
PYTHONPATH=prototype python -S -m harness_rig \
  --repo /path/to/repo \
  --authority AUTHORITY.md \
  --run-id run-123 \
  --now 2026-09-25T12:00:00Z \
  --issued-at 2026-09-25T11:00:00Z \
  --expires-at 2026-09-25T13:00:00Z \
  -- python -S -c "print('ok')"
```

The CLI remains a test surface. Product CLI design is a later milestone.

## Stable M4 semantics

- `AuthorityRef` is provider-neutral: schema/provider/subject/authority identity only. Direct-file path/content canonicalization
  stays inside `DirectAuthority`.
- `AuthorizationGrant` is bounded, nondelegable v1 authorization with integrity, lifetime and exact binding checks. It is not a
  general IAM system.
- `StateIdentity` is Stable v1 exact Git-worktree state with revision, index, tracked/untracked content and submodule identity.
- Stable loaders reject unknown versions/fields/integrity failures and deterministically migrate the exact M3 serialized forms.
- M3 Experimental `AuthorizationGrant.origin` is retired during migration because no trust decision consumed it.

## Preserved direct-path semantics

- One direct `AssurancePlan` requirement; Assurance has no worker/host/model selection surface.
- One direct/single-process `DirectTopology`; topology cannot waive evidence or manufacture authorization.
- One argv-based command/test gate using `shell=False` and a bounded timeout.
- Gate mutation detection via exact state before/after.
- Gate-specific ignored/external path input bindings.
- Producer/run/gate-contract-bound Experimental `EvidenceReceipt`.
- Artifact digest verification.
- Action-qualified deterministic Experimental `AcceptanceVerdict`.
- Protected-path traversal/symlink containment helper.

## M5 Context lifecycle

- `harness_rig.context` implements only stable-ID lifecycle, source freshness comparison, and fail-closed source reconciliation.
- `verification/context_kb.py` owns deterministic YAML-backed manifest generation, whole-collection audit, canonical fingerprinting, and root `AGENTS.md` projection freshness.
- Canonical KB owns durable facts; Context lifecycle owns only the host-facing/root projection.
- Root `AGENTS.md` is not canonical knowledge and is excluded from `manifest.jsonl`.
- No vector/RAG/embedding/semantic-index subsystem exists.

## M6 OpenSpec integration

- `DirectAuthorityProvider` preserves the direct-file provider behind Stable `AuthorityRef`.
- Experimental `SpecEngine` now has only the operations required by the current consumer: availability, health, authority resolution, and archive.
- `OpenSpecAdapter` targets the verified OpenSpec 1.13.2 machine-readable CLI contract; OpenSpec remains an external optional executable.
- The default authority profile binds non-task planning artifacts, effective context/rules, schema/artifact graph, and resolved authority-bearing referenced specs.
- `harness-rig spec archive` is guarded by exact `(A0,S0)`, bounded `spec_archive` authorization, readiness evidence, postconditions, transition evidence, and final `(A1,S1)` stale-precondition reevaluation.
- Primary external Store roots remain unqualified for archive because Stable StateIdentity currently observes the repository worktree. Referenced stores are read-only authority inputs.

## Experimental spec archive CLI

```bash
PYTHONPATH=prototype python -m harness_rig spec archive \
  --repo /path/to/repo \
  --change change-id \
  --run-id archive-123 \
  --now 2026-09-25T12:00:00Z \
  --issued-at 2026-09-25T11:00:00Z \
  --expires-at 2026-09-25T13:00:00Z
```

The CLI is still an experimental test/product surface; M10 owns final CLI compatibility and exit-code/versioning policy.

## M7 repository enforcement

- `harness_rig.repository_ci` implements deterministic application-level CI obligation resolution and final required-verdict validation.
- `governance/ci-policy.json` declares always-required ordinary/KB obligations and conditional governance-sensitive paths.
- `.github/workflows/ci-required.yml` covers pull requests, main pushes, manual dispatch, and merge-group checks; `ci / required` uses `always()` after all prerequisite jobs.
- Fork PR execution uses `pull_request`, read-only contents permission, no secret references, and no privileged actions.
- Remote ruleset/CODEOWNERS configuration remains an install-time repository control and is not claimed as live-qualified by this package.

## M8 host capability qualification

- `harness_rig.host` keeps `CapabilitySet` and `RuntimeResolution` Experimental/module-owned while qualifying the narrow `local-subprocess` adapter as Stable for clean process, process launch, runtime identity observation, and crash reconciliation only.
- `harness-rig doctor` executes a fresh `-I -S` subprocess probe rather than trusting installed files.
- Requested/resolved/observed runtime facts remain distinct.
- Fresh verifier eligibility requires different worker identity, different context, non-ownership of the batch, and real read-only enforcement when Assurance requires it.
- Read-only workers, isolated workers, worktree workers, permission enforcement, fresh verifier, and isolated writer are unsupported on `local-subprocess` and required requests return `BLOCKED` before launch.
- Stable isolated-writer claims require explicit formal native evidence.

## Explicit non-goals at r8.8

Not implemented/promoted through M8:

- multi-agent orchestration;
- recurrence platform;
- central database/evidence service;
- general IAM/revocation service;
- universal environment identity;
- cryptographic remote attestation;
- public plugin SDK;
- Stable `EvidenceReceipt` or `AcceptanceVerdict` schemas;
- Stable `AssurancePlan`, `ExecutionPlan`, `CapabilitySet`, `RuntimeResolution`, or `ContextManifest`.

## Known limits

- `repository_id` remains caller-supplied; M5 converges knowledge/projection ownership but does not define repository identity.
- Direct Authority remains file-backed; OpenSpec is a separate external authority provider behind the same Stable AuthorityRef envelope.
- The local vertical slice trusts a configured local issuer set; provider-backed revocation is not implemented.
- Stable AuthorizationGrant v1 supports only nondelegable grants.
- Input bindings currently implement file-path digests only.
- Tool-version discovery is not generalized.
- Receipts/verdicts are returned as values/JSON; no persistence service exists.
- StateIdentity v1 is the current Git-worktree contract, not a generalized recursive multi-repository state framework.
- No receipt reuse policy is enabled; a different run ID is rejected.


## M9 gate providers

M9 adds Experimental common `GateClaim`/`GateOutcome` semantics plus bounded providers:

- `ArchitectureGate`: AST dependency-boundary evaluation from `governance/architecture-policy.json`;
- `PlaywrightGate`: strict required-scenario JSON/retry/runtime evaluation with provider-native artifacts;
- mutation development gate: exact invariant -> mutant -> detector sensitivity checks in temporary copies.

A missing/skipped required web scenario cannot PASS. Flaky retries remain visible and fail by default. M9 does not claim a native Node Playwright Test project run because `@playwright/test` was unavailable in the qualification runtime.
