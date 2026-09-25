---
id: harness-rig-openspec-spec-engine-and-authority
title: OpenSpec spec engine, authority, and brainstorming integration
summary: 'OpenSpec-first spec-driven architecture for Harness Rig: default external SpecEngine, content-addressed authority,
  authorization separation, validation/archive guards, rigor tiers, and no hard dependency.'
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- User-supplied openspec-brainstorming-improved.zip, supplied 2026-09-21
- Harness Rig planning analysis, refreshed 2026-09-21
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
# Status

This page defines the **recommended Harness Rig integration architecture** for OpenSpec.

It is based primarily on the supplied `openspec_harness_engineering_analysis.md`, whose historical research snapshot checked OpenSpec v1.13.1, plus a current planning-baseline recheck of OpenSpec v1.13.2 on 2026-09-24.

OpenSpec becomes Harness Rig's **default first-class specification engine for behavior-changing work** when it is present and enabled.

OpenSpec does **not** become a hard Harness Rig package/runtime dependency.

# Product role

Harness Rig should use OpenSpec as:

```text
durable behavioral intent
+ isolated change planning
+ behavioral delta specifications
+ conditional change design
+ implementation task state
+ archive/change history
```

Harness Rig continues to own:

```text
generic authority contracts
action authorization
exact implementation state
risk/assurance policy
execution topology
host capability negotiation
deterministic evidence
runtime sensors
acceptance
release/governance
```

The governing wording is:

> OpenSpec specifications are the durable source of agreed behavioral intent.

Do not interpret them as automatic proof of deployed/runtime behavior.

# No hard dependency

The Harness Rig repository should contain:

```text
generic SpecEngine contract
OpenSpec adapter
OpenSpec capability detection
authority fingerprinting
config-health checks
validation/archive guards
integration tests
compatibility policy
documentation
```

The Harness Rig repository should **not** vendor or require:

```text
OpenSpec source
OpenSpec npm package as Harness Rig runtime dependency
copied OpenSpec schemas/templates
OpenSpec parser/merge implementation
OpenSpec Store implementation
copied OpenSpec agent skills as normative Harness Rig logic
```

Runtime relationship:

```text
Harness Rig
    ↓
SpecEngine
    ↓
OpenSpecAdapter
    ↓
subprocess / machine-readable OpenSpec CLI
    ↓
external OpenSpec installation
```

Harness Rig installation remains valid without OpenSpec.

A workflow whose project policy explicitly requires OpenSpec fails closed when the OpenSpec capability is unavailable.

# SpecEngine contract

The first generic contract should be intentionally small.

Conceptual operations:

```text
discover
health
capabilities
context
inspect/list changes
artifact graph
artifact instructions
validate
readiness
semantic review when supported
archive
authority fingerprint
```

Do not expose OpenSpec-specific file formats through the core contract.

The adapter asks the installed engine what artifacts, dependencies, and instructions govern the selected schema.

# Capability model

A SpecEngine adapter should expose capabilities rather than one `supported` Boolean.

OpenSpec capabilities may include:

```text
local_change
behavioral_deltas
custom_schema
strict_validation
effective_instructions
semantic_verify
archive
stores
referenced_stores
```

Harness Doctor reports detected version and verified capability maturity.

Treat OpenSpec Stores/references/worksets as experimental integration surfaces while upstream marks them beta.

# Main spec-driven flow

Recommended default flow for behavior-changing work:

```text
user/engineering intent
      ↓
spec-impact classification
      │
      ├─ no durable behavior change
      │      ↓
      │   explicit no-spec-change path
      │
      └─ behavior change / uncertain
             ↓
      brainstorm / explore if needed
             ↓
       normalized behavior contract
             ↓
        human/authorized approval
             ↓
          OpenSpec change
             ↓
    schema-defined artifact graph
             ↓
    proposal / behavioral deltas
      / conditional design / tasks
             ↓
       strict validation + health
             ↓
       semantic coherence review
          when assurance warrants
             ↓
         AuthoritySnapshot
             ↓
      implementation authorization
             ↓
          Harness Rig Assurance
```

Do not create permanent Harness Rig `intake.md`, `brainstorm.md`, or duplicate planning artifacts by default.

# Brainstorming responsibility

During uncertain planning, classify temporary findings as:

```text
Observed fact
User decision
Material assumption
Open question
```

Resolve only uncertainty that can materially change:

