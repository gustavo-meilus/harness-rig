# Harness Rig r8.4 prototype

This directory contains the executable direct Harness Rig trust path after M4 core-promotion review.

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

From the knowledge-base root:

```bash
PYTHONPATH=prototype python -S -m unittest discover -s prototype/tests -v
```

The M3 regression suite remains in `test_m3_vertical_slice.py`; M4 promotion/boundary cases are in
`test_m4_core_promotion.py`.

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

## Explicit non-goals at r8.4

Not implemented/promoted in M4:

- OpenSpec provider or finalized `SpecEngine`;
- multi-agent orchestration;
- recurrence platform;
- host-adapter qualification platform;
- central database/evidence service;
- general IAM/revocation service;
- universal environment identity;
- cryptographic remote attestation;
- public plugin SDK;
- Stable `EvidenceReceipt` or `AcceptanceVerdict` schemas;
- Stable `AssurancePlan`, `ExecutionPlan`, `CapabilitySet`, `RuntimeResolution`, or `ContextManifest`.

## Known limits

- `repository_id` is caller-supplied; M5 owns Context identity/lifecycle convergence.
- Direct Authority is file-backed only; M6 owns OpenSpec first-class integration.
- The local vertical slice trusts a configured local issuer set; provider-backed revocation is not implemented.
- Stable AuthorizationGrant v1 supports only nondelegable grants.
- Input bindings currently implement file-path digests only.
- Tool-version discovery is not generalized.
- Receipts/verdicts are returned as values/JSON; no persistence service exists.
- StateIdentity v1 is the current Git-worktree contract, not a generalized recursive multi-repository state framework.
- No receipt reuse policy is enabled; a different run ID is rejected.
