---
id: harness-rig-adr-authorization-grant
title: 'ADR: Stable AuthorizationGrant v1 protocol'
summary: Stable M4 bounded authorization protocol covering issuer, principal, action, resource, lifetime, nondelegable semantics, and optional authority/state binding.
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

**M4 disposition: `PROMOTE_STABLE`. Schema: `harness-rig/authorization-grant/v1`.**

# Decision

The former action-name-only authorization concept is replaced by bounded `AuthorizationGrant`.

```text
schema = harness-rig/authorization-grant/v1
grant_id
issuer
principal
action
resource
authority_id?
state_id?
subject_ref?
issued_at
expires_at?
delegation = none
```

# Validity

Shared grant validation checks trusted issuer, matching principal/action/resource, required authority/state/subject binding,
issuance/lifetime and **expiry**, allowed delegation, schema, and integrity. When an external authorization provider has
revocation/current-status semantics, the consequential action adapter must consult that provider at action time; the Stable
grant does not claim to mirror provider status.

A required grant that cannot be verified causes `BLOCKED`.

# Action binding

Initial actions can include:

```text
planning_write
implementation_write
protected_oracle_write
merge
publish
deploy
destructive_operation
```

Planning/implementation write grants normally authorize changing state, so they need not bind the pre-edit state unless
policy requires it. Merge/publish/deploy/destructive grants normally bind the concrete accepted subject/state/resource.

# Delegation

Stable v1 supports only `delegation = none`. A fresh verifier/retry/recurrence actor does not inherit a grant merely because it can read the grant. Non-`none` delegation fails closed until a real consumer earns broader semantics.

# Provider/current-status boundary

Harness Rig does not mirror authorization providers into a central revocation DB and does not embed provider credentials/status in the Stable grant. Consequential action-time integrations consult the authoritative provider when revocation/current-status semantics exist.

# Secrets

Canonical grants contain non-secret IDs/digests. OAuth tokens, API keys, bearer tokens and capability secrets stay in the
provider/host credential boundary.

# RigYard distinction

RigYard's one-use attempt capability is valuable for technical attribution and replay prevention, but is not an
`AuthorizationGrant`:

```text
AuthorizationGrant -> permission to act
one-use attempt capability -> one expected technical attempt/result
```

# M4 compatibility and failure semantics

- Exact Stable v1 values load only after field, lifetime, digest and `grant_id` integrity checks.
- Exact Experimental v1 values migrate deterministically after old `grant_id` verification.
- Migration drops the unused Experimental `origin` field and recomputes `grant_id` under Stable v1.
- Unknown schema/fields, tampering, malformed lifetime/time, and unsupported delegation fail closed.
- A required missing grant is `UNVERIFIABLE`; invalid schema/integrity/binding/time is `INVALID`.

# Minimum-sufficient boundary

Do not add general IAM, roles, a policy language, delegation graphs or an authorization database.

## Related

- [AcceptanceVerdict ADR](adr-acceptance-verdict.md)
- [Security/trust boundaries](security-trust-and-execution-boundaries.md)
