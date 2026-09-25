# Harness Rig M3 experimental vertical slice

This directory contains the first executable Harness Rig trust path.

```text
Direct Authority
    ↓
AssurancePlan (one required claim)
    ↓
DirectTopology (single process / one actor)
    ↓
CommandGate
    ↓
EvidenceReceipt
    ↓
AcceptanceVerdict
```

## Runtime

M3 is implemented in Python using only the standard library plus the local Git executable.

The implementation is deliberately **Experimental**. It exists to prove the trust semantics before M4 evaluates promotion
of any cross-cutting contracts.

## Run the tests

From the knowledge-base root:

```bash
PYTHONPATH=prototype python -S -m unittest discover -s prototype/tests -v
```

The `-S` on fixture Python commands avoids unrelated environment/site startup hooks in the verification environment; it is
not a Harness Rig product requirement.

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

The M3 CLI is only a test surface. Product CLI design remains a later milestone.

## Implemented semantics

- Direct file-backed `AuthorityRef`.
- Structured Git-backed `StateIdentity` with revision, logical index, tracked worktree, untracked nonignored files, and
  explicit submodule state.
- Bounded `AuthorizationGrant` validation for local issuer/principal/action/resource/authority/state/subject/time.
- One direct `AssurancePlan` requirement.
- One direct/single-process `DirectTopology`.
- One argv-based command/test gate using `shell=False` and a bounded timeout.
- Gate mutation detection via exact state before/after.
- Gate-specific ignored/external path input bindings.
- Producer/run/gate-contract-bound `EvidenceReceipt`.
- Artifact digest verification.
- Action-qualified deterministic `AcceptanceVerdict`.
- Protected-path traversal/symlink containment helper.

## Explicit M3 non-goals

Not implemented or promoted in M3:

- OpenSpec provider;
- generalized `SpecEngine`;
- multi-agent orchestration;
- recurrence;
- host-adapter platform;
- central database/evidence service;
- general IAM or revocation service;
- universal environment identity;
- cryptographic remote attestation;
- public plugin SDK;
- Stable contract schemas.

## Known Experimental limitations

- `repository_id` is caller-supplied.
- Direct Authority is file-backed only.
- The local vertical slice trusts a configured local issuer set; provider-backed revocation is not implemented.
- Input bindings currently implement file-path digests only.
- Tool version discovery is not generalized.
- Receipts/verdicts are returned as values/JSON; no persistence service exists.
- Submodule identity is sufficient for M3 dirty-state detection but is not a generalized recursive multi-repository state
  model.
- No receipt reuse policy is enabled; a different run ID is rejected.
- The prototype does not attempt to preserve evidence across policy/schema migrations.

These limitations are inputs to M4 promotion decisions, not hidden future guarantees.