- observable behavior;
- scope;
- compatibility;
- migration;
- failure semantics;
- acceptance conditions;
- authority/authorization.

The brainstorming layer converges to the smallest coherent valuable change.

It does not become another durable planning database.

# Spec-impact decision

Before requiring behavior specifications, determine:

```text
BEHAVIOR_CHANGE
NO_BEHAVIOR_CHANGE
UNKNOWN
```

Interpretation:

- `BEHAVIOR_CHANGE`: use the configured spec engine.
- `NO_BEHAVIOR_CHANGE`: behavioral specs are not required; normal Harness Rig assurance still applies.
- `UNKNOWN`: explore/brainstorm until the distinction is safe enough to decide.

OpenSpec `skip_specs` is a planning/schema mechanism only.

`skip_specs` must never mean `skip verification`.

# Artifact authority ownership

Use one authoritative owner for each knowledge class.

| Knowledge | Preferred owner |
|---|---|
| Why / change boundary | proposal |
| Required observable behavior | capability/delta specifications |
| Change-specific non-obvious technical decisions | design |
| Current work decomposition | tasks |
| Existing full RFC/architecture | existing authoritative design source |
| Executable behavior evidence | tests/gates |
| Structural constraints | architecture/static mechanisms |
| Operational reality | telemetry/runtime sensors |
| Harness Rig policy | Harness Rig |

Do not copy a detailed existing RFC/ORR/ownership source into OpenSpec merely to make OpenSpec self-contained.

Reference it and record only change-specific decisions or behavioral obligations.

# AuthorityRef becomes content-addressed

A named OpenSpec change is not enough to identify authority.

A conceptual OpenSpec `AuthorityRef` should carry:

```text
provider = openspec
resolved root/store identity
change identity
schema identity
engine version/capability profile
authority-bearing content fingerprint
validation/readiness state
```

The fingerprint should cover authority-bearing content rather than incidental timestamps.

Candidate inputs include:

```text
proposal
behavioral delta specifications
implementation-constraining design decisions
relevant effective planning context/rules
selected schema identity
```

Exact canonicalization remains an implementation decision.

# Two-dimensional freshness

Harness Rig evidence is valid only while both identities remain relevant:

```text
authority_id
  what was agreed?

state_id
  what implementation was evaluated?
```

Therefore:

```text
EvidenceReceipt
  authority_id = A
  state_id = S
```

becomes stale if:

- authority changes from `A` to `B`; or
- implementation state changes from `S` to `T`;

unless the gate explicitly proves independence from the changed dimension.

This is a core Harness Rig design principle, not an OpenSpec implementation detail.

# Authority is different from authorization

Keep these concepts separate:

```text
AuthorityRef
  defines the behavior/constraint to satisfy

AuthorizationGrant
  defines which action is currently permitted
```

Possible actions include:

```text
planning_write
implementation_write
merge
publish
deploy
destructive_operation
```

An approved specification does not automatically authorize implementation.

An accepted implementation does not automatically authorize deployment or publication.

Interactive OpenSpec planning may require a separate apply request.

Pre-authorized automation may operate under an explicit bounded authorization grant instead of asking again at every step.

# Rigor tiers

Harness Rig should make OpenSpec the normal engine for durable behavior changes without forcing identical ceremony onto every edit.

Recommended tiers:

## Tier 0 — trivial/non-behavioral

Examples: formatting, straightforward refactor, tooling-only, documentation.

Use:

- explicit no-spec-change decision where relevant;
- project build/static/tests appropriate to the edit.

Do not manufacture behavior requirements.

## Tier 1 — small behavior change

Use:

- concise proposal;
- behavioral delta;
- tasks with verification;
- affected deterministic tests.

Design is optional.

## Tier 2 — normal feature

Use:

- proposal;
- behavioral deltas;
- conditional design;
- tasks;
- appropriate deterministic project evidence;
- semantic review where useful.

## Tier 3 — cross-service/invariant-sensitive

Add risk-specific architecture, contract, security, compatibility, concurrency, migration, or load evidence.

Reference existing authoritative architecture/readiness sources.

## Tier 4 — high-consequence migration/security/protocol/data work

Require stronger behavioral/design clarity, migration/rollback evidence, risk-specific deterministic verification, and independent judgment where the consequence warrants it.

The goal is sufficient evidence, not maximum ceremony.

# Strict validation is not semantic proof

Expose an OpenSpec validation gate such as:

```text
authority.openspec.validate
```

