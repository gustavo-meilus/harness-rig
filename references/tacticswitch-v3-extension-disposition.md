---
id: harness-rig-tacticswitch-v3-extension-disposition
title: TacticSwitch v3 extension disposition
summary: How the minimum-sufficient runtime-execution, recurrence, and hosted-assurance proposals fit into Harness Rig without
  creating new control planes.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- User-supplied tacticswitch-openspec-proposals-v3.zip, README.md, REVIEW.md, and proposal/spec/design files, supplied 2026-09-21
- Harness Rig planning analysis, refreshed 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
---
# Revision note

This page describes the earlier, narrower `tacticswitch-openspec-proposals-v3.zip` source set.

A later user-supplied package, `tacticswitch-openspec-loop-proposals.zip`, expands runtime execution, recurrence, hosted quality-gate, and native-assurance detail. Use [TacticSwitch loop and runtime-policy proposals disposition](tacticswitch-loop-proposals-disposition.md) for the current Harness Rig disposition.

The earlier v3 conclusions remain useful where they intentionally rejected new control planes and preserved minimum-sufficient topology.

# Status

This page records **future design input**, not current TacticSwitch or Harness Rig behavior.

The source is the user-supplied `tacticswitch-openspec-proposals-v3.zip`. Its revision intentionally reduces scope relative to earlier drafts and extends existing TacticSwitch mechanisms instead of adding parallel runtime, state, evidence, benchmark, or CI frameworks.

# Architectural disposition

| Proposal | Harness Rig disposition | Planned placement |
|---|---|---|
| `add-runtime-execution-policy` | Keep the narrow concept; do not create a new subsystem | Control-plane convergence and host-adapter work |
| `add-loop-integration-contract` | Keep as an optional future recurrence contract; do not put recurrence infrastructure in core | Field-hardening / optional host integration after exact-state acceptance is stable |
| `operationalize-loop-assurance` | Mostly transitional convenience; preserve the idea, not necessarily the TacticSwitch-specific workflow | Harness Rig adversarial eval/CI after unified CI exists |

# Optional post-route execution hints

The useful rule is:

> Choose topology first. Allocate optional compute/effort second.

The proposal adds only coarse, vendor-neutral `compute_class` and `effort_class` hints to a worker that the selected route already requires.

Preserve these constraints:

- change risk continues to govern assurance, ownership, independence, authority, and acceptance;
- reasoning difficulty may influence compute/effort for an already-justified responsibility;
- an execution hint must not create a worker;
- it must not transfer ownership;
- it must not add an acceptance stage;
- it must not weaken an existing route requirement;
- R0 remains direct;
- unsupported hints fall back to safe native/default worker configuration if the mandatory worker capability itself is available;
- inability to create a mandatory independent worker still fails closed;
- requesting a hint is not evidence that the concrete runtime/model/effort was actually used;
- no runtime-policy state, runtime receipt framework, model catalog, pricing service, or telemetry subsystem is required.

In Harness Rig, this should be represented as an optional annotation on an already-selected responsibility or execution plan, not as a new policy plane.

Conceptual flow:

```text
AssurancePlan
    ↓
Topology chooses ExecutionPlan
    ↓
optional compute/effort annotation
    ↓
HostAdapter maps or safely ignores the annotation
```

# Keep risk, structure, and reasoning difficulty separate

Do not collapse all work into one `complexity` score.

At minimum preserve the conceptual distinction:

```text
change risk
  -> assurance strength

structural uncertainty / dependency shape
  -> discovery and topology

reasoning difficulty
  -> optional compute/effort escalation
```

A high-risk but routine change can need strong assurance without maximum compute. A low-risk, read-only architectural investigation can require high reasoning effort without production-write controls.

# Optional bounded recurrence

The loop proposal adds genuinely new behavior but deliberately leaves recurrence infrastructure with the host.

A Harness Rig recurrence integration should:

- be opt-in;
- run each cycle as an ordinary Harness Rig/TacticSwitch-controlled cycle against current authoritative state;
- require a host-controlled objective-completion result;
- require a finite `max_cycles`;
- use a bounded progress key;
- normally use canonical `StateIdentity` as the progress key for repository-mutating work;
- require a materially changed next action before repeating against unchanged progress;
- preserve existing `BLOCKED` behavior;
- reject stale evidence;
- reconstruct each cycle from bounded current inputs rather than replaying the full transcript;
- return a small deterministic decision.

The proposed decision set is:

```text
DONE
CONTINUE
BLOCKED
NO_PROGRESS
BUDGET_EXHAUSTED
```

Important semantics:

- model prose alone cannot produce `DONE`;
- `BLOCKED` does not become an automatic retry;
- unchanged progress plus unchanged action produces `NO_PROGRESS`;
- a changed action may allow another cycle only while the finite cycle budget remains;
- the generic loop does not prove convergence or semantic correctness of the host completion predicate.

# Recurrence remains outside the kernel initially

Do not add recurrence contracts to `core` merely because one host needs repeated cycles.

Prefer an application or host integration layer that consumes stable contracts such as:

```text
StateIdentity
AcceptanceVerdict
current blocker status
```

If several independent hosts later need the same recurrence contract, an HRP can consider promoting a minimal shared contract.

# Explicitly deferred recurrence machinery

Do not introduce these with the first recurrence implementation:

```text
loop-specific persistent state
state schema migration for loop bookkeeping
scheduler
queue
daemon
trigger-deduplication service
cross-process lock service
side-effect transaction framework
portable wall-clock budget
portable token budget
portable cost budget
internal strategy generator
full transcript replay
```

Hosts may enforce their own operational limits outside the portable Harness Rig contract.

# Hosted adversarial assurance

The uploaded `operationalize-loop-assurance` proposal is intentionally tooling-only. It composes the existing ordinary quality gate with the existing adversarial-assurance command and uploads the existing JSON report.

For Harness Rig, preserve the principle:

> Native assurance tools may keep their own detailed artifacts. Harness Rig evidence should reference them rather than forcing every tool into one oversized report schema.

Do not prioritize the TacticSwitch-specific manual workflow if the monorepo migration is beginning immediately. Recreate the capability later under Harness Rig's unified CI/eval surface.

# Sequencing

Recommended placement:

```text
0.1-0.3  exact state/evidence first
0.4      optional execution-hint contract after topology selection
0.6      actual host mapping only where capability evidence exists
0.9      optional bounded recurrence and manual adversarial entry point
```

The loop contract must not precede canonical state identity because its progress semantics depend on trustworthy state/evidence freshness.

## Related

- [Roadmap](roadmap.md)
- [Target architecture](target-architecture.md)
- [Host adapters and capability negotiation](host-adapters-and-capabilities.md)
- [Contracts, state, and evidence](contracts-state-and-evidence.md)
