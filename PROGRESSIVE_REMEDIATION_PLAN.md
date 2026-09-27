# Harness Rig Progressive Remediation Plan — r8

**Status:** execution plan  
**Prepared:** 2026-09-24  
**Input baseline:** Harness Rig r7 knowledge-base package, independent adversarial review, `rigyard_current.zip`, current Skill Kit More With Less and LLM knowledge-base-maintainer doctrine, current OpenSpec/GitHub/Playwright verification baseline.

---

## LLM-Ready Execution Index

> **Use this section first in a fresh context.** It is the execution/navigation layer for the plan below. The detailed milestone text remains authoritative.

### Navigation protocol

Stable identifiers:

```text
M#        milestone
M#-T##    execution task
M#-V##    verification task
```

Recommended task-state markers:

```text
[ ] TODO
[~] DOING
[!] BLOCKED
[x] DONE
```

Execution rule:

```text
read milestone scope
→ execute only its M#-T## tasks
→ run all M#-V## verification tasks
→ record PASS / PASS_WITH_GAPS / REWORK / BLOCKED
→ only then advance to the next milestone
```

### LLM resume / handoff record

Update this block whenever execution stops so a fresh context can resume without reconstructing progress:

```yaml
plan: harness-rig-progressive-remediation-r8
current_milestone: M12
current_revision: r8.12
milestone_result: BLOCKED
last_completed_task: M12-T09 / M12-T11 / M12-V02 / M12-V03
next_task: Commit final M12 artifacts, resolve CI obligations, and obtain accepted hosted ci / required verdict for that exact revision
blocking_issue: Hosted final-revision CI verdict and explicit authorization for the independent architecture review payload
verification_pending:
  - M12-T01 canonical python scripts/check.py after final evidence and Context projection
  - M12-T10 / M12-V01 independent architecture review
notes: >
  M0 through M10 completed with PASS. M10 finalized the compact product CLI and versioned machine envelope,
  fail-closed configuration precedence, verifier timeout/cancellation cleanup, atomic r8.9-to-r8.10 migration state
  with explicit rollback, and deterministic release-record/checksum behavior. Runtime/schema migration can complete while
  source-history qualification remains PENDING_M11; M10 does not fabricate the deferred real source history maps.
  Release eligibility is BLOCKED when no accepted repository verdict is
  supplied. The exact source-native pins, bundles, and one-parent import commit
  are verified; the raw TacticSwitch manifest failure and separate passing
  adapter are retained. The authorized read-only Codex CLI assessment and V04
  review are recorded. Codex Desktop and CLI field pilots now cover the real
  adapter/check path, synthetic implementation and fresh verification, and
  observed Windows workspace boundaries in elevated and unelevated modes.
  M11 passed with recorded limits. M12 targeted suites, Context audit, native
  local-subprocess evidence, release fail-closed smoke, and feature-retirement
  review pass. M12 remains blocked because current changes are uncommitted, no
  hosted ci / required verdict exists for the final source revision, and no
  provider-payload authorization was given for the independent architecture
  review. Claude native qualification remains out of scope and is not a gate.
```

### Milestone quick index

