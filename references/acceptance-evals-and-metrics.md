---
id: harness-rig-acceptance-evals-and-metrics
title: Acceptance evaluations and metrics
summary: Behavioral and adversarial tests that verify Harness Rig itself, plus metrics that separate control integrity from
  speed or model performance.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Google Developers Blog, The Anatomy of Harness Engineering, accessed 2026-09-21
- TacticSwitch adversarial assurance and protocol evidence model, accessed 2026-09-21
- Adaptive Engineering Harness verification guidance, accessed 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Skill Kit llm-knowledge-base-maintainer v1.1.0, SKILL.md and DEFAULT_LAYOUT.md, inspected 2026-09-24
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
- Harness Rig M3 experimental direct vertical-slice implementation and executable verification, 2026-09-25
- 'Local runtime evidence: Python 3.13.5 and Git 2.47.3, 2026-09-25'
---
# Principle

M1 freezes known-bad trust scenarios before runtime APIs stabilize.

Machine-readable catalog: `verification/m1-known-bad-fixtures.json`.

# M1 fixtures

```text
M1-F01 commit during session
M1-F02 verifier mutation
M1-F03 identical content / different revision
M1-F04 staged-only edit
M1-F05 dirty consumed submodule
M1-F06 ignored consumed input
M1-F07 expired grant
M1-F08 state-bound grant after state change
M1-F09 nondelegable grant used by another principal
M1-F10 forged/replayed receipt
M1-F11 outdated gate contract
M1-F12 artifact changed after receipt
M1-F13 merge verdict reused for deploy
M1-F14 path traversal
M1-F15 protected symlink escape
M1-F16 malicious executable earlier on PATH
```

M1 validates fixture definitions/coverage only. Runtime execution is deferred to M3.

# Retained evaluations

Authority/state changes stale applicable evidence; unavailable required workers block; protected oracle changes reopen
authority; parallel write conflicts reject; KB IDs/links/manifest integrity stay deterministic.

## Related

- [Trust fixtures](trust-protocol-adversarial-fixtures.md)
- [Contracts](contracts-state-and-evidence.md)


# M3 executable result

M3 converts the M1 fixture definitions into executable runtime evidence.

```text
M1-F01 ... M1-F16: PASS
M3 direct happy path: PASS
M3-V01 ... M3-V05: PASS
test suite: 22/22 PASS
```

See [M3 experimental direct vertical slice](m3-experimental-vertical-slice.md).

The fixture result means the Experimental implementation detects/rejects the specified known-bad cases. It does not promote
the contracts to Stable.
