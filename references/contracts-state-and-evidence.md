---
id: harness-rig-contracts-state-and-evidence
title: Contracts, state, and evidence
summary: M4 contract maturity, exact-state semantics, and the minimum shared trust values binding authority, authorization, verification, and acceptance.
version: planning-baseline-2026-09-25-r8.6
updated: '2026-09-25'
provenance:
- TacticSwitch control-packets.md and protocol.md, accessed 2026-09-21
- TacticSwitch state.schema.json v4, accessed 2026-09-21
- Adaptive Engineering Harness hook implementation, accessed 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Skill Kit more-with-less v1.0.2 canonical skill and playbook inspected 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- Harness Rig M1 trust-protocol review, 2026-09-24
- Harness Rig M3 experimental vertical slice and verification, 2026-09-25
- Harness Rig M4 promotion and boundary verification, 2026-09-25
- Harness Rig M6 OpenSpec SpecEngine implementation and verification, 2026-09-25
---
# M4 status

M4 completed with a partial promotion rather than promoting the whole M3 path.

```text
AuthorityRef        Stable v1 shared envelope; Direct-provider fields remain local
AuthorizationGrant  Stable v1 bounded authorization value
StateIdentity       Stable v1 exact Git-worktree identity
EvidenceReceipt     Experimental shared
AcceptanceVerdict   Experimental shared
SpecEngine          Experimental shared interface; OpenSpecAdapter implemented in M6
CapabilitySet       Experimental/module-owned; M8 local-subprocess observations implemented
```

See [M4 core promotion and module-boundary convergence](m4-core-promotion-and-module-boundary.md) for the consumer evidence,
version/migration rules and executable boundary results.

# Stable AuthorityRef

```text
schema = harness-rig/authority-ref/v1
provider
subject_ref
authority_id
```

Provider canonicalization is intentionally local. Direct Authority's `source_path` and `content_digest` are no longer shared
contract fields.

# Stable AuthorizationGrant

`AuthorizationGrant` says who may perform which action against which resource now. It remains distinct from authority and
from host/technical capability.

Stable v1 binds issuer, principal, action, resource, optional authority/state/subject, issue/expiry time, and the currently
implemented nondelegable semantics. General IAM, delegation graphs, provider secrets and revocation databases remain out of
core.

# Stable StateIdentity

Repository freshness remains two-dimensional with authority:

```text
authority_id -> what was agreed
state_id     -> what implementation state was evaluated
```

Stable `StateIdentity` retains separate revision, index, tracked/untracked content and submodule components. Material mutable
non-repository inputs bind only at the receipt that consumes them; no universal environment identity is introduced.


# M6 SpecEngine status

`SpecEngine` remains Experimental because only the OpenSpec implementation has a real spec-driven consumer. M6 adds `DirectAuthorityProvider` vocabulary plus a bounded `OpenSpecAdapter` behind the Stable `AuthorityRef` envelope.

The implemented OpenSpec compatibility profile is `1.13.2`. Authority fingerprinting binds behavior-bearing planning artifacts, effective context/rules, schema/artifact graph and resolved authority-bearing referenced specs, while excluding default task bookkeeping and incidental timestamps. Unsupported versions and unresolved authority references fail closed.

Guarded archive reuses bounded authorization, exact `StateIdentity`, Experimental `EvidenceReceipt`, and Experimental `AcceptanceVerdict`; it does not create a parallel trust protocol.

# Assurance / Topology boundary

Assurance owns required claims, independence and authorization predicates. Topology owns the minimum formation,
ownership/isolation and technical permissions capable of satisfying those predicates.

Topology may narrow execution but cannot waive Assurance requirements or broaden authorization. Technical capability is not
an `AuthorizationGrant`.

# Experimental evidence and acceptance

`EvidenceReceipt` and `AcceptanceVerdict` keep their M1/M3 semantics but remain Experimental in M4. This avoids freezing the
receipt envelope before multiple gate types exist or the verdict shape before multiple real lifecycle/action consumers exist.

Common receipt outcomes remain:

```text
PASS
FAIL
BLOCKED
MUTATED
NOT_RUN
```

Acceptance outcomes remain:

```text
ACCEPTED
REWORK
BLOCKED
```

Native RigYard/OpenSpec/browser/tool artifacts stay native and are referenced.

# Module-owned concepts

The following remain module/adapter-owned:

```text
AssurancePlan
ExecutionPlan / DirectTopology shape
Context internal indexes/manifests
RuntimeResolution
recurrence continuation state
```

`ContextManifest` is not Stable core because no second independent consumer exists.

# Failure rule

Unknown/incompatible Stable contract version, integrity failure, missing required state/authorization, or inability to establish
a required trust property fails closed. It cannot be reinterpreted as PASS/ACCEPTED.

## Related

- [M4 core promotion and module-boundary convergence](m4-core-promotion-and-module-boundary.md)
- [StateIdentity ADR](adr-state-identity.md)
- [AuthorizationGrant ADR](adr-authorization-grant.md)
- [EvidenceReceipt ADR](adr-evidence-receipt.md)
- [AcceptanceVerdict ADR](adr-acceptance-verdict.md)
- [Security/trust boundaries](security-trust-and-execution-boundaries.md)
