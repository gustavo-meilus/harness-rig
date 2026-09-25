---
id: harness-rig-tacticswitch-loop-proposals-disposition
title: TacticSwitch loop and runtime-policy proposals disposition
summary: Harness Rig disposition of the richer runtime-execution, bounded recurrence, hosted quality-gate, adversarial-assurance,
  and native-smoke proposals.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- Archive README.md, VALIDATION.md, ALIGNMENT-REVIEW.md, and OpenSpec proposal/design/spec/task files, reviewed 2026-09-21
- Harness Rig planning analysis, refreshed 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
---
# Status and source boundary

This page records Harness Rig's disposition of the user-supplied `tacticswitch-openspec-loop-proposals.zip`.

The archive contains OpenSpec proposals, designs, specs, tasks, structural validation, and an alignment review. It explicitly states that OpenSpec CLI validation still needs to run in the authoritative TacticSwitch repository. Treat the archive as **proposed design**, not current implementation.

The package is materially more ambitious than the earlier v3 proposal bundle. It expands:

- runtime execution policy;
- outer-loop recurrence;
- hosted quality/adversarial/native assurance.

Harness Rig should preserve the demonstrated control semantics without importing the proposed schemas wholesale.

# Executive disposition

| Source proposal | Keep | Reshape | Ignore/defer |
|---|---|---|---|
| Runtime execution policy | topology before compute; risk separate from reasoning difficulty; proportional required/preferred/advisory constraints; requested/resolved/observed facts; targeted escalation | express through `ExecutionPlan`, host capabilities, and a bounded `RuntimeResolution` artifact | standalone runtime-policy service, duplicated risk/freshness/permissions authority, central model catalog, generic telemetry platform |
| Loop integration contract | objective completion; finite cycles; state/failure fingerprints; changed-action requirement; least authority; side-effect gate; compact continuation; idempotency | keep recurrence outside core initially; reuse `AuthorityRef`, `StateIdentity`, `AcceptanceVerdict`; host owns scheduling/persistence | scheduler, queue, daemon, webhook service, transaction framework, general loop database |
| Operationalize loop assurance | canonical hosted gate; observed check identities before protection; manual slow assurance; demand-driven native smokes; bounded artifacts; fail-fast ordering | implement under Harness Rig CI/evals; native results feed capability evidence | one scheduled workflow per adapter, universal native gauntlet, automatic support promotion |

# Runtime execution policy: preserve semantics, not ownership duplication

The source proposal defines a portable per-dispatch execution intent containing logical responsibility, phase, change risk, reasoning difficulty, model/effort intent, freshness, permissions, budget, and fallback behavior.

Harness Rig should not copy that object literally because several fields already have authoritative owners.

Recommended ownership:

```text
AssurancePlan
  change risk
  required assurance
  required independence
  human authority requirements

ExecutionPlan
  responsibility
  ownership
  isolation
  freshness
  permissions

ExecutionHint
  reasoning difficulty
  preferred capability class
  preferred effort class
  bounded execution preference

HostAdapter
  RuntimeResolution
```

This prevents risk, freshness, permissions, and authority from existing in multiple independently mutable schemas.

# Topology before compute

Preserve the source rule:

> Runtime execution policy operates only after the minimum-sufficient route and worker responsibility are selected.

A model, effort, or capability preference must not:

- create another worker;
- transfer implementation ownership;
- add a specialist;
- change R0-R4 topology;
- weaken mandatory independent verification.

R0 remains direct when direct execution is otherwise sufficient.

# Required, preferred, and advisory constraints

Preserve proportional enforcement.

A useful portable interpretation is:

```text
fresh independent verifier    required
read-only verifier            required
minimum capability floor      required only when explicitly justified
higher reasoning effort       preferred/advisory unless explicitly required
lower-cost worker             preferred
```

Missing a required capability fails closed.

Missing a preferred or advisory execution preference may use a safe host-selected alternative when the actual resolution and reason are recorded.

High change risk alone must not silently convert model or effort preference into a mandatory compute floor.

# Requested, resolved, and observed facts

This is one of the strongest additions and should enter Harness Rig's host model.

Keep three distinct layers:

```text
requested
  what the portable plan asked for

resolved
  what the adapter configured or selected

observed
  what the host/runtime can actually prove happened
```

Do not infer observed facts from configuration alone.

Useful bounded resolution states from the source include:

```text
PINNED
INHERITED
FALLBACK
UNSUPPORTED
UNVERIFIED
```

