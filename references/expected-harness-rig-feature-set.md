---
id: harness-rig-expected-feature-set
title: Expected Harness Rig feature set and RigYard reconciliation contract
summary: Consolidated expected mature Harness Rig features across spec/authority, context, assurance, topology, evidence,
  hosts, gates, CI, migration, recurrence, retrieval, and extensibility, with a formal reconciliation protocol for currently
  inaccessible RigYard proposals.
version: planning-baseline-2026-09-25-r8.9
updated: '2026-09-25'
provenance:
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
- Harness Rig M4 core-promotion implementation and verification, 2026-09-25
- Harness Rig M9 gate-platform, Playwright, architecture, and mutation verification, 2026-09-25
---
# Status

## M4 trust-contract status

`AuthorityRef`, `AuthorizationGrant`, and `StateIdentity` are Stable v1 after M4. `EvidenceReceipt` and `AcceptanceVerdict` remain **Experimental shared** until additional real providers/lifecycle consumers earn promotion. M8 qualifies the narrow `local-subprocess` host adapter as Stable for four observed native capabilities. M9 adds Experimental common gate semantics plus architecture, Playwright, and mutation providers; `EvidenceReceipt`/`AcceptanceVerdict` remain Experimental shared. `AssurancePlan`, `ExecutionPlan`, `CapabilitySet`, `RuntimeResolution`, recurrence state, Context internals, and `ContextManifest` remain unpromoted/module-owned.


This page is the canonical expected mature Harness Rig feature inventory.

The Context plane now deeply integrates the Skill Kit LLM knowledge-base maintainer model.

# Product definition

```text
intent/specification
      ↓
authority + authorization
      ↓
canonical project knowledge
      ↓
assurance requirement
      ↓
minimum execution topology
      ↓
implementation
      ↓
deterministic/runtime evidence
      ↓
independent judgment where required
      ↓
acceptance
      ↓
repository/release enforcement
```

# 1. Specification and authority

Required:

```text
SpecEngine
OpenSpec first-class adapter
direct/manual authority provider
AuthorityRef
AuthorizationGrant
spec-impact classification
progressive specification rigor
protected authority/oracle handling
```

# 2. Context and canonical knowledge

Required:

```text
AIBoarding-derived context lifecycle
Skill-Kit-derived canonical knowledge-base maintenance
stable logical reference IDs
provenance
source attachment
search-before-create
semantic ownership
reconciliation
conflict/evidence-gap preservation
llms.txt
manifest.jsonl
freshness/drift
deterministic collection integrity
progressive disclosure
```

Normal knowledge discovery uses:

```text
root project map
llms.txt
manifest.jsonl
explicit links
repository/text search
targeted reading of canonical references
```

The expected project contains no embedding, vector-database, hosted-RAG, or semantic-index subsystem.

# 3. Assurance

Required:

```text
risk classification
reasoning difficulty separate from risk
required gates
independent-review requirement
human/action authorization
residual-risk handling
verification tier
```

# 4. Topology

Required:

```text
minimum execution formation
one-writer ownership
fresh verifier eligibility
context isolation
coarse safe parallelism
fail-closed independence
```

One agent plus deterministic feedback is the default.

# 5. Exact state and evidence

Required:

```text
StateIdentity
authority_id + state_id
EvidenceReceipt
stale-evidence rejection
mutating-verifier detection
artifact/provenance references
```

# 6. Acceptance

Required:

```text
AcceptanceVerdict
required evidence completeness
freshness
topology/independence
authority/authorization
protected oracle checks
ACCEPTED / REWORK / BLOCKED
```

# 7. Host capability platform

Required:

```text
CapabilitySet
Claude/Codex/Copilot adapters
Harness Doctor
native conformance
requested/resolved/observed runtime facts
```

# 8. Gates and sensors

First-class:

```text
command/test
knowledge-base integrity
OpenSpec health/validation
OpenSpec archive guard
architecture fitness
Playwright runtime/web acceptance
```

Additional risk-specific gates are added only where justified.

# 9. CI, governance, and release

Required:

```text
affected-module detection
C0-C3 change classes
feature-admission/retirement
canonical quality command
knowledge-base integrity
one ci / required verdict
ruleset integration
release provenance
generated-distribution integrity
```

# 10. Migration

Required imports:

```text
AIBoarding -> Context lifecycle
TacticSwitch -> Topology
Skill Kit engineering-harness-adaptive -> Assurance
Skill Kit llm-knowledge-base-maintainer -> Context knowledge base
```

Preserve relevant history and remove duplicate mechanisms after compatibility is proven.

# 11. Product CLI

Expected compact surface:

```text
harness-rig init
harness-rig doctor
harness-rig spec status
harness-rig verify
harness-rig status
harness-rig migrate
```

Knowledge integrity should participate in ordinary verification/status.

# 12. Behavioral evaluations

Required fixtures include:

```text
committed-in-session state
verifier mutation
stale authority receipt
stale state receipt
missing required fresh worker
protected oracle change
parallel writer conflict
host capability overclaim
OpenSpec absence/degraded mode
duplicate KB stable ID
broken KB link
missing/stale manifest row
invalid llms.txt target
source conflict preserved
unsupported KB claim rejected
Playwright skip/oracle mutation
generated distribution drift
```

# 13. Complexity governance

Required:

```text
feature-admission template
complexity budget
retirement/downgrade condition
periodic simplification review
```

# 14. Earned recurrence

Optional after field evidence.

No scheduler/queue/daemon infrastructure in Harness Rig core.

# 15. Adaptive execution

Optional after evidence.

No model/pricing service in core.

# 16. OpenSpec shared Store support

Experimental only when justified by actual cross-repository work.

# 17. Hooks

Only for lifecycle/permission/completion/state/evidence invariants.

# 18. Extensibility

Internal/static first:

```text
SpecEngine
AuthorityProvider
gate
host adapter
CI adapter
topology strategy
recurrence adapter
```

# Mature product flow

```text
INTENT
  ↓
OpenSpec / SpecEngine
  ↓
AuthorityRef + AuthorizationGrant
  ↓
Context
  ├── root project map
  ├── canonical references
  ├── llms.txt
  └── manifest.jsonl
  ↓
AssurancePlan
  ↓
Topology / ExecutionPlan
  ↓
primary execution
  ↓
deterministic gates + runtime sensors
  ↓
EvidenceReceipt[]
  ↓
fresh semantic review when required
  ↓
AcceptanceVerdict
  ↓
CI / release
```

## Related

- [Skill Kit knowledge-base integration for the Harness Rig Context plane](skill-kit-knowledge-base-context.md)
- [Roadmap](roadmap.md)
