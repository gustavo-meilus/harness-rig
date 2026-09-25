---
id: harness-rig-m9-gate-platform-playwright-architecture-mutation
title: M9 gate platform, Playwright, architecture, and mutation verification
summary: Implemented r8.9 minimum common gate semantics, AST architecture fitness checks, strict Playwright required-scenario evidence, and bounded mutation sensitivity verification.
version: planning-baseline-2026-09-25-r8.9
updated: '2026-09-25'
provenance:
- Harness Rig M9 implementation and adversarial verification, 2026-09-25
- Playwright Test 1.63.0 release/package baseline and official CLI/reporter/retry documentation, rechecked 2026-09-25
- 'Local runtime observation: Node 22.16.0, npm 10.9.2, Playwright browser CLI 1.57.0, no local @playwright/test package, 2026-09-25'
- User-supplied RigYard source snapshot and retained harness-mutation-verification proposal disposition
- Skill Kit More With Less v1.0.2 minimum-sufficient verification doctrine
---
# Result

M9 completed with **PASS** at revision `r8.9` for the repository-local verification platform boundary.

It adds the minimum shared vocabulary needed by distinct gates while keeping provider detail native:

```text
GateClaim / GateOutcome        Experimental common semantics
ArchitectureGate              AST import-boundary provider
PlaywrightGate                external Playwright Test JSON/runtime provider
MutationGate                  bounded development-only detector-sensitivity provider
EvidenceReceipt               still Experimental shared envelope
```

No generic gate registry, browser farm, mutation framework, telemetry service, plugin SDK, or new orchestration layer was added.

# Minimal common gate semantics

`GateClaim` carries only:

```text
schema
claim_id
kind
gate_id
gate_contract_version
required
```

`GateOutcome` carries only:

```text
schema
outcome = PASS | FAIL | BLOCKED | NOT_RUN | MUTATED
reasons
attempt_count
flaky
```

Provider-specific reports, traces, attachments and diagnostics remain provider-native artifacts. The common vocabulary is Experimental because M9 proves multiple provider consumers but does not require Stable promotion of the full evidence envelope.

# Architecture gate

`harness_rig.architecture_gate` evaluates `governance/architecture-policy.json` with Python AST import inspection.

The current policy prevents Stable/core trust modules from importing adapter/development-gate modules such as OpenSpec, Playwright, repository-CI, host, architecture-gate or mutation-gate implementations. A policy rule whose source glob matches no file returns `BLOCKED`; it cannot silently PASS. Syntax/read failures also fail closed. A deliberate forbidden import fixture is detected as `FAIL`.

The provider captures exact state before and after evaluation and emits the existing Experimental `EvidenceReceipt`. A verifier mutation therefore becomes `MUTATED` rather than certifying the changed state.

# Playwright provider

The M9 compatibility target was rechecked against current Playwright Test `1.63.0` public behavior. Current Playwright exposes JSON reporting, retries/flaky classification, `--forbid-only`, `--fail-on-flaky-tests`, and the opt-in `--pass-with-no-tests` flag.

Harness Rig does not infer acceptance from Playwright exit zero alone. `PlaywrightGate` requires an explicit non-empty set of scenarios. Every required scenario is matched by test title and optional project identity, then classified from JSON test results:

```text
MISSING
SKIPPED
NOT_RUN
FAIL
FLAKY
PASS
```

`MISSING`, `SKIPPED`, `NOT_RUN`, or `FAIL` on a required scenario cannot become PASS. Flaky retries remain visible as attempt statuses and retry indexes; strict mode, which is the default, rejects flaky required scenarios. `--pass-with-no-tests` is explicitly forbidden by the provider.

Runtime-sensitive web evidence is kept in a small provider-native sidecar with:

```text
worktree_root
data_namespace
shared_data
console_errors
unexpected_network
```

Wrong worktree, shared data, namespace mismatch, console errors, unexpected network, or missing required runtime observation make the gate fail. Playwright JSON reports, traces/attachments, stdout/stderr digests and runtime sidecars are referenced as native artifacts rather than flattened into the common gate contract.

M9 uses `subprocess` with `shell=False`, an explicit timeout, resolved executable identity and an isolated report path.

# Native-qualification limit

The execution environment did **not** contain a local Node `@playwright/test` installation. It observed:

```text
Node                22.16.0
npm                 10.9.2
playwright CLI      1.57.0 (browser/Python installation)
@playwright/test    unavailable locally
```

Therefore M9 does not claim a native current Playwright Test project run. Provider/protocol behavior is executable against deterministic current-shape JSON/subprocess fixtures, while the current public Playwright 1.63.0 machine behavior is retained as external compatibility evidence. Live project qualification remains future field evidence, not an invented PASS.

# Mutation development gate

The supplied RigYard source snapshot records harness-mutation-verification as planned/unimplemented source-side. M9 does not rewrite that history into an implemented RigYard feature. Harness Rig adopts only the bounded detector-sensitivity principle.

`MutationCase` maps exactly:

```text
invariant_id -> mutant_id -> detector_id
```

The gate requires a green baseline detector, copies the repository into a temporary mutant workspace, performs one exact text substitution, and executes the same detector with `shell=False` and a timeout.

```text
detector red on mutant   -> KILLED  -> gate PASS
detector green on mutant -> SURVIVED -> gate FAIL
baseline red/blocked      -> gate BLOCKED; mutant not admitted as evidence
```

Protected-oracle cases also compute Direct Authority before/after the mutation. Weakening a protected healer/oracle changes authority identity even when a deliberately blind detector stays green; the old authority is therefore reopened instead of being silently reused.

The retained mutation map includes both a red/green sensitivity example and a deliberate detector-gap example, so M9 proves that mutation verification can reveal missing detector sensitivity rather than merely count mutants.

# M9 verification

The M9 adversarial suite proves:

- M9-V01 required Playwright skip/no-test cannot PASS;
- M9-V02 retry/flaky state remains explicit;
- M9-V03 protected healer-oracle mutation changes authority identity;
- M9-V04 wrong worktree, shared data, console errors and unexpected network fail;
- M9-V05 a deliberate architecture violation is detected;
- M9-V06 KILLED and SURVIVED mutation paths distinguish detector sensitivity from a detector gap.

Prior milestone suites are rerun in separate clean Python processes for M9 regression evidence. This avoids interpreting cross-suite process state as part of a gate contract and keeps each retained result independently attributable.

# Deferred boundary

M10 owns product CLI/versioned JSON/config/cancellation/migration/release-provenance finalization. M9 does not advance those surfaces.