The source also distinguishes advisory-only recommendations. Harness Rig should finalize the exact enum only after cross-host evidence.

Unknown or ambiguous outcomes fail toward `UNVERIFIED`, never toward stronger proof.

# RuntimeResolution is not a second evidence universe

Harness Rig should not introduce a standalone persisted runtime-receipt system parallel to `EvidenceReceipt`.

Preferred shape:

```text
ExecutionPlan
    ↓
HostAdapter
    ↓
bounded RuntimeResolution artifact
    ↓
EvidenceReceipt references artifact when material
```

The runtime artifact may contain compact requested/resolved/observed facts, active runtime identity/mode, capability gaps, and evidence references.

Do not persist:

- full prompts;
- transcripts;
- private reasoning;
- full diffs;
- raw home directories;
- verbose secret-bearing logs.

# Targeted escalation and downgrade

Preserve the source's adaptive-compute idea as field-hardening behavior:

- use the lowest evidenced adequate compute for a responsibility;
- do not escalate merely because a task is high consequence;
- escalate the bounded failed/uncertain responsibility when semantic or causal difficulty justifies it;
- re-resolve later settled work rather than inheriting previously escalated compute forever;
- allow downgrade when representative evaluator-owned evidence supports it.

Do not make benchmark-driven execution calibration part of the initial kernel.

It belongs after exact-state acceptance and host-resolution evidence are trustworthy.

# Recurrence: keep the control semantics

The outer-loop proposal contains several strong controls.

An unattended recurrence contract should require:

- an objective completion/failure signal;
- a finite cycle bound;
- current authoritative state reconciliation;
- progress detection;
- a bounded failure fingerprint;
- a changed-action rule after failure;
- an escalation/stop rule;
- least-authority execution;
- explicit side-effect authority;
- duplicate-trigger protection;
- bounded terminal reasons.

Model prose cannot independently produce terminal success.

# Portable cycle budget

The source proposal requires both finite cycle and finite wall-clock budgets for unattended loops, with token/cost ceilings optional when trustworthy telemetry exists.

Harness Rig's recommended portable contract is narrower:

```text
max_cycles        REQUIRED
deadline/timebox  OPTIONAL or host-owned
token budget      OPTIONAL / host-owned
cost budget       OPTIONAL / host-owned
```

Reason: `max_cycles` provides a deterministic provider-neutral bound. Wall-clock semantics can become ambiguous across scheduled waits, external approvals, CI waits, and dormant host time.

Hosts may impose stronger deadlines without changing portable Harness Rig semantics.

# Progress and failure fingerprints

Keep the source distinction between state progress and failure progress.

A recurrence record should be able to compare:

```text
current StateIdentity
bounded deterministic failure fingerprint
external dependency/approval state
bounded next-action class
```

After a failed cycle, budget remaining is not enough to retry.

Another cycle requires at least one material continuation signal:

- state changed;
- deterministic failure evidence changed;
- external dependency or approval changed;
- bounded next-action class changed.

An unchanged repair attempt against unchanged state/failure stops as `NO_PROGRESS` or the applicable blocker instead of consuming the remaining cycle budget blindly.

Changing `repair -> diagnose` may permit another cycle, but the changed label itself is not proof of progress.

# Least authority and side effects

Recurrence must not widen technical authority merely because work is autonomous or repeated.

Reuse Harness Rig's general Authority model for outward or irreversible operations such as:

- merge;
- publish;
- external messaging;
- production mutation;
- destructive data action;
- security/permission change.

A passing implementation does not authorize an outward side effect.

An approval does not prove implementation correctness.

A materially changed target/scope invalidates stale approval.

# Compact continuation state

If recurrence is implemented, keep continuation state storage-neutral and bounded.

Useful facts include:

```text
loop/cycle identity
trigger identity
cycle count
optional time anchor
StateIdentity/progress fingerprint
failure fingerprint/count
bounded next-action class
terminal/blocker reason
approval reference/status
compact evidence references
```

Do not duplicate:

- orchestration batch ledgers;
- full transcripts;
- full diffs;
- raw logs;
- copied specifications;
- private reasoning.

Keep this record outside the kernel initially.

Promote only if multiple independent recurrence consumers demonstrate the same stable need.

# Fresh primary context

Preserve the capability, not a universal reset mandate.

For unattended autonomous cycle boundaries, a fresh primary context can reconstruct from:

- loop contract;
- compact continuation state;
- current repository/framework state;
- only evidence required for the next gate.

