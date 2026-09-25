---
id: harness-rig-progressive-revision-record
title: Harness Rig progressive revision record
summary: Current progressive-remediation milestone status, verification result, evidence limits, and next permitted milestone.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation M0-M3 execution and verification, 2026-09-24 through 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient engineering doctrine, applied 2026-09-25
- Harness Rig M4 core promotion implementation and adversarial verification, 2026-09-25
- Local runtime evidence: Python 3.13.5 and Git 2.47.3, 2026-09-25
---
# Current revision

```text
milestone: M4
package revision: r8.4
result: PASS
date: 2026-09-25
next allowed milestone: M5
resume task: M5-T01
```

# M4 contract dispositions

```text
AuthorityRef        SPLIT_STABLE_INVARIANT_FROM_EXPERIMENTAL_PROVIDER_FIELDS
AuthorizationGrant  PROMOTE_STABLE
StateIdentity       PROMOTE_STABLE
EvidenceReceipt     KEEP_EXPERIMENTAL_SHARED
AcceptanceVerdict   KEEP_EXPERIMENTAL_SHARED
```

Stable schemas now implemented:

```text
harness-rig/authority-ref/v1
harness-rig/authorization-grant/v1
harness-rig/state-identity/v1
```

`AssurancePlan`, direct `ExecutionPlan`/Topology shape, Context internals, `RuntimeResolution`, recurrence state and
`ContextManifest` remain module/adapter-owned.

# Runtime verification

```text
M3 regression suite: 22/22 PASS
M4 adversarial suite: 15/15 PASS
total unittest cases: 37/37 PASS
M1-F01 ... M1-F16 remain PASS
M4-V01 ... M4-V05 PASS
CLI smoke: gate PASS -> merge ACCEPTED
canonical references / manifest rows: 38 / 38
broken canonical/llms links: 0
manifest regeneration: byte-identical
```

# Important boundary

M4 does **not** make the complete vertical slice Stable. `EvidenceReceipt` and `AcceptanceVerdict` remain Experimental until
real additional providers/lifecycle consumers earn a frozen shared shape.

M4 also does not introduce OpenSpec implementation, host qualification, Context convergence, recurrence, generalized IAM,
or new orchestration infrastructure.

# Next

Resume at **M5-T01 - Finalize canonical-KB vs Context-lifecycle ownership**. M5 has not been executed.
