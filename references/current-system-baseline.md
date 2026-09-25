---
id: harness-rig-current-system-baseline
title: Current project baseline
summary: Verified current responsibilities, strengths, overlaps, maturity gaps, and confirmed defects across AIBoarding, TacticSwitch,
  and Adaptive Engineering Harness.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- gustavo-meilus/aiboarding docs/LOOP-ENGINEERING.md, accessed 2026-09-21
- gustavo-meilus/aiboarding CONTRIBUTING.md, accessed 2026-09-21
- gustavo-meilus/tacticswitch docs/GOVERNANCE.md, accessed 2026-09-21
- gustavo-meilus/tacticswitch CONTRIBUTING.md, accessed 2026-09-21
- gustavo-meilus/tacticswitch protocol.md, control-packets.md, and state.schema.json, accessed 2026-09-21
- gustavo-meilus/skill-kit engineering-harness-adaptive SKILL.md and hooks, accessed 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
---
# RigYard source snapshot boundary

`rigyard_current.zip`, supplied 2026-09-24, is now the source-level planning baseline for RigYard.

The snapshot contains current TypeScript source, tests, generated distribution output, current OpenSpec capability specs,
11 archived OpenSpec changes, 8 active OpenSpec changes, retained host/release evidence, and historical handoff material.

Use [RigYard current source and verification baseline](rigyard-current-source-and-verification-baseline.md) for the
current-vs-planned-vs-historical classification. Do not infer Git history or independently rerun verification from the
archive alone: the ZIP contains no `.git/` metadata and this M0 revision records retained verification evidence rather than
claiming that the entire RigYard matrix was rerun in this environment.

# Current responsibilities

## AIBoarding

AIBoarding explicitly owns durable repository context rather than orchestration. Its documented responsibilities include:

- canonical `AGENTS.md`-style onboarding context;
- exact build, test, and run commands;
- drift state in `.aiboarding/state.json`;
- verification instructions;
- compression receipts;
- auditing for stale commands, contradictions, secret-like content, and context bloat.

Its own documentation states that it does not schedule agents, dispatch subagents, or gate merges.

**Harness Rig mapping:** `Context` module.

## Adaptive Engineering Harness

The relevant Skill Kit plugin currently provides:

- scope contracts;
- separate change-risk and reasoning-difficulty classification;
- model/effort guidance;
- KISS/YAGNI discipline;
- deterministic-first verification;
- a verification ladder from static checks through human judgment;
- read-only specialist roles;
- a completion hook that can block on verification failure.

Its skill explicitly warns that when the same agent invents the requirement, expected result, test, implementation, and final judgment, green output can become circular evidence.

**Harness Rig mapping:** `Assurance` module plus gate integration.

## TacticSwitch

TacticSwitch currently provides the strongest formal orchestration protocol:

- deterministic R0-R4 route selection;
- single-writer ownership constraints;
- read-only Scout and Verifier roles;
- fresh verification that does not require a different model vendor;
- fail-closed behavior when mandatory isolated workers are unavailable;
- structured work and result packets;
- exact-state acceptance semantics;
- validation records with before/after state identity;
- explicit treatment of a mutating validator as implementation;
- optional durable state, currently state schema v4.

**Harness Rig mapping:** `Topology` module and seed for shared state/evidence contracts.

# Proposal boundary

Two user-supplied OpenSpec bundles contain proposed TacticSwitch evolution:

- `tacticswitch-openspec-proposals-v3.zip`: earlier, narrower proposal set.
- `tacticswitch-openspec-loop-proposals.zip`: later, richer runtime-execution, recurrence, hosted-gate, and native-assurance proposal set.

Neither archive is current implementation unless independently applied and verified in the authoritative repository.

Use [TacticSwitch loop and runtime-policy proposals disposition](tacticswitch-loop-proposals-disposition.md) for the current Harness Rig disposition.

# Existing overlap

Adaptive Engineering Harness and TacticSwitch both make decisions related to independent review or additional contexts.

The recommended split is:

- Assurance decides **what must be demonstrated**.
- Topology decides **the minimum execution/context arrangement that can satisfy that requirement**.

This removes competing routing authorities.

# Confirmed P0 defect: committed-in-session changes

The current Adaptive Engineering Harness `dirty_paths()` returns tracked paths that differ from the **current `HEAD`** plus untracked non-ignored paths. `workspace_snapshot()` hashes only those dirty paths.

The stop hook compares the current snapshot with its saved baseline. If an agent edits code and commits it during the session, the worktree can become clean again relative to the new `HEAD`. Both snapshots can therefore be empty even though the repository commit changed.

Consequence: the stop-time verifier can be skipped after a committed code change.

Required correction: canonical state identity must include at least the relevant repository identity and `HEAD`, not only dirty worktree paths.

# Confirmed P0 defect: verifier mutation

The current stop hook captures the workspace snapshot before running `engineering_verify.py`. On a zero exit status, it stores that pre-verification snapshot as the verified baseline without re-snapshotting after verification.

Consequence: a verifier that changes relevant files can return success while leaving a state different from the state it evaluated.

TacticSwitch already specifies the correct semantic rule: validation that mutates relevant output becomes implementation, requires a refreshed exact state identity, and must be validated again before fresh verification.

# Maturity boundary

The three projects do not currently form one proven cross-host product. Host adapters and installation behaviors differ, and compatibility claims require clean-process evidence rather than static package inspection.

The unified product should expose capability evidence, not a single "supported" Boolean.

## Related

- [Contracts, state, and evidence](contracts-state-and-evidence.md)
- [Target architecture](target-architecture.md)
- [Host adapters and capability negotiation](host-adapters-and-capabilities.md)
