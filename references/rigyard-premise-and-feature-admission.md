---
id: harness-rig-rigyard-premise-and-feature-admission
title: RigYard premise and minimum-sufficient feature admission
summary: 'More-With-Less product premise for Harness Rig: a small deterministic composition/evidence kernel, explicit feature
  inclusion tiers, and complexity retirement rules, with RigYard source-access limitations preserved.'
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Harness Rig planning analysis, refreshed 2026-09-21
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
# Evidence status

The project premise on this page is now backed by the user-supplied `rigyard_current.zip` source snapshot inspected
2026-09-24.

That snapshot permits source-level inspection of current implementation, tests, retained verification evidence, archived
OpenSpec changes, and 8 active/unarchived OpenSpec changes. It does not contain `.git/`, so exact repository history and
current branch/tag identity are not independently reconstructable from the ZIP alone.

Use [RigYard current source and verification baseline](rigyard-current-source-and-verification-baseline.md) for the
evidence-maturity classification. Planned RigYard OpenSpec changes remain proposals until explicitly reconciled; they are
not automatically Harness Rig requirements.

# RigYard premise

The most useful RigYard premise is:

> Build one small control plane that makes existing engineering mechanisms composable, state-bound, evidence-producing, and auditable without replacing the mechanisms that already own specifications, repository knowledge, runtime behavior, testing, CI, or host execution.

Harness Rig should therefore be a **composition and evidence kernel**, not a universal AI-development framework.

Its differentiated value is knowing:

```text
what authority applies
what action is authorized
what implementation state exists
what assurance is required
what execution topology is sufficient
what host/tool capabilities are available
what evidence was actually produced
whether the current authority/state may be accepted
```

# More With Less doctrine applied to Harness Rig

The current More With Less skill defines the objective as the **minimum sufficient system** that preserves required guarantees.

Its mandatory design consequences for Harness Rig are:

- inspect before simplifying;
- delete/reuse before adding;
- use the least powerful sufficient mechanism;
- keep context progressive;
- one agent by default;
- minimize tools and authority;
- make specification proportional;
- make verification proportional;
- preserve security, authorization, integrity, accessibility, rollback, observability, and explicit invariants;
- prefer root-cause fixes;
- design new harness mechanisms for eventual deletion.

The decision ladder is:

```text
Does this need to exist?
  ↓
Is the project already handling it?
  ↓
Can deterministic project machinery handle it?
  ↓
Can native/runtime/platform behavior handle it?
  ↓
Can an existing dependency/tool handle it?
  ↓
Can one small deterministic mechanism handle it?
  ↓
Can one agent handle it?
  ↓
Does one specialist materially help?
  ↓
Does one bounded loop materially help?
  ↓
Only then custom orchestration/infrastructure
```

Every substantial Harness Rig feature should be able to explain where it enters this ladder and why earlier rungs are insufficient.

# Core product value

Harness Rig should own only the cross-cutting semantics that existing tools do not jointly provide.

Recommended core value:

```text
SpecEngine abstraction
AuthorityRef
AuthorizationGrant
StateIdentity
ContextManifest
AssurancePlan
ExecutionPlan
EvidenceReceipt
AcceptanceVerdict
CapabilitySet
```

Potential adapter/application records such as `RuntimeResolution` or recurrence continuation state stay outside the core until multiple real consumers justify promotion.

# One source of truth per knowledge class

Preferred ownership:

| Knowledge / mechanism | Owner |
|---|---|
| Durable behavioral intent and deltas | OpenSpec when active |
| Broad repository onboarding/context | Harness Rig Context evolved from AIBoarding |
| Risk/evidence requirement | Harness Rig Assurance |
| Minimum execution formation | Harness Rig Topology evolved from TacticSwitch |
| Exact source state | Git-derived Harness Rig StateIdentity |
| Executable behavior | project tests/gates |
| Architecture constraints | project-native deterministic architecture checks |
| Browser/runtime behavior | Playwright/runtime sensors |
| Operational truth | telemetry/runtime systems |
| Host-specific execution behavior | host adapters/native host |
| Repository merge/release enforcement | CI/repository platform |
| Cross-tool evidence/acceptance | Harness Rig |

Harness Rig should reference these sources rather than copy their content into another canonical representation.

# Features that belong in Harness Rig

## Tier A — core, required product identity

These features solve cross-tool problems and should be first-class:

```text
generic SpecEngine contract
content-addressed AuthorityRef
AuthorizationGrant
exact StateIdentity
AssurancePlan
ExecutionPlan
EvidenceReceipt
AcceptanceVerdict
CapabilitySet
staleness detection across authority + state
fail-closed required-capability semantics
governance/change classification
one repository-wide acceptance verdict
```

These are the center of the product.

## Tier B — first-class built-in modules/adapters

These are included because they are necessary to make the core useful, but they are not core truth owners:

```text
Context module evolved from AIBoarding
Assurance module evolved from Adaptive Engineering Harness
Topology module evolved from TacticSwitch
OpenSpec adapter as default external SpecEngine
direct/manual authority provider
Claude/Codex/Copilot host adapters
command/test gate
architecture gate
OpenSpec validation/health/archive guards
Playwright runtime gate
GitHub CI/ruleset adapter
Harness Doctor
legacy migration tooling
generated host distributions
```

External engines/tools remain loose runtime capabilities rather than package dependencies.

## Tier C — earned optional features

Add only after measured recurring failure demonstrates value:

