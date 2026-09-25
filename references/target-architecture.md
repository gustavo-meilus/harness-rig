---
id: harness-rig-target-architecture
title: Target architecture
summary: Proposed modular monorepo architecture, dependency direction, module responsibilities, and extension boundaries.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Harness Rig architecture analysis, 2026-09-21
- Robert C. Martin, The Clean Architecture, 2012
- OpenAI Harness Engineering, 2026-02-11
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Harness Rig expected-feature synthesis, refreshed 2026-09-21
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
---
# Expected-feature authority

Use [Expected Harness Rig feature set and RigYard reconciliation contract](expected-harness-rig-feature-set.md) as the mature feature inventory.

# Architectural objective

Harness Rig is a small authority/state/evidence kernel with bounded modules and adapters.

# Repository shape

```text
harness-rig/
├── core/
│   ├── contracts/
│   ├── authority/
│   ├── state/
│   ├── evidence/
│   └── acceptance/
├── modules/
│   ├── context/
│   │   ├── lifecycle/
│   │   ├── knowledge-base/
│   │   ├── reconciliation/
│   │   ├── freshness/
│   │   └── integrity/
│   ├── assurance/
│   └── topology/
├── adapters/
│   ├── spec/
│   ├── hosts/
│   ├── authorities/
│   ├── recurrence/
│   └── ci/
├── gates/
│   ├── command/
│   ├── knowledge/
│   ├── authority/
│   ├── architecture/
│   ├── tests/
│   ├── security/
│   └── playwright/
├── schemas/
├── migrations/
├── evals/
├── fixtures/
├── distributions/
├── docs/
└── tools/
```

# Context composition

```text
AIBoarding lifecycle/context behavior
+
Skill Kit llm-knowledge-base-maintainer
```

Context owns:

```text
root agent navigation
canonical references
stable IDs
provenance
source attachment
reconciliation
llms.txt
manifest.jsonl
freshness/drift
whole-collection audit
deterministic integrity
progressive disclosure
```

It does not duplicate OpenSpec behavioral specs.

# Dependency direction

```text
core -> external-tool independent
modules -> core
gates -> core contracts
adapters -> core + approved module interfaces
distribution -> composition only
```

# Main lifecycle

```text
intent
  ↓
SpecEngine / AuthorityProvider
  ↓
AuthorityRef + AuthorizationGrant
  ↓
Context
  ↓
AssurancePlan
  ↓
Topology / ExecutionPlan
  ↓
one primary execution by default
  ↓
gates / sensors
  ↓
EvidenceReceipt[]
  ↓
semantic review only where needed
  ↓
AcceptanceVerdict
```

# Knowledge design rule

Do not add hidden retrieval infrastructure to the Context plane.

Improve canonical organization, navigation, links, provenance, reconciliation, and deterministic integrity first.

## Related

- [Skill Kit knowledge-base integration for the Harness Rig Context plane](skill-kit-knowledge-base-context.md)
- [Roadmap](roadmap.md)
