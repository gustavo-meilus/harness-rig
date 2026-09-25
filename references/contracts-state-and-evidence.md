---
id: harness-rig-contracts-state-and-evidence
title: Contracts, state, and evidence
summary: Proposed kernel contracts and exact-state evidence semantics that bind authority, verification, and acceptance.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- TacticSwitch control-packets.md and protocol.md, accessed 2026-09-21
- TacticSwitch state.schema.json v4, accessed 2026-09-21
- Adaptive Engineering Harness hook implementation, accessed 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- Harness Rig progressive remediation M1 trust-protocol review, 2026-09-24
- User-supplied Harness Rig adversarial architecture review, 2026-09-24
- RigYard acceptance evidence, durable worker evidence, result acceptance, attempt capability, workspace baseline source/tests
  inspected 2026-09-24
- Skill Kit more-with-less v1.0.2 canonical skill and playbook inspected 2026-09-24
- Git official status/diff/submodule documentation rechecked 2026-09-24
- Node.js official child_process documentation rechecked 2026-09-24
---
# M1 status

M1 trust protocols are accepted for **Experimental** implementation only. Stable promotion is deferred to M4 after imported
consumers and the M3 vertical slice exercise them.

# Experimental candidates

```text
SpecEngine          experimental; shape from Direct + OpenSpec
AuthorityRef        candidate
AuthorizationGrant  M1 accepted, experimental
StateIdentity       M1 accepted, experimental
EvidenceReceipt     M1 accepted, experimental
AcceptanceVerdict   M1 accepted, experimental
CapabilitySet       experimental; shape from native host evidence
```

Module-owned concepts remain module-owned: Context indexes/manifests, `AssurancePlan`, `ExecutionPlan`, `RuntimeResolution`,
and recurrence state. `ContextManifest` is not promoted by M1.

# Authority / authorization

`AuthorityRef` says what must be true. `AuthorizationGrant` says who may perform which action against which target now.

# State / inputs

See [StateIdentity ADR](adr-state-identity.md). Common evidence binds authority plus repository state. Material mutable
non-repository inputs bind only at the receipt that consumes them; M1 adds no third global state plane.

# Assurance / topology

Assurance owns required claims/independence/authorization predicates. Topology owns formation/ownership/isolation/technical
permissions. Execution may narrow authorization but never broaden it.

# Evidence

See [EvidenceReceipt ADR](adr-evidence-receipt.md).

```text
PASS
FAIL
BLOCKED
MUTATED
NOT_RUN
```

Native RigYard/OpenSpec/browser/tool artifacts stay native and are referenced.

# Acceptance

See [AcceptanceVerdict ADR](adr-acceptance-verdict.md).

```text
ACCEPTED
REWORK
BLOCKED
```

A verdict is deterministic arithmetic over validated receipts/grants, not an authorization bearer token.

# M1 non-goals

No global environment-state type, general IAM, central evidence DB, flattened native evidence, or Stable SpecEngine /
CapabilitySet / ContextManifest.

## Related

- [StateIdentity ADR](adr-state-identity.md)
- [AuthorizationGrant ADR](adr-authorization-grant.md)
- [EvidenceReceipt ADR](adr-evidence-receipt.md)
- [AcceptanceVerdict ADR](adr-acceptance-verdict.md)
- [Security/trust boundaries](security-trust-and-execution-boundaries.md)
- [Trust fixtures](trust-protocol-adversarial-fixtures.md)
