---
id: harness-rig-m4-core-promotion-and-module-boundary
title: M4 core promotion and module-boundary convergence
summary: Source-backed M4 dispositions, stable contract schemas, migration/failure semantics, and executable Assurance/Topology boundary evidence.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- Harness Rig r8.3 executable prototype and M3 verification records inspected 2026-09-25
- Harness Rig progressive remediation plan M4 criteria, 2026-09-25
- Harness Rig M4 execution brief, 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient engineering doctrine, applied 2026-09-25
- Harness Rig M4 executable adversarial tests and migration vectors, 2026-09-25
---
# Result

M4 completes with **PASS** at package revision `r8.4`.

Promotion is intentionally partial:

| Candidate | M4 disposition | Why |
|---|---|---|
| `AuthorityRef` | `SPLIT_STABLE_INVARIANT_FROM_EXPERIMENTAL_PROVIDER_FIELDS` | Direct Authority produces it; CommandGate and Acceptance consume the shared identity. Provider-local file path/content details are not needed across the boundary. |
| `AuthorizationGrant` | `PROMOTE_STABLE` | Bounded authorization is an unavoidable cross-cutting invariant distinct from authority and technical capability. Acceptance validates it; topology cannot manufacture or broaden it. |
| `StateIdentity` | `PROMOTE_STABLE` | CommandGate captures it, receipts bind it, grants may bind it, and Acceptance requires exact freshness. |
| `EvidenceReceipt` | `KEEP_EXPERIMENTAL_SHARED` | One real Harness Rig gate provider exists. M9 owns common gate semantics after more providers exist. |
| `AcceptanceVerdict` | `KEEP_EXPERIMENTAL_SHARED` | The action-qualified invariant is retained, but a second real lifecycle/action consumer has not yet earned a Stable serialized shape. |

No second consumer was fabricated for the two contracts kept Experimental.

# M4-T01 - AuthorityRef

Stable shared shape:

```text
schema = harness-rig/authority-ref/v1
provider
subject_ref
authority_id
```

`authority_id` remains provider-computed. The Direct file provider currently derives it from provider identity, subject,
normalized source path, and authority-bearing file digest.

The following M3 Direct-provider fields are deliberately **not** Stable core fields:

```text
source_path
content_digest
```

They are provider-local canonicalization inputs. The stable contract has no `extra`, `metadata`, `provider_data`, or other
escape bag.

Compatibility/migration:

- exact Stable v1 loads directly after field and digest validation;
- the exact M3 direct-file dataclass shape without `schema` migrates deterministically after its old `authority_id` is
  recomputed and verified;
- migration preserves `authority_id` and discards provider-local `source_path`/`content_digest` from the shared value;
- unknown schemas, unknown legacy shapes, invalid digests, or legacy integrity mismatch fail closed with `ValueError`.

Revisit trigger: a future provider may require a different provider-local canonicalization algorithm, but it should still emit
this four-field stable envelope unless a demonstrated cross-provider invariant requires a schema change.

# M4-T02 - AuthorizationGrant

