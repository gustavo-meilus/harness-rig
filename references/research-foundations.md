---
id: harness-rig-research-foundations
title: Research foundations for Harness Rig
summary: Evidence-supported principles behind verification architecture, harness engineering, architectural boundaries, and
  browser-runtime sensors.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- Alexander Hinojosa, The Tests Were Green. They Were Lying., 2026-09-09
- Alexander Hinojosa and Claude, Your AI Coding Partner Will Tell You It's Done. Here's How to Actually Know., 2026-07-16
- 'Alexander Hinojosa and Claude, The Machinery: A Production Playbook for Coding with AI Agents, 2026-07-16'
- 'OpenAI, Harness engineering: leveraging Codex in an agent-first world, 2026-02-11'
- Google Developers Blog, The Anatomy of Harness Engineering, accessed 2026-09-21
- Robert C. Martin, The Clean Architecture, 2012
- Playwright official documentation, coding agents and test agents, accessed 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
---
# Supported engineering thesis

Reliable AI-assisted development should not depend on trusting the generating model, its self-report, a reviewer, or a green test by itself. Reliability should come from a control system that binds intent, implementation, observable verification, independent judgment where warranted, and acceptance to the same exact source state.

The verifier is also fallible. Tests, mutation systems, reviewers, heuristics, and gates can encode the wrong property or fail to detect realistic faults. A verifier gains credibility when it has demonstrated sensitivity to meaningful known-bad cases, but one positive control does not prove general correctness.

## Practical implications

Prefer:

- executable observations over model assertions;
- independent evidence over self-certification;
- fail-closed treatment of "unable to verify";
- deterministic enforcement for mandatory invariants;
- protected authority for requirements and critical oracles;
- fresh review contexts when independence materially reduces correlated failure;
- durable project state outside transient model context;
- application-runtime observability for integration behavior.

Do not infer that "more agents" automatically means more reliability. Extra contexts are useful only when they provide independent evidence, isolated cognitive work, or safe parallelism that outweighs coordination cost.

## Harness engineering

OpenAI describes a shift in engineering work toward specifying intent, structuring repositories, making applications and observability legible to agents, and building feedback loops. Its reported experience also warns against one giant instruction file: a short repository map plus structured deeper documentation is more maintainable and mechanically checkable.

Harness Rig should therefore make important claims inspectable and enforceable rather than adding more prose to model context.

## Clean Architecture application

Robert C. Martin's Dependency Rule is useful as an enforceable harness property:

- business policy remains inward;
- external mechanisms remain outward;
- dependencies point toward policy;
- domain behavior remains testable without requiring the web or database mechanism.

Harness Rig should express project-specific architectural boundaries as deterministic fitness functions where practical. Playwright then verifies web composition and user-visible behavior rather than becoming the sole proof of inner business invariants.

## Playwright application

Playwright is valuable primarily as a **runtime sensor**:

- it drives real browser behavior;
- it exposes DOM and accessibility state;
- it can preserve traces, screenshots, console output, network observations, and action history;
- its coding-agent interfaces make the application more legible to agents.

Playwright does not know whether the expected behavior is the correct product requirement. Planner, Generator, and Healer capabilities should therefore operate under an authority boundary. A healer may propose test maintenance, but changing protected business expectations, disabling a required scenario, or rewriting an authoritative oracle must invalidate prior acceptance and require separate authority.

## Related

- [Core invariants and trust model](core-invariants-and-trust-model.md)
- [Gate system, Playwright, and runtime sensors](gate-system-playwright-and-runtime-sensors.md)
- [Acceptance evaluations and metrics](acceptance-evals-and-metrics.md)