| Milestone | Revision | Purpose | Jump |
|---|---|---|---|
| **M0** | `r8.0` | Corpus repair and source baseline | [Go](#milestone-m0-corpus-repair-and-source-baseline) |
| **M1** | `r8.1` | Trust protocol ADRs, before stable kernel APIs | [Go](#milestone-m1-trust-protocol-adrs-before-stable-kernel-apis) |
| **M2** | `r8.2` | CHANGELOG-backed source consolidation foundation | [Go](#milestone-m2-changelog-backed-source-consolidation-foundation) |
| **M3** | `r8.3` | Thin complete experimental vertical slice | [Go](#milestone-m3-thin-complete-experimental-vertical-slice) |
| **M4** | `r8.4` | Core promotion and module-boundary convergence | [Go](#milestone-m4-core-promotion-and-module-boundary-convergence) |
| **M5** | `r8.5` | Context convergence and canonical knowledge lifecycle | [Go](#milestone-m5-context-convergence-and-canonical-knowledge-lifecycle) |
| **M6** | `r8.6` | OpenSpec as the first-class external SpecEngine | [Go](#milestone-m6-openspec-as-the-first-class-external-specengine) |
| **M7** | `r8.7` | Trusted repository enforcement | [Go](#milestone-m7-trusted-repository-enforcement) |
| **M8** | `r8.8` | Host capability and topology qualification | [Go](#milestone-m8-host-capability-and-topology-qualification) |
| **M9** | `r8.9` | Gate platform, Playwright, architecture, and mutation verification | [Go](#milestone-m9-gate-platform-playwright-architecture-and-mutation-verification) |
| **M10** | `r8.10` | Product CLI, migration completion, and release provenance | [Go](#milestone-m10-product-cli-migration-completion-and-release-provenance) |
| **M11** | `r8.11` | RigYard disposition, Git-history qualification, and field hardening | [Go](#milestone-m11-rigyard-disposition-git-history-qualification-and-field-hardening) |
| **M12** | `r8.12` | 1.0 qualification and final simplification | [Go](#milestone-m12-10-qualification-and-final-simplification) |

### Master task checklist

#### M0 — Corpus repair and source baseline

**Execution (`r8.0`):**

- [x] **M0-T01** — Repair invalid YAML front matter and define the canonical metadata schema.
- [x] **M0-T02** — Generate `manifest.jsonl` deterministically from canonical references.
- [x] **M0-T03** — Refresh More-With-Less, Skill Kit KB, OpenSpec, and RigYard source provenance.
- [x] **M0-T04** — Replace stale RigYard-access assumptions with current source/evidence status.
- [x] **M0-T05** — Classify stale RigYard handoff/state documents as historical evidence.

**Verification:**

- [x] **M0-V01** — Full canonical YAML parse succeeds.
- [x] **M0-V02** — IDs, links, `llms.txt`, and manifest integrity checks pass.
- [x] **M0-V03** — Manifest regeneration is byte-identical.
- [x] **M0-V04** — All active RigYard changes and evidence maturity states are enumerated.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M1`

#### M1 — Trust protocol ADRs, before stable kernel APIs

**Execution (`r8.1`):**

- [x] **M1-T01** — Write and accept the `StateIdentity` ADR.
- [x] **M1-T02** — Write and accept the bounded `AuthorizationGrant` ADR.
- [x] **M1-T03** — Write and accept the strengthened `EvidenceReceipt` ADR.
- [x] **M1-T04** — Write and accept the action-qualified `AcceptanceVerdict` ADR.
- [x] **M1-T05** — Create the canonical security/trust boundary page.
- [x] **M1-T06** — Create known-bad fixtures for all P0 trust invariants.

**Verification:**

- [x] **M1-V01** — State/revision/content edge cases have executable fixtures.
- [x] **M1-V02** — Authorization expiry/delegation/state-binding fixtures fail closed.
- [x] **M1-V03** — Receipt replay/forgery/version/artifact-integrity fixtures fail closed.
- [x] **M1-V04** — Path traversal, symlink escape, and executable spoofing fixtures fail closed.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M2`

#### M2 — CHANGELOG-backed source consolidation foundation

**Execution (`r8.2`):**

- [x] **M2-T01** — Record the AIBoarding source baseline, target owner, and disposition in `CHANGELOG.md`.
- [x] **M2-T02** — Record the TacticSwitch source baseline, target owner, and disposition in `CHANGELOG.md`.
- [x] **M2-T03** — Record the Skill Kit KB maintainer source baseline, target owner, and disposition in `CHANGELOG.md`.
- [x] **M2-T04** — Record the Adaptive Engineering Harness source baseline, target owner, and disposition in `CHANGELOG.md`.
- [x] **M2-T05** — Record the migration-surface inventory and source→Harness Rig convergence decisions.
- [x] **M2-T06** — Classify each source capability as KEEP / ADAPT / REPLACE / DELETE_AFTER_MIGRATION / HISTORICAL_ONLY.

**Verification:**

- [x] **M2-V01** — `CHANGELOG.md` contains all mandatory source/capability baselines with target ownership and disposition.
- [x] **M2-V02** — Source-specific verification/evidence is recorded where known; unavailable/unknown evidence is not invented.
- [x] **M2-V03** — `CHANGELOG.md` explicitly separates M2 semantic consolidation from deferred M11 Git-history qualification.
- [x] **M2-V04** — Licenses, state, hooks, install/update, generated, schema, test, CI, OpenSpec, and agent/role surfaces are inventoried.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M3`

#### M3 — Thin complete experimental vertical slice

**Execution (`r8.3`):**

- [x] **M3-T01** — Implement Direct Authority.
- [x] **M3-T02** — Implement the smallest Assurance path.
- [x] **M3-T03** — Implement direct/single-agent Topology.
- [x] **M3-T04** — Implement one command/test gate.
- [x] **M3-T05** — Issue an experimental `EvidenceReceipt`.
- [x] **M3-T06** — Issue an experimental action-qualified `AcceptanceVerdict`.

**Verification:**

- [x] **M3-V01** — All M1 P0 trust fixtures run through the M3 implementation path; all M1-F01…F16 also pass.
- [x] **M3-V02** — Skipped/not-run gates cannot become PASS.
- [x] **M3-V03** — Authority/state changes invalidate applicable receipts.
- [x] **M3-V04** — Wrong-run or replayed receipts are rejected.
- [x] **M3-V05** — Missing authorization produces BLOCKED.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M4`

#### M4 — Core promotion and module-boundary convergence

**Execution (`r8.4`):**

- [x] **M4-T01** — Evaluate promotion of `AuthorityRef`.
- [x] **M4-T02** — Evaluate promotion of `AuthorizationGrant`.
- [x] **M4-T03** — Evaluate promotion of `StateIdentity`.
- [x] **M4-T04** — Evaluate promotion of `EvidenceReceipt`.
- [x] **M4-T05** — Evaluate promotion of `AcceptanceVerdict`.
- [x] **M4-T06** — Keep `AssurancePlan`, `ExecutionPlan`, Context internals, RuntimeResolution, and recurrence state module/adapter-owned unless proven cross-cutting.
- [x] **M4-T07** — Remove `ContextManifest` from initial stable core unless a second independent consumer proves need.

**Verification:**

- [x] **M4-V01** — Each promoted core contract has two concrete consumers or one unavoidable cross-cutting invariant.
- [x] **M4-V02** — No provider-specific escape fields are needed.
- [x] **M4-V03** — Assurance cannot select workers.
- [x] **M4-V04** — Topology cannot waive evidence or broaden authorization.
- [x] **M4-V05** — Version/migration/failure semantics are explicit for promoted contracts.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M5`

#### M5 — Context convergence and canonical knowledge lifecycle

**Execution (`r8.5`):**

- [x] **M5-T01** — Finalize canonical-KB vs Context-lifecycle ownership.
- [x] **M5-T02** — Define stable-ID rename/move/split/merge/retirement rules.
- [x] **M5-T03** — Define provenance and source-freshness conventions.
- [x] **M5-T04** — Implement source reconciliation and conflict/gap preservation.
- [x] **M5-T05** — Implement deterministic manifest generation and whole-collection audit.
- [x] **M5-T06** — Keep root `AGENTS.md` as rules/navigation, not duplicate canonical knowledge.

**Verification:**

- [x] **M5-V01** — Rename/split/merge/retirement fixtures pass.
- [x] **M5-V02** — External-source freshness changes are detected correctly.
- [x] **M5-V03** — Conflicts remain explicit and unsupported claims are rejected.
- [x] **M5-V04** — Canonical KB changes and AGENTS projection drift have exactly one owner each.
- [x] **M5-V05** — No vector/RAG subsystem is introduced.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M6`

#### M6 — OpenSpec as the first-class external SpecEngine

**Execution (`r8.6`):**

- [x] **M6-T01** — Implement/refine DirectAuthorityProvider and OpenSpecAdapter.
- [x] **M6-T02** — Refine the experimental `SpecEngine` interface from real consumers.
- [x] **M6-T03** — Define/test the default OpenSpec authority fingerprint profile.
- [x] **M6-T04** — Implement authority-bearing referenced-spec handling.
- [x] **M6-T05** — Implement effective OpenSpec health/config/rules checks.
- [x] **M6-T06** — Expose guarded `harness-rig spec archive` with transition evidence.

**Verification:**

- [x] **M6-V01** — Base Harness Rig works when OpenSpec is absent.
- [x] **M6-V02** — OpenSpec-required workflows fail closed when OpenSpec is unavailable.
- [x] **M6-V03** — Authority fingerprint distinguishes tasks-only vs behavior-bearing changes.
- [x] **M6-V04** — Malformed config/rules and unresolved authority references fail appropriately.
- [x] **M6-V05** — Archive partial/postcondition failures return BLOCKED.
- [x] **M6-V06** — Post-archive acceptance is reevaluated against final authority/state.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M7`

#### M7 — Trusted repository enforcement

**Execution (`r8.7`):**

- [x] **M7-T01** — Emit a CI obligation artifact for the evaluated revision.
- [x] **M7-T02** — Make `ci / required` execute even after prerequisite failures.
- [x] **M7-T03** — Validate every mandatory obligation/result explicitly.
- [x] **M7-T04** — Support merge queues via `merge_group` when enabled.
- [x] **M7-T05** — Define untrusted fork and privileged workflow boundaries.
- [x] **M7-T06** — Protect CI/resolver/policy/oracle paths as governance-sensitive surfaces.

**Verification:**

- [x] **M7-V01** — Prerequisite-failure meta-test passes.
- [x] **M7-V02** — Skipped mandatory job is detected.
- [x] **M7-V03** — Merge-queue scenario is covered.
- [x] **M7-V04** — Fork PR cannot access privileged secrets/actions.
- [x] **M7-V05** — Self-modifying CI/resolver and wrong-SHA/wrong-producer cases fail closed.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M8`

#### M8 — Host capability and topology qualification

**Execution (`r8.8`):**

- [x] **M8-T01** — Select and qualify the first Stable host candidate.
- [x] **M8-T02** — Reuse RigYard's implemented/local/native-qualified/Stable maturity distinction.
- [x] **M8-T03** — Refine `CapabilitySet` from observed native behavior.
- [x] **M8-T04** — Define fresh-verifier semantics as a real context/permission boundary.
- [x] **M8-T05** — Reconcile RigYard isolated-writer capability as optional and evidence-gated.

**Verification:**

- [x] **M8-V01** — Clean-process discovery and launch pass.
- [x] **M8-V02** — Requested/resolved/observed facts are captured.
- [x] **M8-V03** — Read-only and isolation requirements are actually enforced or BLOCKED.
- [x] **M8-V04** — Crash/reconciliation and evidence attribution pass.
- [x] **M8-V05** — Isolated-writer Stable claim requires retained formal native evidence.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M9`

#### M9 — Gate platform, Playwright, architecture, and mutation verification

**Execution (`r8.9`):**

- [x] **M9-T01** — Define minimal common gate claim/outcome semantics.
- [x] **M9-T02** — Implement/refine the architecture gate provider.
- [x] **M9-T03** — Implement/refine the Playwright provider with explicit required scenarios.
- [x] **M9-T04** — Reconcile RigYard harness-mutation-verification as a bounded development gate.
- [x] **M9-T05** — Map invariant → mutant → detector for mutation fixtures.

**Verification:**

- [x] **M9-V01** — Required Playwright skip/no-test cannot PASS.
- [x] **M9-V02** — Flaky retries remain visible.
- [x] **M9-V03** — Healer oracle mutation reopens authority.
- [x] **M9-V04** — Wrong-worktree/shared-data/console-network failure fixtures behave correctly.
- [x] **M9-V05** — A deliberate architecture violation is detected.
- [x] **M9-V06** — At least one mutation red/green detector-gap example is proven.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M10`

#### M10 — Product CLI, migration completion, and release provenance

**Execution (`r8.10`):**

- [x] **M10-T01** — Finalize compact CLI including guarded `spec archive`.
- [x] **M10-T02** — Define versioned JSON and exit-code semantics.
- [x] **M10-T03** — Define config precedence and noninteractive behavior.
- [x] **M10-T04** — Define cancellation/timeout cleanup.
- [x] **M10-T05** — Finalize migration completion/rollback criteria.
- [x] **M10-T06** — Finalize minimum release provenance/checksum/attestation behavior.

**Verification:**

- [x] **M10-V01** — Noninteractive BLOCKED semantics pass.
- [x] **M10-V02** — Malformed/global-weakened config cases fail safely.
- [x] **M10-V03** — Cancellation/timeout cleanup is verified.
- [x] **M10-V04** — Interrupted migration and mixed old/new state fixtures pass.
- [x] **M10-V05** — Rollback/downgrade behavior is tested/documented.
- [x] **M10-V06** — Build→artifact provenance is consistent.

**Milestone result:** `PASS`  
**Allowed next milestone:** `M11`

#### M11 — RigYard disposition, Git-history qualification, and field hardening

**Execution (`r8.11`):**

- [x] **M11-T01** — Disposition v0.3 isolated writers.
- [x] **M11-T02** — Disposition harness mutation verification.
- [x] **M11-T03** — Disposition v0.4 approved revision/traceability requirements.
- [x] **M11-T04** — Disposition v0.5 static composition.
- [x] **M11-T05** — Disposition v0.6 richer topology families.
- [x] **M11-T06** — Disposition v0.7 distributed execution.
- [x] **M11-T07** — Disposition v0.8 observability/effects.
- [x] **M11-T08** — Claude native qualification is out of scope for now per
  user direction; not an M11 acceptance gate.
- [x] **M11-T09** — Complete representative Codex Desktop/CLI implementation
  and native capability qualification with recorded limits. Evidence:
  `verification/m11-codex-field-pilot.json`.
- [x] **M11-T10** — Validate object-complete AIBoarding, TacticSwitch, and Skill Kit bundles and refs.
- [x] **M11-T11** — Retain full source histories as submodules at audited pins; do not rewrite upstream history.
- [x] **M11-T12** — Reconcile source pins, refs, bundles, and `CHANGELOG.md`; see `verification/m11-changelog-reconciliation.json`.
- [x] **M11-T13** — Retain raw legacy failures and separate passing adapter results; see `verification/m11-import-only-status.json` and `verification/m11-legacy-check-results.json`.
- [x] **M11-T14** — Inventory source refs, surfaces, signatures, and tag objects; see `verification/m11-source-repository-inventory/` and `verification/m11-object-fidelity-audit.json`.

**Verification:**

- [x] **M11-V01** — Every active RigYard proposal has exactly one Harness Rig disposition.
- [x] **M11-V02** — Deferred features have explicit evidence triggers.
- [x] **M11-V03** — Field-pilot evidence records authorized read-only and
  implementation pilots, outcomes, costs, and limits.
- [x] **M11-V04** — In-scope proposals with no distinct value are deferred or
  kept optional. Bounded mutation verification remains for its distinct
  detector-gap evidence. See `verification/m11-rigyard-dispositions.json`.
- [x] **M11-V05** — The one-parent import commit contains only the approved gitlinks and `.gitmodules`; see `verification/m11-import-only-status.json`.
- [x] **M11-V06** — Retain legacy failures and passing import-only evidence;
  all M11 acceptance criteria now have evidence.
- [x] **M11-V07** — `CHANGELOG.md` reconciles with actual source history; material discrepancies are resolved or explicitly recorded. Evidence: `verification/m11-changelog-reconciliation.json`.
- [x] **M11-V08** — Exact upstream signature-bearing commits and tag objects are retained and matched to bundles; local trust revalidation limits are recorded.

**Milestone result:** `PASS`
**Allowed next milestone:** `M12`; M11 gates pass with recorded limitations.

Dispositions: `verification/m11-rigyard-dispositions.json` (8/8 active
proposals). Claude native qualification is out of scope. V04 passed. Codex
field evidence and limitations: `verification/m11-codex-field-pilot.json`;
overall gate: `verification/m11-history-qualification-status.json`.

#### M12 — 1.0 qualification and final simplification

**Execution (`r8.12`):**

- [x] **M12-T01** — Canonical suite passed: 139 tests across 9 modules.
- [x] **M12-T02** — Context audit, unchanged manifest, fresh projection.
- [x] **M12-T03** — All P0 adversarial trust fixtures.
- [x] **M12-T04** — OpenSpec compatibility fixtures and strict validation.
- [!] **M12-T05** — M7 CI suite passed; bind obligations to final source SHA and obtain hosted verdict.
- [x] **M12-T06** — Retain native `local-subprocess` evidence; Codex adapter remains unqualified.
- [x] **M12-T07** — Gate-provider adversarial suite.
- [x] **M12-T08** — Migration upgrade/rollback fixtures.
- [x] **M12-T09** — Missing-verdict release smoke rejected the candidate as expected.
- [!] **M12-T10** — Fresh-context review awaits explicit authorization for provider payload.
- [x] **M12-T11** — Final feature-retirement review recorded.

**Verification:**

- [!] **M12-V01** — Blocked pending M12-T10 independent architecture review.
- [x] **M12-V02** — Supported trust invariant holds within observed capability limits.
- [x] **M12-V03** — Disposition evidence admits no speculative mechanism; M12 adds no product code.

**Milestone result:** `BLOCKED` — see `verification/m12-verification-record.json`.
**Allowed next milestone:** `NONE / 1.0 qualification complete`

---

## 1. Purpose

This plan converts the r7 remediation analysis into a sequence of **progressive, independently verifiable revisions**.

The plan is deliberately not a one-shot rewrite.

Each milestone:

1. changes only one coherent trust or product boundary;
2. produces a reviewable intermediate knowledge-base/project state;
3. runs deterministic and adversarial verification appropriate to that boundary;
4. records unresolved evidence gaps explicitly;
5. blocks the following milestone when its exit criteria are not satisfied.

The goal is not to implement every reviewer suggestion or every RigYard proposal.

The goal is to establish the **smallest verified Harness Rig architecture** that can safely bind:

```text
agreed intent
+ bounded authorization
+ canonical project knowledge
+ minimum-sufficient execution
+ exact source/runtime evidence
+ fail-closed acceptance
```

The current Skill Kit `more-with-less` doctrine remains the feature-admission rule:

```text
understand before simplifying
reuse before adding
deterministic before inferential
one agent before multiple agents
existing project/tool mechanism before new infrastructure
preserve correctness/security/authorization/integrity
every significant harness mechanism needs evidence and a retirement condition
```

---

# 2. Source and evidence policy

The remediation must never treat the adversarial reviewer report as automatically correct.

For every proposed change:

```text
review finding
    ↓
reproduce against the current Harness Rig package
    ↓
inspect current primary implementation/source when applicable
    ↓
compare against RigYard current implementation and retained evidence
    ↓
apply More-With-Less admission test
    ↓
ACCEPT / RESHAPE / DEFER / REJECT
    ↓
add only the minimum change
    ↓
verify with a known-bad or representative fixture
```

## Evidence classes

Every revised page must distinguish:

- **verified current implementation**
- **retained formal evidence**
- **local/non-formal verification**
- **planned OpenSpec change**
- **accepted Harness Rig target design**
- **architectural hypothesis**
- **deferred/earned capability**
- **unresolved evidence gap**

Do not promote a RigYard proposal to an implemented Harness Rig feature merely because the proposal exists.

Do not promote a retained artifact to independently rerun evidence unless it was actually rerun.

---

# 3. Current source baseline

## Harness Rig r7

Use r7 as the editable starting knowledge corpus.

Known immediate issues:

- three canonical pages have YAML front matter that fails standard YAML parsing;
- `manifest.jsonl` is synchronized but should become deterministically generated;
- More-With-Less provenance uses an obsolete path in several pages;
- OpenSpec current-version provenance is stale;
- stable-core candidates are prematurely generalized;
- Context lifecycle/KB freshness ownership overlaps;
- migration ordering is internally inconsistent.

## More With Less

Canonical source for this revision:

```text
skill-kit/plugins/more-with-less/skills/more-with-less/
```

Treat this as the primary simplification and feature-admission doctrine.

## Skill Kit LLM knowledge-base maintainer

Preserve as the basis for first-class Harness Rig Context knowledge:

```text
canonical Markdown
stable logical IDs
provenance
search-before-create
reconciliation
llms.txt
manifest.jsonl
whole-collection integrity
```

No vector/embedding/RAG subsystem belongs in the expected project.

## RigYard current source snapshot

`rigyard_current.zip` is now the source-level planning baseline for RigYard implementation and unfinished proposals.

Important current evidence maturity:

| Surface | Current status |
|---|---|
| v0.1 Codex/Linux local-filesystem path | retained formal qualification/release evidence exists |
| v0.1.1 adapter-neutral infrastructure | implemented |
| v0.3 isolated parallel writers | implementation/tasks nearly complete; formal native isolated-writer evidence still missing |
| Claude adapter | experimental/unqualified; fail-closed evidence gap retained |
| Copilot adapter | experimental/unqualified; fail-closed evidence gap retained |
| mutation verification | planned, unimplemented |
| v0.4 approved pipeline evolution / traceability | planned |
| v0.5 static composition | planned |
| v0.6 richer topology | planned |
| v0.7 distributed execution | planned |
| v0.8 observability/effects | planned |
| Claude native qualification | out of scope for now; not an M11 or M12 gate |

RigYard also already implements useful evidence concepts that must be reused before inventing generalized replacements, including core acceptance evidence and durable worker-result evidence.

## Current OpenSpec baseline

Use a dated compatibility baseline rather than a timeless "latest" statement.

For this revision, the planning baseline is OpenSpec **v1.13.2**, rechecked 2026-09-24.

Historical RigYard artifacts that used older OpenSpec versions remain historical evidence and must not be rewritten.

---

# 4. Progressive revision policy

Each milestone produces a package revision:

```text
r8.0
r8.1
r8.2
...
```

A milestone is not considered complete because pages were edited.

It is complete only after its verification section passes.

## Verification result vocabulary

Use:

```text
PASS
  milestone claims verified

PASS_WITH_GAPS
  verified scope passes but a documented external evidence gap remains;
  later milestone may continue only when that gap is explicitly non-blocking

REWORK
  milestone artifacts are internally inconsistent or fail an adversarial fixture

BLOCKED
  required source/tool/native capability unavailable and the milestone cannot
  truthfully claim its intended result
```

No `REWORK` or `BLOCKED` milestone may be used as the foundation for a stable downstream contract.

---

# 5. Milestone M0 — Corpus repair and source baseline

### M0 task navigation

**Target revision:** `r8.0`

**Execution tasks:**

- [x] **M0-T01** — Repair invalid YAML front matter and define the canonical metadata schema.
- [x] **M0-T02** — Generate `manifest.jsonl` deterministically from canonical references.
- [x] **M0-T03** — Refresh More-With-Less, Skill Kit KB, OpenSpec, and RigYard source provenance.
- [x] **M0-T04** — Replace stale RigYard-access assumptions with current source/evidence status.
- [x] **M0-T05** — Classify stale RigYard handoff/state documents as historical evidence.

**Verification tasks:**

- [x] **M0-V01** — Full canonical YAML parse succeeds.
- [x] **M0-V02** — IDs, links, `llms.txt`, and manifest integrity checks pass.
- [x] **M0-V03** — Manifest regeneration is byte-identical.
- [x] **M0-V04** — All active RigYard changes and evidence maturity states are enumerated.

**Result:** `PASS`

### M0 execution record — 2026-09-24

**Result:** `PASS`

**Produced package:** `harness-rig-knowledge-base-2026-09-24-r8.0.zip`

**Verified:**

- production YAML parse across the complete canonical collection;
- required metadata and unique IDs;
- relative links and `llms.txt` targets;
- exhaustive deterministic manifest coverage;
- byte-identical second manifest generation;
- Skill Kit More-With-Less v1.0.2 canonical source/path;
- Skill Kit KB maintainer v1.1.0 source/version;
- OpenSpec v1.13.2 current planning release baseline;
- RigYard 0.1.1 source snapshot inventory;
- exactly 8 active and 11 archived RigYard OpenSpec changes;
- active-change task counts;
- retained Codex formal evidence classification;
- Claude/Copilot experimental-unqualified classification;
- explicit absence of formal isolated-writer host evidence.

**Evidence limits:** RigYard's complete test/native-host matrix was not independently rerun in M0, and the supplied ZIP contains no `.git/`.

**Next permitted milestone:** `M1`

> Do not advance from this milestone until every required verification task above is completed and the milestone result is recorded.

**Progressive revision:** `r8.0`  
**Purpose:** make the planning corpus itself trustworthy before using it to define trust protocols.

## Scope

Repair the r7 canonical knowledge collection.

### Required changes

1. Fix all invalid YAML front matter.
2. Define one canonical front-matter schema.
3. Parse front matter using a standard YAML parser.
4. Generate `manifest.jsonl` deterministically from canonical references.
5. Keep `llms.txt` curated rather than requiring exhaustiveness.
6. Replace obsolete More-With-Less provenance with the canonical:
   `plugins/more-with-less/skills/more-with-less`.
7. Record the current More-With-Less plugin version and checked date.
8. Refresh OpenSpec planning provenance to v1.13.2 / 2026-09-24.
9. Separate:
   - page `updated`;
   - external source version/commit;
   - external source checked date.
10. Replace the old "RigYard inaccessible" assumption with the real source snapshot status.
11. Add a RigYard reconciliation index covering:
    - current code;
    - current tests;
    - retained evidence;
    - archived changes;
    - active changes;
    - stale historical handoff documents.
12. Mark stale `INITIAL_STATE.md`, `handoff.md`, and relevant `GRILL_REPORT.md` claims as historical transition material rather than current status.

## Do not change yet

Do not redesign kernel contracts in M0.

Do not rewrite the roadmap beyond correcting demonstrably false/current-source statements.

## Verification

### KB structural verification

- parse every canonical front matter block with the production parser;
- required fields present;
- stable IDs unique;
- dates valid;
- all relative links resolve;
- all `llms.txt` links resolve;
- exactly one manifest row per canonical page;
- no manifest row for removed pages;
- manifest regeneration is byte-identical on a second run.

### Source verification

- More-With-Less source path exists and version is recorded;
- KB-maintainer source/version recorded;
- OpenSpec baseline is v1.13.2 with checked date;
- every active RigYard OpenSpec change is enumerated exactly once;
- RigYard current verification maturity table matches retained artifacts;
- historical documents are not presented as current state.

### Exit criteria

`PASS` only when the corpus can verify itself using the same structural rules Harness Rig intends to provide.

---

# 6. Milestone M1 — Trust protocol ADRs, before stable kernel APIs

### M1 task navigation

**Target revision:** `r8.1`

**Execution tasks:**

- [x] **M1-T01** — Write and accept the `StateIdentity` ADR.
- [x] **M1-T02** — Write and accept the bounded `AuthorizationGrant` ADR.
- [x] **M1-T03** — Write and accept the strengthened `EvidenceReceipt` ADR.
- [x] **M1-T04** — Write and accept the action-qualified `AcceptanceVerdict` ADR.
- [x] **M1-T05** — Create the canonical security/trust boundary page.
- [x] **M1-T06** — Create known-bad fixtures for all P0 trust invariants.

**Verification tasks:**

- [x] **M1-V01** — State/revision/content edge cases have executable fixtures.
- [x] **M1-V02** — Authorization expiry/delegation/state-binding fixtures fail closed.
- [x] **M1-V03** — Receipt replay/forgery/version/artifact-integrity fixtures fail closed.
- [x] **M1-V04** — Path traversal, symlink escape, and executable spoofing fixtures fail closed.

**Result:** `PASS`

### M1 execution record — 2026-09-24

**Result:** `PASS`

**Produced:** `harness-rig-knowledge-base-2026-09-24-r8.1.zip`

**Accepted Experimental ADRs:** StateIdentity, AuthorizationGrant, EvidenceReceipt, AcceptanceVerdict.

**Added:** canonical security/trust boundary and 16 stable known-bad fixture definitions (`M1-F01` … `M1-F16`).

**Verified:** required ADR dimensions; no named global EnvironmentIdentity type; RigYard reuse/adaptation; fixture
coverage/uniqueness; canonical YAML/link/manifest integrity.

**Boundary:** runtime execution of the fixture catalog is deferred to M3 and is not claimed by M1.

**Next:** `M2`



> Do not advance from this milestone until every required verification task above is completed and the milestone result is recorded.

**Progressive revision:** `r8.1`  
**Purpose:** resolve the high-value protocol ambiguities before implementations are encouraged to depend on them.

This milestone defines protocols and adversarial fixtures. It does not yet declare the protocols Stable.

## 6.1 StateIdentity ADR

Resolve:

```text
revision provenance
vs
source content identity
vs
dirty overlay
```

The ADR must cover:

- repository identity;
- revision/HEAD identity;
- base tree;
- tracked staged/unstaged changes;
- deletions;
- untracked nonignored files;
- file modes;
- symlinks;
- path normalization;
- worktrees;
- unborn HEAD;
- submodules;
- read errors;
- cross-platform canonical serialization.

Gate-consumed ignored/generated/external inputs should normally be recorded in gate evidence rather than universally bloating StateIdentity.

## 6.2 AuthorizationGrant ADR

Replace the incomplete top-level `AuthorizationScope` idea with a bounded grant concept.

Minimum questions:

```text
issuer
principal/grantee
action
resource/target
authority/state binding when material
issued time
expiry
delegation
revocation/invalidation
interactive vs standing/preauthorized origin
```

Do not build general IAM.

## 6.3 EvidenceReceipt ADR

Strengthen the existing evidence concept using both Harness Rig requirements and RigYard's implemented evidence patterns.

Candidate required semantics:

```text
receipt identity/version
claim
subject
authority binding
state binding
gate-specific material input bindings
producer/run provenance
gate contract version
tool/command identity
before/after state
outcome taxonomy
artifact references/digests
timing
receipt integrity/digest
admissibility
```

Native detailed artifacts remain outside the generic receipt.

## 6.4 AcceptanceVerdict ADR

A verdict must be qualified by:

```text
subject
decision_for
policy
authority/state
evidence set
authorization grants used when applicable
outcome
```

`ACCEPTED` must never mean universally correct or universally authorized.

## 6.5 Security/trust owner

Create:

```text
security-trust-and-execution-boundaries.md
```

Cover only cross-cutting invariants:

- untrusted repository/source/tool/test/browser content;
- safe command construction;
- external executable identity;
- root-contained filesystem paths;
- symlink handling;
- protected authority/oracles;
- evidence producer/admissibility;
- secret-bearing evidence artifacts;
- fork/PR trust;
- privileged release/deploy separation.

Do not create a new security subsystem.

## Verification

Create known-bad protocol fixtures before implementation:

1. commit made during session;
2. verifier mutates source;
3. identical content on a different revision;
4. staged-only edit;
5. dirty consumed submodule;
6. gate-consumed ignored input changes;
7. expired grant;
8. state-bound grant after state change;
9. nondelegable grant used by another principal;
10. forged/replayed receipt;
11. receipt from outdated gate-contract version;
12. artifact changed after receipt;
13. merge acceptance reused for deployment;
14. path traversal;
15. protected-path symlink escape;
16. malicious executable earlier on `PATH`.

## Exit criteria

- ADRs are internally consistent;
- each P0 trust claim has at least one known-bad fixture;
- no new universal identity plane was introduced without evidence;
- RigYard implemented evidence mechanisms have an explicit reuse/adaptation disposition;
- contracts remain Experimental.

---

# 7. Milestone M2 — CHANGELOG-backed source consolidation foundation

### M2 task navigation

**Target revision:** `r8.2`

**Execution tasks:**

- [x] **M2-T01** — Record the AIBoarding source baseline, target owner, and disposition in `CHANGELOG.md`.
- [x] **M2-T02** — Record the TacticSwitch source baseline, target owner, and disposition in `CHANGELOG.md`.
- [x] **M2-T03** — Record the Skill Kit KB maintainer source baseline, target owner, and disposition in `CHANGELOG.md`.
- [x] **M2-T04** — Record the Adaptive Engineering Harness source baseline, target owner, and disposition in `CHANGELOG.md`.
- [x] **M2-T05** — Record the migration-surface inventory and source→Harness Rig convergence decisions.
- [x] **M2-T06** — Classify each source capability as KEEP / ADAPT / REPLACE / DELETE_AFTER_MIGRATION / HISTORICAL_ONLY.

**Verification tasks:**

- [x] **M2-V01** — `CHANGELOG.md` contains all mandatory source/capability baselines with target ownership and disposition.
- [x] **M2-V02** — Source-specific verification/evidence is recorded where known; unavailable/unknown evidence is not invented.
- [x] **M2-V03** — `CHANGELOG.md` explicitly separates M2 semantic consolidation from deferred M11 Git-history qualification.
- [x] **M2-V04** — Licenses, state, hooks, install/update, generated, schema, test, CI, OpenSpec, and agent/role surfaces are inventoried.

**Result:** `PASS`

### M2 execution record — CHANGELOG sequencing revision — 2026-09-25

**Result:** `PASS`

The full Git-history requirement has moved to M11.

M2 now proves source-consolidation traceability using:

```text
CHANGELOG.md
canonical source/provenance records
source-surface inventory
capability dispositions
```

Machine verification:

```text
verification/m2-changelog-consolidation-verification.json
```

**Next permitted milestone:** `M3`

> This does not delete Git-history qualification. M11 remains fail-closed before M12 / 1.0.

**Progressive revision:** `r8.2`

## Purpose

Make source capabilities and migration decisions explicit before the experimental vertical slice without requiring
object-complete Git histories as an early sequencing dependency.

## CHANGELOG rule

Material source-derived semantic changes are recorded in root `CHANGELOG.md` with source identity, date, target owner,
disposition, semantic change, and verification/evidence when available.

M11 later reconciles this ledger against actual source history.

## Exit criteria

The source baselines, ownership, dispositions, migration surfaces, and deferred Git-history obligations are explicit enough
for M3 to proceed without inventing source semantics.

---


# 8. Milestone M3 — Thin complete experimental vertical slice

### M3 task navigation

**Target revision:** `r8.3`

**Execution tasks:**

- [x] **M3-T01** — Implement Direct Authority.
- [x] **M3-T02** — Implement the smallest Assurance path.
- [x] **M3-T03** — Implement direct/single-agent Topology.
- [x] **M3-T04** — Implement one command/test gate.
- [x] **M3-T05** — Issue an experimental `EvidenceReceipt`.
- [x] **M3-T06** — Issue an experimental action-qualified `AcceptanceVerdict`.

**Verification tasks:**

- [x] **M3-V01** — All M1 P0 trust fixtures run through the M3 implementation path; all M1-F01…F16 also pass.
- [x] **M3-V02** — Skipped/not-run gates cannot become PASS.
- [x] **M3-V03** — Authority/state changes invalidate applicable receipts.
- [x] **M3-V04** — Wrong-run or replayed receipts are rejected.
- [x] **M3-V05** — Missing authorization produces `BLOCKED`.

**Result:** `PASS`

### M3 execution record — 2026-09-25

**Implementation:** `prototype/harness_rig/`

**Runtime:** Python 3.13.5 + Git 2.47.3

**Runtime result:** `22/22 PASS`

Machine evidence:

```text
verification/m3-unittest-output.txt
verification/m3-fixture-results.json
verification/m3-verification-record.json
verification/m3-cli-smoke.json
```

Implemented path:

```text
Direct Authority
→ one Assurance requirement
→ direct/single-process Topology
→ one command/test gate
→ Experimental EvidenceReceipt
→ Experimental action-qualified AcceptanceVerdict
```

Additional verified properties:

```text
command timeout -> BLOCKED
artifact digest tamper -> REWORK
wrong gate contract -> BLOCKED
merge verdict != deploy verdict
../ traversal -> reject
protected symlink escape -> reject
unexpected PATH executable -> BLOCKED when expected identity is required
```

**Next permitted milestone:** `M4`

> M3 PASS proves the Experimental path. It does not itself promote any contract to Stable.

**Progressive revision:** `r8.3`

## Scope

M3 implemented exactly one minimum-sufficient direct path. No OpenSpec provider, multi-agent machinery, recurrence, plugin
runtime, database, or universal environment identity was introduced.

## Reuse boundary

The generic receipt uses run/producer/gate/artifact binding patterns already demonstrated in RigYard evidence without copying
RigYard's native worker-result schemas into the core receipt.

## Exit criteria

A complete direct path works without OpenSpec or multi-agent machinery, and every M3 verification task passes.

M4 may now evaluate—not assume—promotion of the proven cross-cutting contracts.

---


# 9. Milestone M4 — Core promotion and module-boundary convergence

### M4 task navigation

**Target revision:** `r8.4`

**Execution tasks:**

- [x] **M4-T01** — Evaluate promotion of `AuthorityRef`.
- [x] **M4-T02** — Evaluate promotion of `AuthorizationGrant`.
- [x] **M4-T03** — Evaluate promotion of `StateIdentity`.
- [x] **M4-T04** — Evaluate promotion of `EvidenceReceipt`.
- [x] **M4-T05** — Evaluate promotion of `AcceptanceVerdict`.
- [x] **M4-T06** — Keep `AssurancePlan`, `ExecutionPlan`, Context internals, RuntimeResolution, and recurrence state module/adapter-owned unless proven cross-cutting.
- [x] **M4-T07** — Remove `ContextManifest` from initial stable core unless a second independent consumer proves need.

**Verification tasks:**

- [x] **M4-V01** — Each promoted core contract has two concrete consumers or one unavoidable cross-cutting invariant.
- [x] **M4-V02** — No provider-specific escape fields are needed.
- [x] **M4-V03** — Assurance cannot select workers.
- [x] **M4-V04** — Topology cannot waive evidence or broaden authorization.
- [x] **M4-V05** — Version/migration/failure semantics are explicit for promoted contracts.

**Result:** `PASS`

> Do not advance from this milestone until every required verification task above is completed and the milestone result is recorded.

**M4 completion record (2026-09-25):**

```text
AuthorityRef        SPLIT_STABLE_INVARIANT_FROM_EXPERIMENTAL_PROVIDER_FIELDS
AuthorizationGrant PROMOTE_STABLE
StateIdentity       PROMOTE_STABLE
EvidenceReceipt     KEEP_EXPERIMENTAL_SHARED
AcceptanceVerdict   KEEP_EXPERIMENTAL_SHARED
```

Stable v1 promotion is limited to the provider-neutral `AuthorityRef` envelope, bounded `AuthorizationGrant`, and exact
`StateIdentity`. Direct-provider authority path/content fields remain provider-owned. `EvidenceReceipt` remains Experimental
shared because only one Harness Rig gate provider exists; `AcceptanceVerdict` remains Experimental shared because there is
not yet a second real consequential lifecycle consumer.

Verification evidence: all 22 affected M3 regression tests and all 15 M4 adversarial/promotion tests pass; unknown/incompatible
Stable contract versions fail closed; exact Experimental v1 grant/state forms migrate deterministically after old-integrity
validation; the AuthorityRef legacy Direct form migrates without freezing provider fields; Assurance cannot select workers;
and Topology cannot waive evidence or broaden/mint authorization.

**Progressive revision:** `r8.4`  
**Purpose:** stabilize only abstractions that real consumers have proven necessary.

## Candidate stable core

Evaluate promotion for:

```text
AuthorityRef
AuthorizationGrant
StateIdentity
EvidenceReceipt
AcceptanceVerdict
```

`CapabilitySet` remains Experimental until host evidence proves its shared semantics.

## Keep module-owned initially

```text
AssurancePlan
ExecutionPlan
Context internal manifests/indexes
RuntimeResolution
recurrence continuation state
```

Remove `ContextManifest` from the initial stable core unless a second independent consumer proves a cross-cutting need.

## Assurance / Topology boundary

Finalize:

```text
Assurance
  what evidence/independence/authorization predicates are required

Topology
  what minimum execution formation and technical permissions satisfy them

HostAdapter
  what the host can actually enforce/observe

Acceptance
  whether the required predicates were actually satisfied
```

An `ExecutionPlan` may narrow authorization but never broaden it.

## Verification

- direct authority provider consumes promoted contracts cleanly;
- one command gate consumes promoted contracts cleanly;
- no provider-specific escape fields are required;
- Assurance does not select workers;
- Topology does not waive gates/risk;
- technical permission capability does not imply authorization;
- policy change invalidates an obsolete AssurancePlan;
- all core contracts have explicit version/migration/failure semantics.

## Exit criteria

A contract is promoted only when:

```text
two concrete consumers need the shared semantics
OR
one unavoidable cross-cutting invariant cannot safely live elsewhere
```

---

# 10. Milestone M5 — Context convergence and canonical knowledge lifecycle

### M5 task navigation

**Target revision:** `r8.5`

**Execution tasks:**

- [x] **M5-T01** — Finalize canonical-KB vs Context-lifecycle ownership.
- [x] **M5-T02** — Define stable-ID rename/move/split/merge/retirement rules.
- [x] **M5-T03** — Define provenance and source-freshness conventions.
- [x] **M5-T04** — Implement source reconciliation and conflict/gap preservation.
- [x] **M5-T05** — Implement deterministic manifest generation and whole-collection audit.
- [x] **M5-T06** — Keep root `AGENTS.md` as rules/navigation, not duplicate canonical knowledge.

**Verification tasks:**

- [x] **M5-V01** — Rename/split/merge/retirement fixtures pass.
- [x] **M5-V02** — External-source freshness changes are detected correctly.
- [x] **M5-V03** — Conflicts remain explicit and unsupported claims are rejected.
- [x] **M5-V04** — Canonical KB changes and AGENTS projection drift have exactly one owner each.
- [x] **M5-V05** — No vector/RAG subsystem is introduced.

**Result:** `PASS`

> M5 completed with PASS on 2026-09-25. M6 is the next permitted milestone; no M6 execution is included in r8.5.

**Progressive revision:** `r8.5`  
**Purpose:** merge AIBoarding lifecycle behavior with Skill Kit canonical KB behavior without retaining two truth/freshness systems.

## Final Context ownership

### Canonical KB owns

```text
durable factual/project knowledge
stable IDs
provenance
source reconciliation
material conflicts/gaps
canonical-content freshness
manifest
structural integrity
```

### Context lifecycle owns

```text
root AGENTS.md/navigation projection
host-facing loading/projection
projection freshness
onboarding/install lifecycle
projection compression
```

## Stable ID lifecycle

Define:

```text
rename/move -> preserve ID
split -> primary successor keeps old ID; other topics receive new IDs
merge -> one surviving ID; retired IDs recorded when needed
retired ID -> never reused for unrelated knowledge
```

Use optional lineage metadata only when necessary.

## Provenance

For volatile material, record:

```text
source
version/commit when available
checked date
```

Do not use page `updated` as source-freshness proof.

## Verification

- rename fixture;
- split fixture;
- merge fixture;
- deleted/retired ID non-reuse;
- external source advances without page edit;
- source conflict preserved explicitly;
- unsupported conclusion rejected;
- canonical page change makes AGENTS projection stale;
- projection-only change does not rewrite canonical KB;
- deterministic manifest generation;
- full collection structural audit.

## Executed verification — r8.5

```text
M3 regression suite: 22/22 PASS
M4 adversarial suite: 15/15 PASS
M5 Context lifecycle suite: 14/14 PASS
combined discovery: 51/51 PASS
canonical references / manifest rows: 39 / 39
manifest regeneration: byte-identical
root AGENTS projection: FRESH
whole-collection audit: PASS
retrieval-subsystem surface scan: NONE
CLI smoke: command-gate PASS -> merge ACCEPTED
```

## Exit criteria

Exactly one component owns each kind of Context freshness and knowledge identity.

No vector/RAG/retrieval subsystem is introduced.

---

# 11. Milestone M6 — OpenSpec as the first-class external SpecEngine

### M6 task navigation

**Target revision:** `r8.6`

**Execution tasks:**

- [x] **M6-T01** — Implement/refine DirectAuthorityProvider and OpenSpecAdapter.
- [x] **M6-T02** — Refine the experimental `SpecEngine` interface from real consumers.
- [x] **M6-T03** — Define/test the default OpenSpec authority fingerprint profile.
- [x] **M6-T04** — Implement authority-bearing referenced-spec handling.
- [x] **M6-T05** — Implement effective OpenSpec health/config/rules checks.
- [x] **M6-T06** — Expose guarded `harness-rig spec archive` with transition evidence.

**Verification tasks:**

- [x] **M6-V01** — Base Harness Rig works when OpenSpec is absent.
- [x] **M6-V02** — OpenSpec-required workflows fail closed when OpenSpec is unavailable.
- [x] **M6-V03** — Authority fingerprint distinguishes tasks-only vs behavior-bearing changes.
- [x] **M6-V04** — Malformed config/rules and unresolved authority references fail appropriately.
- [x] **M6-V05** — Archive partial/postcondition failures return BLOCKED.
- [x] **M6-V06** — Post-archive acceptance is reevaluated against final authority/state.

**Result:** `PASS`

> Do not advance from this milestone until every required verification task above is completed and the milestone result is recorded.

**Progressive revision:** `r8.6`  
**Purpose:** prove OpenSpec-first spec-driven work without making OpenSpec a hard dependency.

## Scope

Implement/refine:

```text
DirectAuthorityProvider
OpenSpecAdapter
experimental SpecEngine -> minimum shared interface
```

Use current machine-readable OpenSpec surfaces rather than internal parsing.

## Authority profile

Establish a tested default authority fingerprint profile.

Initial hypothesis:

```text
authority-bearing:
  approved scope/proposal
  behavioral delta specifications
  design clauses that materially constrain implementation

normally not authority-bearing:
  task completion bookkeeping
  timestamps
  incidental ordering metadata
  engine version itself
```

Test rather than assume.

## Referenced authority

Only actually authority-bearing references should affect authority identity.

An unavailable authority-bearing reference must produce:

```text
BLOCKED
```

not warning-only acceptance.

## Effective health

Verify:

```text
CLI/version
root/store resolution
schema/artifact graph
effective instructions/rules
strict validation
reference resolution
```

Do not equate process exit zero with complete health.

## Archive

Expose guarded:

```text
harness-rig spec archive
```

Conceptually:

```text
(A0,S0)
   ↓
guarded OpenSpec archive
   ↓
(A1,S1)
```

Record a transition receipt.

Ambiguous or partial mutation => `BLOCKED`.

## Verification

- OpenSpec executable absent -> base Harness Rig remains operational;
- OpenSpec-required project -> fail closed when unavailable;
- tasks-only edit;
- proposal/scope edit;
- behavioral-spec edit;
- constraining-design edit;
- irrelevant metadata edit;
- `skip_specs`;
- custom artifact graph;
- malformed config/rules;
- strict validation failure;
- semantic coherence failure;
- unresolved authority-bearing reference;
- archive partial mutation;
- archive postcondition mismatch;
- final post-archive acceptance reevaluated against A1/S1.

## M6 execution result

Implemented at `r8.6`:

```text
DirectAuthorityProvider
OpenSpecAdapter (OpenSpec 1.13.2 compatibility profile)
Experimental SpecEngine: available / health / authority / archive
harness-rig/openspec-authority-profile/v1
guarded harness-rig spec archive
```

Verification retained in the r8.6 package proves base operation without OpenSpec, fail-closed required workflows, tasks-vs-behavior authority identity, custom artifact graphs, `skip_specs`, authority-bearing references, malformed rules/strict-validation failures, partial/postcondition archive failures, semantic-review fail-closed behavior, bounded authorization, transition evidence, and final `(A1,S1)` stale-precondition reevaluation.

Primary external Store archive remains deliberately unqualified until exact state identity can observe that mutation domain. This is a bounded M6 limitation, not an implicit Stable capability claim.

## Exit criteria

OpenSpec is the normal behavior-change engine but remains an external capability behind a bounded adapter.

---

# 12. Milestone M7 — Trusted repository enforcement

### M7 task navigation

**Target revision:** `r8.7`

**Execution tasks:**

- [x] **M7-T01** — Emit a CI obligation artifact for the evaluated revision.
- [x] **M7-T02** — Make `ci / required` execute even after prerequisite failures.
- [x] **M7-T03** — Validate every mandatory obligation/result explicitly.
- [x] **M7-T04** — Support merge queues via `merge_group` when enabled.
- [x] **M7-T05** — Define untrusted fork and privileged workflow boundaries.
- [x] **M7-T06** — Protect CI/resolver/policy/oracle paths as governance-sensitive surfaces.

**Verification tasks:**

- [x] **M7-V01** — Prerequisite-failure meta-test passes.
- [x] **M7-V02** — Skipped mandatory job is detected.
- [x] **M7-V03** — Merge-queue scenario is covered.
- [x] **M7-V04** — Fork PR cannot access privileged secrets/actions.
- [x] **M7-V05** — Self-modifying CI/resolver and wrong-SHA/wrong-producer cases fail closed.

**Result:** `PASS`

**Verification evidence:** 14/14 M7 repository-enforcement tests PASS; combined M3-M7 discovery 81/81 PASS; package-local workflow/policy checks PASS. Remote GitHub ruleset/CODEOWNERS installation was not claimed or required as local executable evidence.

**Allowed next milestone:** `M8`

**Progressive revision:** `r8.7`  
**Purpose:** make one repository-wide verdict actually mean all mandatory obligations ran for the intended revision.

## CI obligation artifact

The affected-work resolver emits:

```text
evaluated revision / merge-group subject
affected modules
mandatory obligations
expected result identities
```

This remains CI/application evidence, not a new stable core contract.

## `ci / required`

Must:

- execute even when prerequisite jobs fail;
- explicitly inspect every mandatory obligation;
- reject missing/disallowed skipped results;
- confirm expected revision/event subject;
- confirm expected producer;
- include governance/KB-integrity requirements.

## GitHub trust

Support:

- `pull_request`;
- `push` as appropriate;
- manual dispatch;
- `merge_group` when merge queues are enabled;
- untrusted fork mode;
- C3 protection of workflows/resolver/policy/oracle paths.

Do not use privileged `pull_request_target` to execute untrusted PR code.

Organization-owned required workflows may be a stronger optional mode where available.

## Verification

CI meta-fixtures:

1. prerequisite fails;
2. downstream aggregator would normally skip;
3. mandatory job condition evaluates false;
4. merge queue event;
5. fork PR without secrets;
6. PR modifies the affected-module resolver;
7. PR modifies its own required workflow;
8. wrong SHA result;
9. same check name from wrong producer/event;
10. generated artifact changes through an upstream source path.

## Exit criteria

One green repository verdict implies a complete, same-subject obligation set — not merely a green aggregator job.

---

# 13. Milestone M8 — Host capability and topology qualification

### M8 task navigation

**Target revision:** `r8.8`

**Execution tasks:**

- [ ] **M8-T01** — Select and qualify the first Stable host candidate.
- [ ] **M8-T02** — Reuse RigYard's implemented/local/native-qualified/Stable maturity distinction.
- [ ] **M8-T03** — Refine `CapabilitySet` from observed native behavior.
- [ ] **M8-T04** — Define fresh-verifier semantics as a real context/permission boundary.
- [ ] **M8-T05** — Reconcile RigYard isolated-writer capability as optional and evidence-gated.

**Verification tasks:**

- [ ] **M8-V01** — Clean-process discovery and launch pass.
- [ ] **M8-V02** — Requested/resolved/observed facts are captured.
- [ ] **M8-V03** — Read-only and isolation requirements are actually enforced or BLOCKED.
- [ ] **M8-V04** — Crash/reconciliation and evidence attribution pass.
- [ ] **M8-V05** — Isolated-writer Stable claim requires retained formal native evidence.

**Result:** `NOT_RUN`

> Do not advance from this milestone until every required verification task above is completed and the milestone result is recorded.

**Progressive revision:** `r8.8`  
**Purpose:** derive capability semantics from real host evidence rather than designing a universal host model first.

## First Stable host candidate

Use the strongest retained native evidence as the starting point.

Current RigYard evidence makes Codex/Linux the natural first candidate.

Do not make all Claude/Codex/Copilot integrations Stable merely for symmetry.

## Reuse RigYard qualification semantics

Preserve distinctions:

```text
implemented
locally tested
native qualified
Stable claim
```

## CapabilitySet

Only now refine the shared CapabilitySet.

Each claimed capability should include:

```text
status
host/runtime profile
evidence source
tested version/mode
observation time/freshness
limitations
```

## Fresh verifier

Must represent a real context boundary:

- did not implement/own the batch;
- cannot write when read-only is required;
- did not inherit the full implementation transcript unless policy explicitly allows bounded context;
- is attributable to the intended host/runtime.

## Isolated writers

RigYard v0.3 is implementation-complete enough to inform Harness Rig, but its formal real-host isolated-writer qualification remains incomplete.

Do not claim it Stable until the retained formal packet exists.

## Verification

For the first Stable candidate:

- clean-process discovery;
- launch;
- exact mode/profile observation;
- fresh verifier;
- read-only enforcement;
- worktree/isolation behavior;
- unsupported capability fail-closed;
- requested/resolved/observed distinction;
- process crash/reconciliation;
- evidence attribution.

For isolated writers:

- two genuinely concurrent writers;
- canonical root inaccessible;
- peer root inaccessible;
- attributable outputs;
- conflict classification;
- cleanup/recovery;
- no prompt-only isolation credit;
- formal retained native evidence packet.

## Exit criteria

At least one host path is genuinely qualified.

Other built-in adapters retain Experimental/Beta labels until their own evidence exists.

---

# 14. Milestone M9 — Gate platform, Playwright, architecture, and mutation verification

### M9 task navigation

**Target revision:** `r8.9`

**Execution tasks:**

- [x] **M9-T01** — Define minimal common gate claim/outcome semantics.
- [x] **M9-T02** — Implement/refine the architecture gate provider.
- [x] **M9-T03** — Implement/refine the Playwright provider with explicit required scenarios.
- [x] **M9-T04** — Reconcile RigYard harness-mutation-verification as a bounded development gate.
- [x] **M9-T05** — Map invariant → mutant → detector for mutation fixtures.

**Verification tasks:**

- [x] **M9-V01** — Required Playwright skip/no-test cannot PASS.
- [x] **M9-V02** — Flaky retries remain visible.
- [x] **M9-V03** — Healer oracle mutation reopens authority.
- [x] **M9-V04** — Wrong-worktree/shared-data/console-network failure fixtures behave correctly.
- [x] **M9-V05** — A deliberate architecture violation is detected.
- [x] **M9-V06** — At least one mutation red/green detector-gap example is proven.

**Result:** `PASS`

> Do not advance from this milestone until every required verification task above is completed and the milestone result is recorded.

**Progressive revision:** `r8.9`  
**Purpose:** broaden evidence only after generic gate semantics are precise.

## Common gate result semantics

Every gate must identify:

```text
claim
subject
required input bindings
actual execution status
artifacts
outcome
```

Minimum outcome distinctions should cover the failures needed by real providers, including:

```text
PASS
FAIL
BLOCKED/UNAVAILABLE
SKIPPED when meaningful
FLAKY/PARTIAL where the provider can produce them
```

Do not create a giant universal taxonomy beyond demonstrated providers.

## Architecture gate

Ship a built-in provider.

Require it only when project policy declares mechanically enforceable architecture rules.

## Playwright provider

Define:

```text
required scenario set
executed scenarios
skipped scenarios
flaky scenarios
failed scenarios
test-source identity
server/worktree identity
browser/project/tool identity
runtime/fixture input bindings
artifact references
```

Policy:

```text
required skip != PASS
required no-test != PASS
flake remains visible
healer changes protected oracle -> authority reopened
healer changes implementation -> new state, fresh verification
```

## Mutation verification

Reconcile RigYard's active `add-harness-mutation-verification` proposal.

This is a good candidate for field-hardening because it directly tests whether harness detectors catch deliberate weakenings.

Keep it:

- deterministic;
- repository-owned;
- curated;
- bounded;
- development-only;
- outside runtime/public protocol;
- mapped from invariant -> mutant -> detector.

Require at least one red/green detector-gap example before calling the mutation gate useful.

## Verification

- required Playwright test skipped;
- fail then pass retry;
- healer edits expected result;
- wrong-worktree server;
- shared DB fixture contamination;
- console/network failure with visual PASS;
- secret seeded into trace/log;
- architecture violation deliberately introduced;
- semantic mutation survives before detector strengthening;
- same mutation killed after detector strengthening.

## Exit criteria

Every first-class gate's PASS claim is narrower and more explicit than "tool exited zero."

---

# 15. Milestone M10 — Product CLI, migration completion, and release provenance

### M10 task navigation

**Target revision:** `r8.10`

**Execution tasks:**

- [x] **M10-T01** — Finalize compact CLI including guarded `spec archive`.
- [x] **M10-T02** — Define versioned JSON and exit-code semantics.
- [x] **M10-T03** — Define config precedence and noninteractive behavior.
- [x] **M10-T04** — Define cancellation/timeout cleanup.
- [x] **M10-T05** — Finalize migration completion/rollback criteria.
- [x] **M10-T06** — Finalize minimum release provenance/checksum/attestation behavior.

**Verification tasks:**

- [x] **M10-V01** — Noninteractive BLOCKED semantics pass.
- [x] **M10-V02** — Malformed/global-weakened config cases fail safely.
- [x] **M10-V03** — Cancellation/timeout cleanup is verified.
- [x] **M10-V04** — Interrupted migration and mixed old/new state fixtures pass.
- [x] **M10-V05** — Rollback/downgrade behavior is tested/documented.
- [x] **M10-V06** — Build→artifact provenance is consistent.

**Result:** `PASS`

> Do not advance from this milestone until every required verification task above is completed and the milestone result is recorded.

**Progressive revision:** `r8.10`  
**Purpose:** turn the verified internals into a small predictable product surface.

## CLI surface

Target:

```text
harness-rig init
harness-rig doctor
harness-rig spec status
harness-rig spec archive
harness-rig verify
harness-rig status
harness-rig migrate
```

Do not wrap every external command.

## Machine contract

Automation-facing commands need:

```text
versioned JSON envelope
documented exit categories
noninteractive behavior
BLOCKED/degraded representation
timeout/cancellation cleanup
configuration precedence
```

Repository policy may not be weakened by user-global configuration.

## Migration completion

M10 separates **runtime/schema migration completion** from **1.0/source-history migration completion** so the earlier M11 deferral remains explicit rather than being silently bypassed.

Runtime/schema migration is complete when:

- every imported capability has a keep/adapt/replace/delete disposition;
- supported legacy state is migrated or explicitly unsupported;
- install/runtime paths converge;
- duplicate Context/state/evidence/routing ownership is removed;
- duplicate hooks are removed;
- generated distributions have one source;
- the supported upgrade is tested;
- rollback/downgrade policy is tested/documented;
- legacy product transition status is documented.

1.0/source-history migration additionally requires M11 PASS, including preserved/reconciled source history and reproducible commit/tag mappings. M10 records that prerequisite as `PENDING_M11`; it does not fabricate real source-history maps.

## Release provenance

Minimum:

```text
accepted source revision
accepted repository verdict
build workflow identity
generated distributions
artifact digests/checksums
attestation where operationally useful
immutable release record
```

Pin or otherwise control mutable build inputs where release integrity depends on them.

Do not introduce an additional signing platform without a consumer requirement.

## Verification

- noninteractive BLOCKED;
- malformed project config;
- global user config attempts to weaken repo policy;
- Ctrl-C/timeout during verifier;
- guarded archive unavailable;
- JSON backward-compatibility fixture;
- interrupted migration;
- mixed old/new state;
- duplicate hook firing;
- schema migration rollback/downgrade;
- old->new commit lookup;
- rebuild/release provenance consistency.


## M10 execution outcome

Implemented at `r8.10`:

- compact product command surface with versioned `harness-rig/cli-envelope/v1` machine output;
- retained r8.9 raw JSON compatibility for direct verification, doctor, and guarded archive;
- defaults < user-global < project < CLI configuration precedence, with repository policy unavailable to user-global override;
- fail-closed noninteractive behavior and process-group cleanup for direct verifier timeout/cancellation;
- atomic `harness-rig/migration-state/v1` with supported r8.9 -> r8.10 upgrade, explicit rollback, interrupted/mixed-state/duplicate-hook detection, and `PENDING_M11` history qualification;
- deterministic `harness-rig/release-record/v1` artifact digests and immutable record verification, with missing accepted repository verdict represented as `BLOCKED`;
- no signing platform, migration service, configuration server, or orchestration framework.

M10 verification adds 18 adversarial/product tests. The clean-process M3-M10 regression is 133/133 PASS (22 + 15 + 14 + 16 + 14 + 14 + 20 + 18); the canonical KB audit is 44 references / 44 manifest rows with a FRESH root projection and byte-identical manifest regeneration. Final package evidence is retained under `verification/m10-*`. Real object-complete source histories and source->rewritten commit/tag maps remain M11 work and are not claimed by M10.

## Exit criteria

A CI system and a human can both operate Harness Rig without interpreting prose or scraping unstable console output.

---

# 16. Milestone M11 — RigYard disposition, Git-history qualification, and field hardening

### M11 task navigation

**Target revision:** `r8.11`

**Execution tasks:**

- [x] **M11-T01** — Disposition v0.3 isolated writers.
- [x] **M11-T02** — Disposition harness mutation verification.
- [x] **M11-T03** — Disposition v0.4 approved revision/traceability requirements.
- [x] **M11-T04** — Disposition v0.5 static composition.
- [x] **M11-T05** — Disposition v0.6 richer topology families.
- [x] **M11-T06** — Disposition v0.7 distributed execution.
- [x] **M11-T07** — Disposition v0.8 observability/effects.
- [x] **M11-T08** — Claude native qualification is out of scope for now per
  user direction; not an M11 acceptance gate.
- [x] **M11-T09** — Complete representative Codex Desktop/CLI implementation
  and native capability qualification with recorded limits. Evidence:
  `verification/m11-codex-field-pilot.json`.
- [x] **M11-T10** — Validate object-complete AIBoarding, TacticSwitch, and Skill Kit bundles and refs.
- [x] **M11-T11** — Retain full source histories as submodules at audited pins; do not rewrite upstream history.
- [x] **M11-T12** — Reconcile source pins, refs, bundles, and `CHANGELOG.md`; see `verification/m11-changelog-reconciliation.json`.
- [x] **M11-T13** — Retain raw legacy failures and separate passing adapter results; see `verification/m11-import-only-status.json` and `verification/m11-legacy-check-results.json`.
- [x] **M11-T14** — Inventory source refs, surfaces, signatures, and tag objects; see `verification/m11-source-repository-inventory/` and `verification/m11-object-fidelity-audit.json`.

**Verification tasks:**

- [x] **M11-V01** — Every active RigYard proposal has exactly one Harness Rig disposition.
- [x] **M11-V02** — Deferred features have explicit evidence triggers.
- [x] **M11-V03** — Field-pilot evidence records authorized read-only and
  implementation pilots, outcomes, costs, and limits.
- [x] **M11-V04** — In-scope proposals with no distinct value are deferred or
  kept optional. Bounded mutation verification remains for its distinct
  detector-gap evidence. See `verification/m11-rigyard-dispositions.json`.
- [x] **M11-V05** — The one-parent import commit contains only the approved gitlinks and `.gitmodules`; see `verification/m11-import-only-status.json`.
- [x] **M11-V06** — Retain legacy failures and passing import-only evidence;
  all M11 acceptance criteria now have evidence.
- [x] **M11-V07** — `CHANGELOG.md` reconciles with actual source history; material discrepancies are resolved or explicitly recorded. Evidence: `verification/m11-changelog-reconciliation.json`.
- [x] **M11-V08** — Exact upstream signature-bearing commits and tag objects are retained and matched to bundles; local trust revalidation limits are recorded.

**Result:** `PASS`

> M11 is the late provenance/history gate. Unavailable required source history blocks M12/1.0, not M3–M10.

**Progressive revision:** `r8.11`

**Purpose:** explicitly reconcile remaining RigYard proposals, field-harden the system, and qualify full source history before final 1.0 acceptance.

Current status: M11-T01–T14 and M11-V01–V08 are complete. Codex Desktop and
CLI field pilots cover the real adapter/check path, synthetic implementation
and fresh verification, and observed Windows workspace boundaries in elevated
and unelevated modes. M11 passed with recorded limits; M12 is eligible. See
`verification/m11-history-qualification-status.json` and
`verification/m11-codex-field-pilot.json`.

## 16.1 v0.3 isolated parallel writers

Disposition target:

```text
INCLUDE as optional Topology capability
NOT default
NOT Stable until formal native evidence exists
```

## 16.2 Harness mutation verification

Disposition target:

```text
INCLUDE as bounded field-hardening/development gate
```

if M9 proves it catches a distinct failure.

## 16.3 v0.4 approved pipeline evolution / traceability

Do not import a universal pipeline subsystem automatically.

Extract only requirements that map to real Harness Rig concepts:

```text
immutable approved plan/revision identity where plans persist
active work pinned to approved revision
deterministic material-impact review
requirement -> verification-obligation traceability where project policy requires it
```

Admit this only if the Harness Rig execution-plan/pipeline product actually needs persistent approved revisions.

Otherwise keep it deferred.

## 16.4 v0.5 static composition

Default disposition:

```text
DEFER / EARNED
```

It solves authoring duplication but adds another authoring language.

Admit only after repeated real duplication in stable plan/pipeline artifacts.

If ever admitted, composition must compile away before approval/runtime.

## 16.5 v0.6 richer topology

Default disposition:

```text
DEFER POST-1.0
```

Potential families are admitted independently:

```text
conditional branch
bounded loop
bounded fan-out
map/reduce
compensation
```

No family receives authority merely because another family is proven.

No runtime graph mutation or model-selected edges.

## 16.6 v0.7 distributed execution

Default disposition:

```text
DEFER POST-1.0
```

This crosses a major trust boundary:

```text
authenticated remote identity
transport
shared durable storage
leases
partitions
remote crash/replay
```

Do not include until a real cross-host workflow requires it.

## 16.7 v0.8 operational observability and effects

Split the proposal.

### Keep before/at 1.0

Minimal diagnostic/audit observability needed to understand:

```text
routing
gate failures
evidence freshness
host degradation
migration failures
```

Do not build a telemetry platform.

### Defer

Generic external-effect workflow support unless Harness Rig is intentionally going to execute external side effects.

If later admitted:

```text
controller-owned effect identity
explicit authorization
idempotency
durable receipt
ambiguous-effect BLOCKED behavior
```

## 16.8 Claude native qualification (OUT OF SCOPE)

Do not run Claude native qualification for M11 or M12. Reopen only after an
explicit scope decision. This work is not an acceptance gate.

## Field pilot

Run representative projects:

1. small behavior change;
2. ambiguous change;
3. existing detailed RFC;
4. high-risk migration/security change;
5. browser/UI change;
6. non-behavioral refactor;
7. isolated writer scenario if supported;
8. multiple host adapters with different maturity.

Measure:

```text
false acceptance
missing requirements
rework
stale authority/evidence
KB drift
CI obligation misses
gate flake
host degradation
human review time
agent/tool/context cost
contract count
persistent state count
hooks
handoffs
```

## Simplification review

For every non-trivial mechanism ask:

```text
Did it catch a distinct failure?
Can an existing mechanism now replace it?
Can it become optional?
Can it be deleted?
Can its contract shrink?
```

## 16.9 Full Git-history qualification

M11 owns the Git requirements originally assigned to M2.

Required sequence:

```text
validate object-complete histories
→ rewrite/import to isolated legacy prefixes
→ generate source→rewritten commit/tag maps
→ verify tree/topology equivalence
→ run relevant legacy deterministic checks
→ prove import-only commits
→ reconcile migration surfaces
→ reconcile CHANGELOG.md against actual history
→ resolve signed commit/tag fidelity requirements
```

Prepared tooling is retained under `verification/m11-*`.

If required source history is unavailable or unverifiable:

```text
M11 = BLOCKED
M12 cannot PASS
```

## Exit criteria

Every active RigYard proposal has one explicit disposition, field pilots have driven a simplification review, and full
source-history qualification has reconciled `CHANGELOG.md` against actual history with no unresolved provenance gap capable
of invalidating 1.0.

---

# 17. Milestone M12 — 1.0 qualification and final simplification

### M12 task navigation

**Target revision:** `r8.12`

**Execution tasks:**

- [ ] **M12-T01** — Run the full deterministic repository suite.
- [ ] **M12-T02** — Run KB self-validation.
- [ ] **M12-T03** — Run all P0 adversarial trust fixtures.
- [ ] **M12-T04** — Run OpenSpec compatibility fixtures.
- [ ] **M12-T05** — Run CI obligation meta-suite.
- [ ] **M12-T06** — Verify retained native evidence for at least one Stable host.
- [ ] **M12-T07** — Run gate-provider adversarial suite.
- [ ] **M12-T08** — Run migration upgrade/rollback fixtures.
- [ ] **M12-T09** — Run release provenance smoke.
- [ ] **M12-T10** — Run one fresh-context architecture review.
- [ ] **M12-T11** — Run final feature-retirement review.

**Verification tasks:**

- [ ] **M12-V01** — No unresolved P0/P1 issue invalidates a 1.0 claim.
- [ ] **M12-V02** — The supported trust invariant is demonstrably true.
- [ ] **M12-V03** — The final product is smaller than the union of imported/planned systems.

**Result:** `NOT_RUN`

> Do not advance from this milestone until every required verification task above is completed and the milestone result is recorded.

**Progressive revision:** `r8.12` / 1.0 planning baseline  
**Purpose:** prove that the resulting platform is both trustworthy and smaller than the union of its source projects.

## Required 1.0 conditions

### Trust kernel

- stable `AuthorityRef`;
- stable bounded `AuthorizationGrant`;
- exact, cross-platform `StateIdentity`;
- admissible claim-specific `EvidenceReceipt`;
- action-qualified `AcceptanceVerdict`;
- gate-specific material input binding.

### Context

- canonical KB lifecycle;
- deterministic manifest/integrity;
- provenance and freshness rules;
- clean AIBoarding lifecycle / canonical-KB ownership boundary.

### Specification

- OpenSpec-first working path;
- no OpenSpec hard dependency;
- tested compatibility profile;
- deterministic authority fingerprint;
- guarded archive transition.

### Assurance / Topology

- separate ownership;
- one-agent direct path proven;
- additional contexts only when justified;
- at least one real isolation/freshness mechanism proven.

### Host

- at least one genuinely Stable host path;
- other adapters labeled according to evidence.

### Gates

- command/test gate;
- KB integrity gate;
- OpenSpec gate;
- architecture/Playwright providers only at the maturity their evidence supports.

### Repository enforcement

- one complete repository verdict;
- merge-queue/fork/workflow trust semantics;
- protected acceptance/governance surfaces.

### Product

- stable machine-readable CLI contract;
- safe migration/rollback;
- release provenance;
- security/trust boundaries.

## Explicitly not required for 1.0

```text
generic recurrence infrastructure
adaptive model/effort optimization
all host adapters Stable
shared OpenSpec Store backbone
static composition
richer topology families
distributed execution
external-effect platform
public plugin SDK/marketplace
generic telemetry platform
new retrieval infrastructure
vector/embedding/RAG subsystem
```

## Final verification

1. full deterministic repository suite;
2. KB self-validation;
3. all P0 adversarial trust fixtures;
4. OpenSpec compatibility fixture suite;
5. CI obligation meta-suite;
6. first Stable host retained native evidence;
7. gate provider adversarial suite;
8. migration upgrade/rollback fixtures;
9. release provenance smoke;
10. one fresh-context architecture review against the full final package;
11. feature-retirement review;
12. no unresolved P0/P1 issue that invalidates a 1.0 claim.

## Exit criteria

The product can truthfully claim:

> For its supported scope, Harness Rig binds accepted intent, bounded authorization, exact evaluated state, required evidence, and the acceptance decision without silently substituting weaker mechanisms when required capabilities are unavailable.

---

# 18. Cross-milestone verification matrix

| Milestone | Primary invariant proven | Main verification mode |
|---|---|---|
| M0 | planning corpus itself is structurally/evidentially trustworthy | deterministic KB/source audit |
| M1 | trust protocols are precise enough to falsify | ADR review + adversarial fixtures |
| M2 | imported sources remain attributable and historically intact | history/test provenance |
| M3 | smallest end-to-end trust path works | direct vertical integration tests |
| M4 | only proven abstractions enter core | multi-consumer contract tests |
| M5 | one canonical Context knowledge/freshness ownership model | KB lifecycle/drift fixtures |
| M6 | OpenSpec is first-class without hard dependency | adapter/authority/archive fixtures |
| M7 | one green CI verdict means complete required obligations | CI meta-tests |
| M8 | host capability claims correspond to observed native enforcement | retained native host evidence |
| M9 | gate PASS means the stated claim was actually observed | provider-specific adversarial tests |
| M10 | users/CI can operate product deterministically | CLI/migration/release tests |
| M11 | RigYard proposals are admitted by evidence, not inheritance | field pilots + disposition review |
| M12 | 1.0 scope is trustworthy and minimum-sufficient | full qualification + simplification review |

---

# 19. Dependency graph

```text
M0
 ↓
M1
 ↓
M2
 ↓
M3
 ↓
M4
 ├─────────────┐
 ↓             ↓
M5            M6
 └──────┬──────┘
        ↓
       M7
        ↓
       M8
        ↓
       M9
        ↓
      M10
        ↓
      M11
        ↓
      M12
```

Interpretation:

- M0 and M1 are mandatory before stable architecture work.
- M2 imports real consumers before core stabilization.
- M3 proves the minimal direct trust path.
- M4 promotes only earned abstractions.
- Context and OpenSpec can progress after the trust path is coherent.
- CI and host qualification depend on stable enough identity/evidence semantics.
- broader gates come after gate claim semantics exist.
- productization comes after the safety boundaries are real.
- advanced RigYard proposals are reconciled after the minimum platform exists.
- 1.0 is a qualification/simplification milestone, not a feature-accumulation milestone.

---

# 20. Progressive package rules

For every milestone package:

```text
references/
llms.txt
manifest.jsonl
```

must remain internally valid.

Each package revision must add a short revision record containing:

```text
milestone
accepted changes
rejected/deferred changes
source versions checked
verification run
verification result
known gaps
next allowed milestone
```

Never label a package with the next milestone revision until the previous milestone verification is complete.

When a primary external source changes materially during the sequence:

1. mark the dependent claim stale;
2. recheck only affected milestones;
3. do not restart unrelated verified work;
4. update source provenance;
5. rerun the minimum relevant adversarial fixtures.

---

# 21. Stop conditions

Pause progression when any of these occurs:

```text
P0 trust invariant cannot be specified deterministically
required source history unavailable for an import milestone
native host evidence contradicts a capability claim
OpenSpec compatibility behavior invalidates authority semantics
CI cannot prove same-subject obligation completeness
a new mechanism cannot identify a distinct failure it solves
two modules claim ownership of the same authoritative state
verification mutates the state it claims to certify without a fresh cycle
```

The correct response is `BLOCKED` or `REWORK`, not a weaker fallback disguised as success.

---

# 22. Features deliberately excluded from this progressive plan

Unless future field evidence reopens them:

```text
vector database
embeddings
hosted RAG
generic scheduler/queue/daemon
distributed lock service as a general platform
central model/pricing catalog
generic telemetry platform
mandatory multi-agent pipeline
OpenSpec fork/parser/Store implementation
new test framework
public plugin marketplace
universal cloud control plane
second canonical Context/evidence store
```

This exclusion is a design constraint, not merely a scheduling choice.

---

# 23. Definition of plan completion

This progressive remediation plan is complete when:

1. every r7 reviewer P0/P1 finding has an explicit source-audited disposition;
2. every current RigYard active OpenSpec change has an explicit Harness Rig disposition;
3. all accepted trust changes have adversarial verification;
4. all deferred features have a concrete evidence trigger;
5. the package's own KB passes the same integrity rules it specifies;
6. no core abstraction exists solely because future consumers might need it;
7. the final roadmap represents the smallest supported 1.0 rather than the union of every source project's ambitions.