One coherent interactive bounded task may keep a warm context.

Host capability/policy decides whether fresh-cycle reconstruction can actually be enforced.

# Trigger idempotency

Preserve the invariant:

> The same logical `(loop_id, trigger_id)` must not create two concurrent writers or duplicate outward actions.

Do not build generic distributed infrastructure in Harness Rig core to satisfy this.

The host adapter owns the mechanism:

- file lock for local/file-backed integrations;
- platform concurrency primitive where available;
- scheduler-native deduplication where available.

The recurrence contract describes the required behavior, not the storage/locking technology.

# Terminal reasons

The source proposal needs richer terminal reasons than the earlier simple five-state sketch.

Harness Rig should preserve bounded distinctions such as:

```text
DONE
CONTINUE
BUDGET_EXHAUSTED
NO_PROGRESS
HUMAN_GATE
INVALID_CONTRACT
EXTERNAL_WAIT
INNER_ROUTE_BLOCKED
```

Exact names remain open until implementation.

Do not collapse every non-success into one generic `BLOCKED` if the reason determines the next safe action.

# Hosted quality gate: move this earlier

The source proposal identifies a real operational gap: having a canonical local gate is not the same as having hosted evidence and merge enforcement.

Harness Rig `0.5` should include:

```text
pull_request
push to main
workflow_dispatch
    ↓
same canonical ordinary quality command
    ↓
real observed check identities
    ↓
ruleset/branch protection only after those identities exist
```

Do not guess required check names.

Do not duplicate the ordinary correctness command list in workflow YAML.

Hosted CI consumes the same canonical gate.

# Slow assurance: one proportional surface

Preserve one optional slow-assurance entry point.

Default behavior:

- manual dispatch;
- deterministic canonical prerequisite first;
- adversarial assurance only when relevant;
- native adapter smoke only for the adapter/mode whose evidence is decision-relevant;
- bounded structured artifacts;
- unavailable runtime/authentication remains an evidence gap;
- no automatic adapter promotion.

Only schedule a slow/native job after repeated real runs demonstrate:

- stable environment;
- explicit evidence-freshness requirement;
- acceptable reliability;
- justified quota/cost;
- distinct signal not provided by a cheaper sensor.

Jobs that become redundant or chronically unavailable should return to manual-only or be removed.

# Native host conformance belongs in 0.6

This package strengthens the roadmap here.

Host capability claims should be backed by native evidence when the claim depends on native runtime behavior.

Useful native smoke observations include:

- worker creation;
- isolation/freshness;
- permissions;
- fail-closed behavior;
- requested/resolved/observed runtime execution facts;
- interactive versus headless/ephemeral mode where claimed.

One successful mode does not prove an untested mode.

One successful smoke does not automatically promote an adapter to Stable.

# What to ignore

Do not import these as Harness Rig architecture:

```text
standalone runtime-policy service
duplicate risk/freshness/permissions authority
central model catalog
pricing service
generic runtime telemetry platform
second persistent runtime evidence system
benchmark calibration in core
loop-specific authority system
generic scheduler
queue
daemon
webhook server
state database/service
distributed lock service
side-effect transaction framework
mandatory portable token/cost accounting
one scheduled workflow per host adapter
universal native gauntlet
automatic support promotion from one smoke
```

# Alignment-review limitation

The package's `ALIGNMENT-REVIEW.md` is useful design evidence that the proposals were revised to fit More With Less and Engineering Discipline principles.

Its `PASS` assessments do **not** prove that:

- runtime policy improves accepted-task outcomes;
- recurrence prevents real production failures;
- the proposed host smoke cadence is cost-effective;
- benchmark-driven compute optimization generalizes.

Those require implementation and field evidence.

# Apply-time validation boundary

The archive states that OpenSpec CLI validation was not available when the bundle was prepared.

Before applying the proposals in TacticSwitch, run strict OpenSpec validation in the authoritative repository with the installed OpenSpec version and then run each proposal's required implementation validation.

Do not treat unavailable native/adversarial checks as passed.

## Related

- [Roadmap](roadmap.md)
- [Target architecture](target-architecture.md)
- [Contracts, state, and evidence](contracts-state-and-evidence.md)
- [Host adapters and capability negotiation](host-adapters-and-capabilities.md)
- [CI, review, versioning, and release governance](ci-review-and-release-governance.md)
- [Acceptance evaluations and metrics](acceptance-evals-and-metrics.md)
