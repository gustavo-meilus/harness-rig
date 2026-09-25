---
id: harness-rig-adr-evidence-receipt
title: 'ADR: Experimental EvidenceReceipt protocol'
summary: Accepted M1 claim-specific evidence envelope with state/authority binding, bounded material input bindings, producer
  admissibility, gate versions, artifact integrity, and replay rules.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation M1 trust-protocol review, 2026-09-24
- User-supplied Harness Rig adversarial architecture review, 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- RigYard acceptance evidence, durable worker evidence, result acceptance, attempt capability, workspace baseline source/tests
  inspected 2026-09-24
- Skill Kit more-with-less v1.0.2 canonical skill and playbook inspected 2026-09-24
- Git official status/diff/submodule documentation rechecked 2026-09-24
- Node.js official child_process documentation rechecked 2026-09-24
---
# Status

**Accepted for Experimental implementation in M1. Stable promotion is forbidden before M4.**

# Reuse before invention

Current RigYard evidence already demonstrates useful patterns Harness Rig should reuse:

```text
run/step/attempt/request binding
closed required-check sets
explicit permission-unavailable outcomes
bounded stdout/stderr
worker/lifecycle identity
artifact digest + byte count
one-use attempt disposition
stale/replay rejection
strict schemas
worker self-checks kept advisory
```

Harness Rig references those native details; it does not flatten them into one mega-schema.

# Decision

`EvidenceReceipt` is a claim/applicability envelope:

```text
receipt_id
claim:
  claim_id
  subject_ref
authority_id
state_before
state_after
certified_state_id?
input_bindings[]
producer:
  producer_id
  run_id
  attempt_id?
gate:
  gate_id
  contract_version
tool:
  executable_identity?
  tool_version?
  invocation_digest?
outcome
started_at
finished_at
artifacts[]
receipt_digest
```

# Claim/subject

A receipt supports exactly `claim_id` about `subject_ref`; it cannot silently prove a broader property.

# State

Normal PASS requires unchanged relevant state. If `state_before != state_after`, outcome is `MUTATED` and no post-mutation
state is certified.

# Material input bindings

A gate records only material mutable non-repository inputs it actually depends on, such as feature flags, DB fixtures,
container digests, deployment revisions, browser/runtime profiles or external contract versions.

A source-only deterministic gate uses an empty list. No third global environment identity is introduced.

# Producer/admissibility

Valid JSON is not sufficient. Initial admissible patterns are a current Harness Rig run, a trusted CI run bound to the
expected subject/workflow, or an explicit imported-evidence provider that validates its native artifact.

Arbitrary pre-existing repository files are not fresh receipts merely because their schema parses.

# Gate version and tool identity

`contract_version` identifies PASS semantics. Incompatible gate semantics stale prior receipts even if `gate_id` is the same.

Where consequential, bind resolved executable/tool/runtime identity rather than trusting an unexpected mutable PATH result.

# Outcome

M1 common vocabulary:

```text
PASS
FAIL
BLOCKED
MUTATED
NOT_RUN
```

Provider-specific flaky/retry/partial states remain native until later evidence shows a shared contract is needed.

Required NOT_RUN never satisfies a required claim.

# Artifacts

Reference native evidence by kind/digest/location/retention. Inline retained content must match bytes/digest. Sensitive
artifacts follow security/retention policy.

# Integrity/replay

`receipt_digest` hashes canonical receipt content excluding itself.

Reuse requires matching claim, subject, authority, applicable state policy, material inputs, gate contract, admissible
producer and artifact integrity.

Local digest integrity is not a third-party attestation.

# Minimum-sufficient boundary

Do not add a flattened evidence warehouse, mandatory signatures for every local receipt, global environment snapshots, or a
second copy of RigYard worker-result protocols.

## Related

- [StateIdentity ADR](adr-state-identity.md)
- [AcceptanceVerdict ADR](adr-acceptance-verdict.md)
