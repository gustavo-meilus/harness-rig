---
id: harness-rig-adr-authorization-grant
title: 'ADR: Experimental AuthorizationGrant protocol'
summary: Accepted M1 bounded authorization protocol covering issuer, principal, action, resource, expiry, delegation, revocation,
  and optional authority/state binding.
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

# Decision

The former action-name-only authorization concept is replaced by bounded `AuthorizationGrant`.

```text
grant_id
issuer
principal
scope:
  action
  resource
bindings:
  authority_id?
  state_id?
  subject_ref?
issued_at
expires_at?
delegation
origin
provider_ref
```

# Validity

Grant validation checks trusted issuer, matching principal/action/resource, required authority/state/subject binding,
issuance/lifetime and **expiry**, allowed delegation, and provider revocation/current status where that authoritative
provider supports it.

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

Default is `none`. A fresh verifier/retry/recurrence actor does not inherit a grant merely because it can read the grant.

# Revocation

Harness Rig does not mirror authorization providers into a central revocation DB. Consequential action-time validation
consults the authoritative provider when revocation/current-status semantics exist.

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

# Minimum-sufficient boundary

Do not add general IAM, roles, a policy language, delegation graphs or an authorization database.

## Related

- [AcceptanceVerdict ADR](adr-acceptance-verdict.md)
- [Security/trust boundaries](security-trust-and-execution-boundaries.md)
