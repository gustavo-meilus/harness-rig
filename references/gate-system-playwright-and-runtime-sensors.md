---
id: harness-rig-gate-system-playwright-and-runtime-sensors
title: Gate system, Playwright, and runtime sensors
summary: Gate-provider model for deterministic evidence and a Playwright integration that treats browser automation as a sensor
  rather than the source of product truth.
version: planning-baseline-2026-09-25-r8.9
updated: '2026-09-25'
provenance:
- Adaptive Engineering Harness verification ladder, accessed 2026-09-21
- Playwright official documentation for coding agents and test agents, accessed 2026-09-21
- OpenAI Harness Engineering application-legibility section, 2026-02-11
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- Playwright Test 1.63.0 CLI, JSON reporter, and retry/flaky behavior rechecked 2026-09-25
- Harness Rig M9 executable gate-platform implementation and adversarial fixtures, 2026-09-25
---
# M9 realized boundary

M9 implements the minimum shared `GateClaim`/`GateOutcome` vocabulary plus concrete architecture, Playwright, and mutation providers. These semantics are Experimental; provider-native evidence remains referenced rather than flattened. The authoritative M9 implementation record is [M9 gate platform, Playwright, architecture, and mutation verification](m9-gate-platform-playwright-architecture-mutation.md).

The Playwright provider now requires explicit scenarios, preserves retry/flaky evidence, forbids `--pass-with-no-tests`, and uses a provider-native runtime sidecar for worktree/data/console/network observations. No local Node `@playwright/test` installation was available in the qualification environment, so fixture/subprocess protocol evidence is not presented as a live native project run.

# Gate contract

A gate consumes relevant authority/state/configuration and produces an `EvidenceReceipt`.

Possible gate families:

```text
authority
syntax
static
type
unit
property
architecture
contract
integration
security
performance
migration
web.acceptance
semantic.review
```

Run cheap, high-signal gates before expensive or inferential gates.

# OpenSpec authority gates

When OpenSpec is the active SpecEngine, useful gates include:

```text
authority.openspec.health
authority.openspec.validate
authority.openspec.archive-guard
semantic.openspec.conformance   # inferential, optional
```

Interpretation:

- `health`: executable/version/root/config/effective-rule capability is usable.
- `validate`: OpenSpec's invoked validation checks pass.
- `archive-guard`: pre/post archive state transition satisfies Harness Rig expectations.
- `semantic.conformance`: OpenSpec/model semantic review; not formal proof.

Do not label semantic review as equivalent to executable correctness.

# Config-health protection

Until upstream guarantees malformed config/rules fail loudly, health checks should verify that expected effective instructions/rules are actually loaded rather than trusting a zero validation exit alone.

# Gate admission

A new gate should normally not change core.

Declare:

```text
id
kind
maturity
capabilities
dependencies
consumed authority/state
produced evidence
behavioral tests
```

# Architecture gate

Projects can encode dependency rules as deterministic fitness functions.

Architecture evidence remains independent of OpenSpec design prose.

# Playwright gate

Treat Playwright as a `web.acceptance`/runtime-observation provider.

A receipt can reference:

- test result;
- browser trace;
- screenshot;
- DOM/accessibility snapshot;
- console/network evidence.

Playwright does not define product truth.

# Application legibility

For stronger web autonomy, provide per-worktree runtime observability where justified:

```text
isolated app
isolated state/database
health check
browser session
logs
traces
metrics
```

# Oracle protection

A planner/healer/test generator may propose changes to expectations.

Changing protected behavioral authority/oracles invalidates or reopens authority rather than silently preserving acceptance.

# Clean Architecture role

Use Playwright for composed user/web behavior.

Use inner deterministic gates for business invariants and architecture boundaries.

## Related

- [OpenSpec spec engine, authority, and brainstorming integration](openspec-spec-engine-and-authority.md)
- [Research foundations](research-foundations.md)
- [Acceptance evaluations and metrics](acceptance-evals-and-metrics.md)