```text
bounded autonomous recurrence
adaptive model/effort calibration
additional knowledge infrastructure
shared OpenSpec Store integration beyond small pilots
custom OpenSpec schemas
source-preservation review
requirements-quality review
targeted spec/code drift analysis
additional security/performance/migration gate providers
```

Each must have:

```text
failure it solves
measurable evidence of value
bounded scope
cost/complexity budget
fallback/degraded behavior
retirement or downgrade condition
```

## Tier D — deliberately external or rejected by default

Do not build these into Harness Rig unless future evidence overturns the decision:

```text
OpenSpec implementation/vendor fork
custom replacement specification system
new test framework
general scheduler/queue/daemon
distributed lock service
side-effect transaction platform
central model/pricing catalog
general telemetry platform
universal cloud control plane
hosted retrieval infrastructure
mandatory swarm/multi-agent workflow
public plugin marketplace before real third-party demand
generic ownership registry when another source already owns it
```

# Deterministic shell, probabilistic middle

Harness Rig should prefer deterministic code for:

```text
authority/state fingerprinting
schema checks
capability detection
permission constraints
protected paths
change classification
gate execution
evidence receipts
staleness checks
architecture rules
retry budgets
progress/failure comparison
merge/release policy
```

Use models for:

```text
brainstorming
semantic planning
implementation
investigation
trade-off reasoning
semantic review
```

For high-value claims, evidence production should not remain under the implementation agent's sole discretion.

# One agent by default

Default:

```text
one primary agent
+ deterministic feedback
```

Add another context only for:

```text
independent judgment
context isolation
different authority/permissions
specialized expertise
useful parallelism
```

Do not turn Harness Rig into a default committee architecture.

Topology exists precisely to keep escalation minimum-sufficient.

# Hooks

Hooks earn their place only for invariants that should not depend on model memory, such as:

```text
lifecycle persistence
permissions
completion gates
state/evidence capture
required restoration
```

Do not use hidden hooks merely to repeat optional advice, stylistic preferences, or generic routing suggestions.

# Specification proportionality

OpenSpec is the default engine for behavior-changing spec-driven work, but specification depth remains proportional:

```text
trivial/non-behavioral
  -> direct/no-spec-change

obvious bug
  -> expected behavior + regression

small behavior change
  -> concise behavior + acceptance

complex feature
  -> proposal/spec/design/tasks only where each removes distinct uncertainty

high-risk migration/security/protocol/data change
  -> explicit behavior/design/rollback/compatibility/strong evidence
```

# Verification proportionality

Verification strength grows with consequence:

```text
Tier 0
  format/build/type as applicable

Tier 1
  + affected tests

Tier 2
  + integration/executable acceptance

Tier 3
  + architecture/security/property/migration checks where relevant

Tier 4
  + independent semantic review where mechanical evidence is insufficient
  + mutation where oracle sensitivity matters
  + UI/E2E evidence where users are affected
  + external provenance for high-value measurements
```

Do not run an expensive gauntlet just because it exists.

# Feature admission template

Every non-trivial proposed Harness Rig feature should answer:

```text
Problem:
Which repeated concrete failure exists?

Existing mechanisms:
Which project/native/external mechanism already addresses it?

Gap:
Why are those mechanisms insufficient?

Smallest mechanism:
What is the least powerful additional mechanism?

Authority:
What new authority/tool/permission/state does it add?

Evidence:
How will we know it improves outcomes or closes the failure?

Degraded mode:
What happens when it is unavailable?

Retirement:
What would allow deletion, collapse, or downgrade?

Core test:
Why must this be core instead of an adapter/gate/application feature?
```

A missing credible answer is grounds to defer the feature.

# Complexity budget

Track architecture complexity as a first-class product metric.

Useful counts/trends include:

```text
core contract count
persistent state/schema count
external runtime dependencies
always-loaded context size
host-specific branches
gate providers
hooks
agent roles
handoffs
required CI checks
manual compatibility matrices
deprecated/legacy surfaces
```

The target is not zero.

The target is that each item still earns its maintenance burden.

# Expected mature Harness Rig

A mature deployment should resemble:

```text
             INTENT
               │
               ▼
     SpecEngine / OpenSpec
               │
         AuthorityRef
               │
       AuthorizationGrant
               │
               ▼
            Context
               │
               ▼
         AssurancePlan
               │
               ▼
           Topology
               │
         ExecutionPlan
               │
               ▼
        primary execution
               │
       deterministic gates
        + runtime sensors
               │
       EvidenceReceipt[]
               │
     fresh review if needed
               │
               ▼
      AcceptanceVerdict
               │
        CI/release policy
```

Most ordinary work should travel through the simplest subset of this diagram.

# Reconciliation requirement

This page remains a product-premise/admission page; source-level RigYard implementation facts belong in the dedicated current-source baseline.

During the progressive Harness Rig reconciliation:

1. inspect manifests/dependencies;
2. inspect core schemas/contracts;
3. inspect state/evidence implementation;
4. inspect OpenSpec/host adapters;
5. inspect hooks/CI/tests;
6. inspect planned changes/issues;
7. compare actual components against this feature-admission policy;
8. remove or reclassify any premise that actual implementation falsifies.

## Related

- [Roadmap](roadmap.md)
- [Target architecture](target-architecture.md)
- [OpenSpec spec engine, authority, and brainstorming integration](openspec-spec-engine-and-authority.md)
- [Risks, non-goals, and deferred work](risks-non-goals-and-deferred-work.md)
- [Decision log](decision-log.md)