Stable shared shape:

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
delegation
```

M4 deletes the unused Experimental `origin` field rather than freezing it. Provider credentials, revocation storage, and
provider-current-status data remain outside the shared value. Consequential action-time integrations remain responsible for
consulting an authoritative provider when that provider has revocation/current-status semantics.

Stable v1 implements only `delegation = none`. A non-`none` value fails closed instead of pretending that delegation graphs
exist.

Compatibility/migration:

- exact Stable v1 loads only after field, timestamp, digest and `grant_id` integrity checks;
- exact `harness-rig/authorization-grant/experimental-v1` values migrate deterministically after the Experimental `grant_id`
  is verified;
- migration drops Experimental `origin` and recomputes `grant_id` under Stable v1;
- unknown schema, unknown fields, tampering, malformed lifetime, unsupported delegation, or invalid time fails closed;
- validation returns `INVALID` for unsupported schema/integrity/time/delegation and `UNVERIFIABLE` for a required missing grant.

The stable invariant is bounded permission to perform an action. It is not general IAM and it does not turn technical host
capability into authorization.

# M4-T03 - StateIdentity

Stable shared schema:

```text
schema = harness-rig/state-identity/v1
repository_id
revision { head_oid, head_tree_oid? }
index_manifest_digest
tracked_manifest_digest
untracked_nonignored_manifest_digest
submodules[]
content_id
state_id
```

The current capture implementation is the Git-worktree profile already exercised in M3. M4 does not claim a generalized
multi-repository or cross-platform state framework.

Compatibility/migration:

- exact Stable v1 loads after strict field/digest/integrity validation;
- exact Experimental v1 serializations migrate after their old `state_id` is verified;
- migration preserves component/content identities and recomputes `state_id` because schema identity participates in state
  identity;
- a golden Stable v1 serialization vector is executable in `test_state_identity_stable_golden_vector`;
- unknown schema, extra/missing fields, malformed digests, or integrity mismatch fails closed;
- inability to capture required Git state produces no `StateIdentity`; callers cannot derive an acceptance PASS from missing
  state.

Revisit trigger: a demonstrated non-Git or multi-repository consumer may require a separate state domain/profile. It must not
be introduced as an untyped escape field in this schema.

# M4-T04 - EvidenceReceipt

Disposition: `KEEP_EXPERIMENTAL_SHARED`.

Current producer/consumer evidence is real but narrow:

```text
CommandGate -> EvidenceReceipt -> Acceptance
```

Only one actual Harness Rig gate provider exists. `EvidenceReceipt` therefore remains
`harness-rig/evidence-receipt/experimental-v1` while preserving the M1/M3 invariants: claim/subject/authority/state/run/gate
binding, explicit outcomes, material input bindings, referenced native artifacts, integrity and replay checks.

Provider-native RigYard/OpenSpec/browser/tool evidence remains native and referenced rather than flattened.

Revisit trigger: M9, after at least a second materially different gate/provider exercises the shared envelope.

# M4-T05 - AcceptanceVerdict

Disposition: `KEEP_EXPERIMENTAL_SHARED`.

Acceptance remains action-qualified and deterministic, but M4 has only the direct vertical slice plus CLI exit consumption.
That is insufficient to freeze lifecycle/action serialization ahead of the real CI/repository/product consumers planned for
M7/M10.

The schema therefore remains `harness-rig/acceptance-verdict/experimental-v1`.

Revisit trigger: a second real consequential action/lifecycle consumer with retained execution evidence.

# M4-T06 - Module ownership retained

The following remain module/adapter-owned and are not promoted for symmetry:

```text
AssurancePlan
ExecutionPlan / DirectTopology plan shape
Context internal indexes/manifests
RuntimeResolution
recurrence continuation state
```

Executable M4 boundary tests prove:

- `AssurancePlan`/`AssuranceRequirement` contain no worker, host, model or principal selection field;
- DirectTopology cannot make missing required evidence acceptable because Acceptance consumes Assurance requirements directly;
- DirectTopology cannot turn an action-mismatched grant into valid authorization;
- a technical direct formation does not satisfy a missing authorization grant.

This preserves:

```text
Assurance = WHAT must be demonstrated
Topology  = minimum WHO/WHERE formation capable of satisfying it
Acceptance = whether the required predicates were actually satisfied
```

# M4-T07 - ContextManifest

`ContextManifest` remains out of Stable core. No second independent consumer exists.

Context-owned indexes/manifests continue toward M5. No general Context schema or retrieval subsystem is introduced in M4.

# M4 verification

```text
M4-V01 PASS - every promoted contract has two concrete consumers or one unavoidable cross-cutting invariant
M4-V02 PASS - promoted dataclasses have no provider escape bags; Direct Authority local fields were removed from AuthorityRef
M4-V03 PASS - Assurance cannot encode/select worker/host/model/principal
M4-V04 PASS - Topology cannot waive required evidence or broaden/mint authorization
M4-V05 PASS - promoted schemas have explicit compatibility, migration, integrity and unknown/failure semantics
```

Executable evidence is retained in:

```text
prototype/tests/test_m3_vertical_slice.py
prototype/tests/test_m4_core_promotion.py
verification/m4-verification-record.json
verification/m4-fixture-results.json
verification/m4-unittest-output.txt
verification/m4-cli-smoke.json
verification/m4-kb-integrity.json
```

# Complexity result

M4 adds no registry, dependency-injection layer, plugin SDK, central contract/evidence service, IAM system, orchestration
framework, vector/RAG subsystem, recurrence platform, or generic telemetry platform.

The only shared runtime additions are strict v1 loaders/migrators for the three promoted values plus one digest-format helper.
