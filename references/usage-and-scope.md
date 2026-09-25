---
id: harness-rig-usage-and-scope
title: Harness Rig knowledge-base usage and scope
summary: How an LLM should use this collection without confusing current implementation, proposed architecture, evidence,
  and decisions.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- LLM Knowledge Base Maintainer skill, gustavo-meilus/skill-kit, accessed 2026-09-21
- Lite Writing skill, gustavo-meilus/skill-kit, accessed 2026-09-21
- Research and design synthesis from the Harness Rig analysis completed through 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Harness Rig expected-feature synthesis, refreshed 2026-09-21
- Skill Kit llm-knowledge-base-maintainer v1.1.0, SKILL.md and DEFAULT_LAYOUT.md, inspected 2026-09-24
- Harness Rig knowledge-base-first Context synthesis, refreshed 2026-09-24
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
# Purpose

This collection is the canonical planning baseline for Harness Rig.

The expected project is:

```text
OpenSpec-first for behavior-changing intent
Skill-Kit-knowledge-base-first for durable project context
authority/state/evidence-bound for acceptance
minimum-sufficient in orchestration
```

# Retrieval order

1. [North star and product boundary](north-star-and-product-boundary.md)
2. [Expected Harness Rig feature set and RigYard reconciliation contract](expected-harness-rig-feature-set.md)
3. [Skill Kit knowledge-base integration for the Harness Rig Context plane](skill-kit-knowledge-base-context.md)
4. [RigYard current source and verification baseline](rigyard-current-source-and-verification-baseline.md)
5. [RigYard premise and minimum-sufficient feature admission](rigyard-premise-and-feature-admission.md)
6. [Core invariants and trust model](core-invariants-and-trust-model.md)
7. [OpenSpec spec engine, authority, and brainstorming integration](openspec-spec-engine-and-authority.md)
8. topic-specific page
9. [Roadmap](roadmap.md)
10. [Decision log](decision-log.md)
11. [Source register](source-register.md)

# Knowledge-base contract

This package itself dogfoods:

```text
canonical references
stable IDs
provenance
llms.txt
manifest.jsonl
whole-collection validation
```

No embedding/vector/RAG retrieval layer is part of this expected design.

# Authority

OpenSpec owns agreed behavioral intent.

Context references own durable project/engineering knowledge in their declared scope.

Code/tests/runtime remain authoritative for their respective evidence.

## Related

- [Skill Kit knowledge-base integration for the Harness Rig Context plane](skill-kit-knowledge-base-context.md)
- [Roadmap](roadmap.md)

# M1 trust-protocol reading order

"
    "1. [Contracts](contracts-state-and-evidence.md)
"
    "2. [StateIdentity ADR](adr-state-identity.md)
"
    "3. [AuthorizationGrant ADR](adr-authorization-grant.md)
"
    "4. [EvidenceReceipt ADR](adr-evidence-receipt.md)
"
    "5. [AcceptanceVerdict ADR](adr-acceptance-verdict.md)
"
    "6. [Security/trust boundaries](security-trust-and-execution-boundaries.md)
"
    "7. [Trust fixtures](trust-protocol-adversarial-fixtures.md)

"
    "These contracts are Experimental after M1.
