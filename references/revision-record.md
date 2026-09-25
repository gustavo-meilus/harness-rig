---
id: harness-rig-progressive-revision-record
title: Harness Rig progressive revision record
summary: Current progressive-remediation milestone status, verification result, evidence limits, and next permitted milestone.
version: planning-baseline-2026-09-25-r8.6
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation M0-M5 execution and verification, 2026-09-24 through 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient engineering doctrine, applied 2026-09-25
- OpenSpec v1.13.2 public release/package/CLI/agent-contract surfaces rechecked 2026-09-25
- Harness Rig M6 OpenSpec SpecEngine implementation and adversarial verification, 2026-09-25
---
# Current revision

```text
milestone: M6
package revision: r8.6
result: PASS
date: 2026-09-25
next allowed milestone: M7
resume task: M7-T01
```

# M6 implemented boundary

```text
DirectAuthorityProvider -> Stable AuthorityRef v1
OpenSpecAdapter         -> Stable AuthorityRef v1
Experimental SpecEngine -> available / health / authority / archive
```

OpenSpec remains an optional external executable. Base Harness Rig still works when it is absent; an OpenSpec-required path fails closed when it is unavailable or incompatible.

The current compatibility profile is exactly OpenSpec `1.13.2`. Version is a health/compatibility predicate, not part of the authority fingerprint.

# M6 authority and health semantics

- Default task bookkeeping does not alter OpenSpec authority identity.
- Proposal/scope, behavioral deltas, constraining design, effective context/rules, custom non-task artifacts and authority-bearing referenced specs do alter authority identity.
- Unknown custom planning artifacts are conservatively authority-bearing.
- `skip_specs` is supported as an OpenSpec planning decision but never skips strict validation, Harness authorization, exact state or acceptance.
- Unresolved authority-bearing references fail closed.
- Root health, planning completeness, strict validation, current apply/archive instructions and effective config/rule shapes are checked explicitly.
- Primary external Store roots are not archive-qualified in M6; read-only referenced Stores can contribute authority.
- Strict OpenSpec validation is not semantic proof. A required semantic-coherence predicate that fails/unknown blocks before archive.

# Archive transition

`harness-rig spec archive` evaluates `(A0,S0)`, requires bounded `spec_archive` authorization and readiness evidence, invokes only OpenSpec's public archive command, checks postconditions, records transition evidence for `(A1,S1)`, and explicitly rechecks the pre-archive receipt/grant against final authority/state. The old preconditions must not remain accepted.

Partial mutation, command failure, missing archive target, active-change residue, or unreadable final affected specs produce `BLOCKED`.

# Runtime verification

```text
M3 regression suite: 22/22 PASS
M4 adversarial suite: 15/15 PASS
M5 Context suite: 14/14 PASS
M6 OpenSpec suite: 16/16 PASS
combined unittest cases: 67/67 PASS
M1-F01 ... M1-F16 remain PASS through M3 regressions
M6-V01 ... M6-V06 PASS
```

Final collection counts are recorded in `verification/m6-verification-record.json` after deterministic manifest/projection regeneration; exact packaged-byte rerun evidence is reported in the delivery handoff after package construction.

# Important boundary

M6 does not implement M7 repository enforcement, M8 host qualification, M9 gate/Playwright platform work, M10 CLI finalization, or M11 Git-history qualification. It does not promote Experimental `SpecEngine`, `EvidenceReceipt`, or `AcceptanceVerdict` to Stable.

No OpenSpec parser/merge engine, npm dependency, vector/RAG subsystem, IAM system, evidence database, plugin SDK, recurrence platform, generic telemetry platform, or new orchestration framework was introduced.

The verification sandbox did not expose a local `openspec` executable, so M6 does not claim live native-runtime qualification. Adapter behavior is covered by deterministic 1.13.2 contract fixtures and subprocess-boundary verification; external public-contract facts were rechecked on 2026-09-25.

# Next

Resume at **M7-T01 - Emit a CI obligation artifact for the evaluated revision**. M7 has not been executed.
