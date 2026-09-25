---
id: harness-rig-m1-trust-protocol-adversarial-fixtures
title: M1 trust-protocol adversarial fixtures
summary: Sixteen stable known-bad state, authorization, evidence, acceptance, path, symlink, and executable scenarios defined
  before runtime implementation.
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
# Purpose

These known-bad fixtures freeze M1 trust semantics before runtime APIs are stabilized.

Machine-readable catalog: `verification/m1-known-bad-fixtures.json`.

M1 validates definitions and coverage. Runtime execution is explicitly deferred to M3 and is not claimed in r8.1.

# M1-F01 — Commit during session

**Area:** `state`  
**Executable by:** `M3`

**Setup:** Modify tracked source, commit it so worktree becomes clean.

**Expected:** Current state still differs from the session baseline.

**Invariant:** Committed changes remain observable.

# M1-F02 — Verifier mutates source

**Area:** `state`  
**Executable by:** `M3`

**Setup:** Run a zero-exit gate that changes relevant source.

**Expected:** MUTATED; post-mutation state is not certified.

**Invariant:** Verification mutation becomes implementation.

# M1-F03 — Identical content on different revision

**Area:** `state`  
**Executable by:** `M3`

**Setup:** Recreate identical content at a different commit.

**Expected:** Revision changes; content may remain equal; reuse follows policy.

**Invariant:** Revision provenance is distinct.

# M1-F04 — Staged-only edit

**Area:** `state`  
**Executable by:** `M3`

**Setup:** Stage content differing from HEAD.

**Expected:** Index identity changes independently.

**Invariant:** Logical index state is explicit.

# M1-F05 — Dirty consumed submodule

**Area:** `state`  
**Executable by:** `M3`

**Setup:** Dirty an initialized submodule without changing superproject gitlink.

**Expected:** State/input changes or BLOCKED.

**Invariant:** Consumed submodule state cannot disappear.

# M1-F06 — Ignored consumed input changes

**Area:** `evidence-input`  
**Executable by:** `M3`

**Setup:** Change ignored gate input while authority/repository state is otherwise constant.

**Expected:** Input binding changes; old receipt becomes inapplicable.

**Invariant:** Material non-source inputs are bound.

# M1-F07 — Expired grant

**Area:** `authorization`  
**Executable by:** `M3`

**Setup:** Use deploy grant after expiry.

**Expected:** INVALID/BLOCKED.

**Invariant:** Authorization lifetime is enforced.

# M1-F08 — State-bound grant after state change

**Area:** `authorization`  
**Executable by:** `M3`

**Setup:** Grant for S0, change to S1.

**Expected:** Old grant invalid for S1.

**Invariant:** Target binding is enforced.

# M1-F09 — Nondelegable grant used by another principal

**Area:** `authorization`  
**Executable by:** `M3`

**Setup:** Grant P1, present from P2.

**Expected:** INVALID absent explicit delegation.

**Invariant:** Possession does not imply delegation.

# M1-F10 — Forged/replayed receipt

**Area:** `evidence`  
**Executable by:** `M3`

**Setup:** Copy or hand-author valid-looking receipt from another run.

**Expected:** Reject absent explicit admissible producer/reuse policy.

**Invariant:** Evidence provenance is required.

# M1-F11 — Outdated gate contract

**Area:** `evidence`  
**Executable by:** `M3`

**Setup:** Use v1 receipt when incompatible v2 semantics required.

**Expected:** Receipt inapplicable.

**Invariant:** PASS semantics are versioned.

# M1-F12 — Artifact changed after receipt

**Area:** `evidence`  
**Executable by:** `M3`

**Setup:** Mutate referenced artifact after digest recorded.

**Expected:** Integrity failure.

**Invariant:** Artifacts are content-bound.

# M1-F13 — Merge verdict reused for deploy

**Area:** `acceptance`  
**Executable by:** `M3`

**Setup:** Present merge ACCEPTED at deploy boundary.

**Expected:** Does not satisfy deploy decision/authorization.

**Invariant:** Acceptance is action-qualified.

# M1-F14 — Path traversal

**Area:** `security`  
**Executable by:** `M3`

**Setup:** Use ../ to escape approved root.

**Expected:** Reject before mutation.

**Invariant:** Protected paths remain contained.

# M1-F15 — Protected symlink escape

**Area:** `security`  
**Executable by:** `M3`

**Setup:** Symlink protected path outside root.

**Expected:** Reject/BLOCK.

**Invariant:** Symlinks cannot bypass containment.

# M1-F16 — Malicious executable earlier on PATH

**Area:** `security`  
**Executable by:** `M3`

**Setup:** Place fake tool before expected tool.

**Expected:** Detect/reject or bind exact unexpected identity.

**Invariant:** Executable identity is evidence-backed.

# M1 result

```text
definitions: PASS
unique IDs: PASS
required scenario coverage: PASS
runtime execution: DEFERRED TO M3
```
