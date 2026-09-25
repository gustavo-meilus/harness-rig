---
id: harness-rig-adr-acceptance-verdict
title: 'ADR: Experimental AcceptanceVerdict protocol'
summary: Accepted M1 acceptance protocol qualified by subject, lifecycle decision, policy, evidence set, authority/state,
  and current authorization.
version: planning-baseline-2026-09-25-r8.4
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
- Harness Rig M4 core-promotion implementation and verification, 2026-09-25
---
# Status

**M4 disposition: `KEEP_EXPERIMENTAL_SHARED`.** The action-qualified invariant remains required, but a second real consequential lifecycle/action consumer has not yet earned a Stable serialized shape.

# Decision

`AcceptanceVerdict` answers one lifecycle decision for one subject under one policy.

```text
verdict_id
subject_ref
decision_for
policy_ref
authority_id
state_id
evidence_receipts[]
authorization_grants[]
outcome
reasons[]
evaluated_at
verdict_digest
```

# Lifecycle decision

Initial examples:

```text
implementation_complete
merge
publish
deploy
destructive_operation
```

One verdict type is enough. `ACCEPTED for merge` does not imply deploy eligibility/authorization.

# Policy

`policy_ref` identifies the version/digest-addressable acceptance policy: required claims/gates, independence,
authorization predicates, staleness rules and residual-risk handling.

# Evidence

The verdict references exact receipt IDs/digests. Reject missing required evidence, wrong claims/subjects, stale
authority/state/input bindings, inadmissible producers, incompatible gate contracts, and non-satisfying outcomes.

# Authorization

A verdict may record which grant IDs satisfied authorization predicates at evaluation time. The verdict is not a bearer
authorization.

Before the consequential action, revalidate current subject, authority/state and grant validity including expiry/revocation.

# Outcomes

```text
ACCEPTED -> all mandatory predicates for decision_for are satisfied now
REWORK   -> evidence proves a required property false
BLOCKED  -> required evidence/capability/authority/authorization/trust cannot be established
```

# Determinism

Final required-receipt/grant arithmetic is deterministic. A semantic-review receipt may be model-produced, but missing
deterministic prerequisites cannot be waived by model judgment.

# Minimum-sufficient boundary

Do not add one verdict class per action, a workflow service, a global policy server or a verdict DB without concrete need.

## Related

- [AuthorizationGrant ADR](adr-authorization-grant.md)
- [EvidenceReceipt ADR](adr-evidence-receipt.md)
