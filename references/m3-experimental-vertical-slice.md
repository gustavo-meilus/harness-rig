---
id: harness-rig-m3-experimental-vertical-slice
title: M3 experimental direct vertical slice
summary: Executable Direct Authority to Assurance to direct Topology to command gate to EvidenceReceipt to action-qualified
  AcceptanceVerdict path, with all M1 fixtures and M3 verification checks passing while contracts remain Experimental.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- Harness Rig M3 experimental direct vertical-slice implementation and executable verification, 2026-09-25
- 'Local runtime evidence: Python 3.13.5 and Git 2.47.3, 2026-09-25'
---
# Status

```text
milestone: M3
revision: r8.3
result: PASS
contract maturity: EXPERIMENTAL
implementation: prototype/harness_rig/
tests: 22/22 PASS
next: M4
```

# What M3 proves

Harness Rig now has one complete executable trust path:

```text
Direct Authority
    ↓
one Assurance requirement
    ↓
Direct/single-process Topology
    ↓
one command/test gate
    ↓
experimental EvidenceReceipt
    ↓
experimental action-qualified AcceptanceVerdict
```

The happy path produces:

```text
gate outcome: PASS
receipt certified state: exact pre/post-equal StateIdentity
verdict outcome: ACCEPTED
decision_for: merge
```

Machine evidence:

```text
verification/m3-verification-record.json
verification/m3-fixture-results.json
verification/m3-unittest-output.txt
verification/m3-cli-smoke.json
```

# Implementation boundary

The implementation lives under:

```text
prototype/harness_rig/
```

It uses only the Python standard library and the Git executable.

This is intentionally a prototype package. M3 does not create a generalized kernel package or Stable public API.

# Direct Authority

`DirectAuthority` hashes one repository-contained authority file and returns an Experimental `AuthorityRef`.

M3 does not require OpenSpec.

# Assurance

`AssurancePlan` has exactly one `AssuranceRequirement` in the vertical slice:

```text
claim_id
gate_id
gate_contract_version
decision_for
require_authorization
```

Assurance does not select workers.

# Topology

`DirectTopology` records one principal and one formation:

```text
direct-single-process
```

It does not waive the Assurance requirement and does not issue/broaden authorization.

# StateIdentity

The M3 state implementation observes:

```text
HEAD / UNBORN revision
HEAD tree
logical Git index
tracked worktree bytes/types/symlinks/deletions
untracked nonignored files
submodule recorded gitlink
submodule observed HEAD/content/status
```

Consequences verified at runtime:

- commit-during-session remains visible even when the worktree becomes clean;
- identical repository content on a new revision preserves `content_id` while changing revision/state identity;
- staged-only edits change index/state identity;
- dirty consumed submodule state is visible.

# Command gate

The M3 gate:

- invokes an argv directly with `shell=False`;
- resolves and records the executable;
- optionally requires an expected executable identity;
- uses a bounded timeout;
- captures state before and after;
- returns `MUTATED` if relevant repository state changes during verification;
- returns `NOT_RUN` when no command is supplied;
- records gate-specific file input bindings;
- records native stdout/stderr digests plus configured artifact digests.

Required `NOT_RUN`, `BLOCKED`, `FAIL`, or `MUTATED` does not satisfy acceptance.

# EvidenceReceipt

M3 receipts bind:

```text
claim
subject
authority
state_before
state_after
certified_state
material file input bindings
producer
run
gate + contract version
resolved executable
outcome
artifact digests
receipt integrity
```

No universal environment identity was introduced.

The M3 implementation directly reuses the useful RigYard pattern of binding evidence to run/producer/gate/artifact identity,
while keeping detailed tool-native evidence outside the generic receipt.

# AuthorizationGrant

M3 validates:

```text
issuer
principal
action
resource
authority binding
state binding
subject binding
issued time
expiry
nondelegable principal match
```

Missing required authorization produces `BLOCKED`.

M3 has no general IAM or provider-backed revocation service.

# AcceptanceVerdict

Acceptance validates:

```text
receipt integrity
claim / subject
authority freshness
state freshness
input-binding freshness
gate identity / contract version
producer run identity
required PASS outcome
artifact integrity
required AuthorizationGrant
```

Verdicts are action-qualified.

An `ACCEPTED` merge verdict is not applicable to deployment.

# Runtime fixture results

All M1 known-bad fixtures execute against M3 implementation components:

```text
M1-F01 ... M1-F16: PASS
```

Additional milestone checks:

```text
direct vertical happy path: PASS
required NOT_RUN cannot become PASS: PASS
authority change invalidates receipt: PASS
state change invalidates receipt: PASS
wrong-run/replay rejection: PASS
missing authorization -> BLOCKED: PASS
command timeout -> BLOCKED: PASS
```

# Security-path fixtures

M3 also executes:

```text
../ path traversal -> rejected
protected symlink escape -> rejected
unexpected executable earlier on PATH -> BLOCKED when expected identity is required
```

# What M3 does not prove

M3 does not prove:

- Stable schemas;
- OpenSpec integration;
- remote/host-specific trust;
- CI merge-queue enforcement;
- provider revocation;
- cross-repository atomic state;
- generalized external-input types;
- cryptographic receipt attestation;
- production performance/scalability.

Those claims must not be inferred from M3's PASS.

# M4 handoff

M4 may now **evaluate** promotion of:

```text
AuthorityRef
AuthorizationGrant
StateIdentity
EvidenceReceipt
AcceptanceVerdict
```

M3 does not automatically promote them.

`AssurancePlan` and the direct execution plan remain module-owned unless M4 finds evidence for broader promotion.

## Related

- [Contracts, state, and evidence](contracts-state-and-evidence.md)
- [StateIdentity ADR](adr-state-identity.md)
- [AuthorizationGrant ADR](adr-authorization-grant.md)
- [EvidenceReceipt ADR](adr-evidence-receipt.md)
- [AcceptanceVerdict ADR](adr-acceptance-verdict.md)
- [M1 trust-protocol adversarial fixtures](trust-protocol-adversarial-fixtures.md)