A PASS means the OpenSpec artifacts satisfy the structural/semantic checks that the invoked OpenSpec validation command actually implements.

It does **not** prove product behavior.

OpenSpec semantic verification is also inferential review and remains secondary to stronger deterministic evidence for mechanically testable properties.

# Config health guard

The supplied analysis records current upstream issue evidence that malformed OpenSpec configuration/rules may be ignored while ordinary validation can still exit successfully.

Until upstream behavior eliminates this gap, Harness Rig's OpenSpec health gate should verify both:

```text
OpenSpec validation
AND
expected effective context/rules/instructions are actually loaded
```

Keep OpenSpec `config.yaml` small:

- terminology;
- planning-specific stable constraints;
- pointers to authoritative sources;
- universally relevant non-obvious context.

Do not turn it into the engineering handbook.

# Archive is a guarded state transition

Treat OpenSpec archive as a correctness-sensitive mutation of durable intent.

Harness Rig should not reimplement delta merging.

It should guard the transition:

```text
pre-archive
  authority/spec snapshot
  current change delta
  structural validation
  required Harness evidence

OpenSpec archive

post-archive
  resulting durable spec fingerprint
  expected delta postconditions
  archived change state
```

Record the guard result through ordinary `EvidenceReceipt`/artifact references.

Recent OpenSpec releases have hardened archive behavior, and the supplied analysis records still-open requests for stronger archive postconditions. Version pinning/compatibility evidence therefore matters.

# Existing detailed designs

When a detailed design/RFC already exists:

```text
existing authoritative design
      ↓ reference
OpenSpec proposal
      ↓
behavioral deltas
      ↓
design.md only for new decisions/deviations
      ↓
tasks
```

For high-consequence ingestion, an optional transient source-preservation review may compare the source design with the resulting OpenSpec artifacts and report:

- lost behavioral obligations;
- missing constraints;
- unsupported assumptions;
- contradictions.

Do not persist another trace artifact unless auditability genuinely requires it.

# Stores and shared specifications

OpenSpec Stores are strategically relevant for:

- shared contracts;
- platform capabilities;
- planning before a code repository exists;
- multi-repository behavioral intent.

Do not make Stores foundational while upstream marks them beta.

Recommended sequence:

```text
repo-local OpenSpec
  ↓
stable OpenSpec adapter
  ↓
small shared-Store pilot
  ↓
evaluate real cross-repo workflow evidence
```

Reuse existing repository/service ownership sources where they exist.

Do not invent a second ownership registry merely to satisfy Store planning.

# Custom schemas

Custom schemas are process policy.

Do not proliferate Harness Rig-specific OpenSpec schemas initially.

Start close to the stock `spec-driven` model and customize only after recurring measured friction or missed failure classes justify it.

Before adding a custom artifact, answer:

> What property validates this artifact beyond the model reading its own output?

# Drift responsibility

OpenSpec durable intent can drift from code/runtime.

Harness Rig should eventually support targeted drift controls for high-value capabilities:

```text
behavior-changing PR
  -> spec-impact decision

high-value capability
  -> targeted spec/code/test drift review

production escape
  -> update smallest durable intent/evidence control
```

Do not continuously re-read the entire repository with an LLM merely to claim synchronization.

# Pilot before strong organizational claims

Before declaring the integration mature, pilot representative work:

1. small behavioral feature;
2. vague request;
3. existing detailed design;
4. cross-service change;
5. high-risk migration/invariant change;
6. no-behavior-change defect/refactor.

Measure:

```text
missing requirements
late assumptions
spec churn after implementation begins
implementation/spec divergence
rework
false-done rate
human review time
agent context/token cost
stale specs
archive/validation failures
custom controls that still catch distinct failures
```

# Non-goals

Do not make Harness Rig:

```text
an OpenSpec fork
an OpenSpec parser
an OpenSpec package distribution
an OpenSpec Store implementation
a duplicate ORR/RFC system
a universal requirement to create OpenSpec artifacts for every edit
a system that treats OpenSpec semantic verify as formal proof
a system that treats OpenSpec specs as runtime truth
```

## Related

- [North star and product boundary](north-star-and-product-boundary.md)
- [Contracts, state, and evidence](contracts-state-and-evidence.md)
- [Roadmap](roadmap.md)
- [Acceptance evaluations and metrics](acceptance-evals-and-metrics.md)
- [Source register](source-register.md)
