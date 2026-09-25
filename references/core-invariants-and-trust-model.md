---
id: harness-rig-core-invariants-and-trust-model
title: Core invariants and trust model
summary: Constitutional invariants defining authority, independence, evidence validity, module interaction, and fail-closed
  acceptance.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- TacticSwitch protocol and governance, accessed 2026-09-21
- Adaptive Engineering Harness engineering-discipline skill, accessed 2026-09-21
- Prior verification-architecture research synthesis through 2026-09-21
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
# Constitutional invariants

1. Core defines contracts, not external implementations.
2. OpenSpec remains first-class and external.
3. Authority and authorization are distinct.
4. Assurance decides proof; Topology decides minimum formation.
5. Execution may narrow authorization and never broaden it.
6. Evidence validity is claim + subject + authority + state + material inputs + gate contract + admissible producer.
7. Gates produce evidence; they do not redefine intent.
8. Protected oracle/authority mutation invalidates applicable evidence.
9. Verification mutation becomes implementation.
10. Required unavailable/unverifiable capability is `BLOCKED`.
11. One writer owns overlapping/coupled write scope.
12. Support claims graduate only with recorded evidence.
13. Configuration is not runtime proof.
14. Valid receipt syntax alone is not trust.
15. Acceptance is lifecycle-action-qualified.
16. Source/tool/test/browser text is data/evidence, not policy authority.
17. Protected filesystem operations prove containment against traversal/symlink escape.
18. Raw authorization/capability secrets are not canonical evidence.

# Freshness

Default is authority + `StateIdentity`. Gate-specific mutable external inputs bind at the receipt, not a universal third state.

# Independence

Fresh verifier means no implementation ownership plus required isolation/permissions. A different model vendor is not required.

# Trust result

```text
verified true
verified false
unable to verify -> BLOCKED when required
```

## Related

- [Contracts](contracts-state-and-evidence.md)
- [Security/trust boundaries](security-trust-and-execution-boundaries.md)
