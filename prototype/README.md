# Harness Rig r8.12 prototype

The current local `verify` and `direct` commands report gate evidence only.
`spec archive` requires `--confirm-local-archive` and reports readiness and
transition checks without an authenticated authorization claim. Repository
CI is candidate-controlled project evidence. The release record uses v3
`source_revision`; v1 and v2 records cannot qualify a new release.

This directory contains the historical direct trust prototype, M5 Context
lifecycle, the bounded OpenSpec adapter, the native local-process host, gate
providers, and the compact product, migration, and provenance paths.

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
  -- python -S -c "print('ok')"
```

The raw direct invocation remains an r8.9 compatibility surface. Product callers should use `harness-rig verify`, which emits the versioned M10 machine envelope.

## Stable M4 semantics

- `AuthorityRef` is provider-neutral: schema/provider/subject/authority identity only. Direct-file path/content canonicalization
  stays inside `DirectAuthority`.
- `AuthorizationGrant` v1 retains nondelegable structural and contextual checks.
  Its unkeyed digest does not authenticate the issuer or principal.
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
- `harness-rig spec archive` requires explicit local confirmation and checks
  exact `(A0,S0)`, readiness, postconditions, transition evidence, and final
  `(A1,S1)` stale-precondition reevaluation.
- Primary external Store roots remain unqualified for archive because Stable StateIdentity currently observes the repository worktree. Referenced stores are read-only authority inputs.

## Experimental spec archive CLI

```bash
PYTHONPATH=prototype python -m harness_rig spec archive \
  --repo /path/to/repo \
  --change change-id \
  --run-id archive-123 \
  --now 2026-09-25T12:00:00Z \
  --confirm-local-archive
```

The guarded operation is unchanged; M10 adds `--json-v1` for the versioned machine envelope while retaining the r8.9 raw JSON compatibility shape.

## M7 repository enforcement

- `.github/workflows/ci-required.yml` runs ordinary tests and Context audit
  on pull requests, main pushes, manual dispatch, and merge groups. The
  `ci / required` job checks both native results using `always()`.
- Fork PR execution uses `pull_request`, read-only contents permission, no secret references, and no privileged actions.
- Remote ruleset/CODEOWNERS configuration remains an install-time repository control and is not claimed as live-qualified by this package.

## M8 host capability qualification

- `harness_rig.host` keeps `CapabilitySet` and `RuntimeResolution` Experimental/module-owned while qualifying the narrow `local-subprocess` adapter as Stable for clean process, process launch, runtime identity observation, and crash reconciliation only.
- `harness-rig doctor` executes a fresh `-I -S` subprocess probe rather than trusting installed files.
- Requested/resolved/observed runtime facts remain distinct.
- Fresh verifier eligibility requires different worker identity, different context, non-ownership of the batch, and real read-only enforcement when Assurance requires it.
- Read-only workers, isolated workers, worktree workers, permission enforcement, fresh verifier, and isolated writer are unsupported on `local-subprocess` and required requests return `BLOCKED` before launch.
- Stable isolated-writer claims require explicit formal native evidence.

## Explicit non-goals through r8.10

Not implemented/promoted through r8.10:

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


## M10 product CLI, migration, and release provenance

- Product commands are `init`, `doctor`, `spec status`, `spec archive`, `verify`, `status`, and `migrate`.
- `harness-rig/cli-envelope/v1` gives automation a versioned JSON envelope and explicit exit categories.
- Config precedence is defaults < user-global < project < CLI; user-global configuration cannot define repository policy.
- Direct verification uses process-group cleanup so timeout/cancellation cannot leave verifier descendants running.
- `harness-rig/migration-state/v1` supports r8.9 -> r8.10 plus explicit rollback; real source-history qualification remains `PENDING_M11`.
- `harness-rig/release-record/v3` binds artifact hashes and `source_revision`
  to an explicit GitHub repository, repository ID, workflow run ID, attempt,
  and `ci / required` job ID. Creation returns CANDIDATE or BLOCKED; read-only
  authenticated `gh api` calls check the hosted run.
- `verification/release_provenance.py attest` submits the validated candidate
  byte snapshot to the protected manual workflow. Artifact filenames, sizes,
  and SHA-256 values are validated before approval; record-derived summary text
  is escaped as literal Markdown. Verification parses one captured record
  snapshot and checks artifact integrity, live hosted CI, and GitHub artifact
  attestation over those bytes. V1, v2, BLOCKED, unsigned, or changed records
  cannot pass.
- The attestation environment approval records the solo owner's action over
  listed artifact hashes. It does not provide separation of duties or an
  independent CI oracle. Live ruleset observation is a separate release gate.
