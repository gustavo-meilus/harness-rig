# Harness Rig execution roadmap

**Current revision:** r8.12 checkpoint `978c361def2d2805951fd044aa82dedc73160bc4`
**Completed:** M0-M12 PASS, with the limits recorded below.
**Next:** Prepare and inspect a real candidate before any future attestation.
V04 passed; Claude is out of scope for now.
**Final planned qualification:** M12 / 1.0

This root file is the Git/Codex execution projection requested for the repository handoff. The detailed milestone source of truth remains `PROGRESSIVE_REMEDIATION_PLAN.md`; durable architecture knowledge remains under `references/` and is indexed by `llms.txt`.

## Operating priorities after Git transformation

- Codex Desktop/CLI is the **primary operational and native-qualification target**.
- Claude Code native qualification is **out of scope for now** and is not an
  M11 or M12 gate.
- OpenSpec is the first-class external specification workflow for remaining changes; do not build a second spec/planning framework.
- Apply Adaptive Engineering Harness discipline: inspect before editing, keep scope bounded, verify executable behavior, report only observed evidence, and fail closed when a required capability is absent.
- Apply More With Less: delete/reuse before adding, deterministic/native mechanisms before orchestration, one agent/direct path by default, and no new subsystem without a concrete failure that earns it.
- Do not reopen M0-M10 unless a regression or contradictory retained evidence requires it.
- Do not claim original Git provenance from the reconstructed Harness Rig milestone commits. They are synthetic reconstruction commits from verified snapshots.

## Milestone ledger

### M0 / r8.0 - Corpus repair and source baseline - PASS

Completed:
- repair YAML front matter and canonical metadata schema;
- deterministic `manifest.jsonl` generation;
- source provenance refresh for More With Less, Skill Kit KB, OpenSpec, and RigYard;
- stale RigYard assumptions repaired;
- stale handoff/state files classified as historical evidence.

Verified:
- canonical YAML parsing;
- IDs/links/`llms.txt`/manifest integrity;
- byte-identical manifest regeneration;
- active RigYard change/evidence maturity inventory.

### M1 / r8.1 - Trust protocol ADRs - PASS

Completed:
- `StateIdentity`, bounded `AuthorizationGrant`, `EvidenceReceipt`, and action-qualified `AcceptanceVerdict` ADRs;
- canonical security/trust boundary;
- 16 P0 known-bad fixtures.

Verified:
- state/revision/content edge cases;
- expiry/delegation/state-binding failures;
- receipt replay/forgery/version/artifact-integrity failures;
- path traversal/symlink/executable spoofing failures.

### M2 / r8.2 - CHANGELOG-backed source consolidation - PASS

Completed:
- source baselines and ownership/dispositions for AIBoarding, TacticSwitch, Skill Kit KB maintainer, and Adaptive Engineering Harness;
- migration-surface inventory;
- KEEP / ADAPT / REPLACE / DELETE_AFTER_MIGRATION / HISTORICAL_ONLY classifications.

Verified:
- source/capability traceability in `CHANGELOG.md`;
- no invented unavailable evidence;
- full Git-history qualification explicitly deferred to M11;
- licenses/state/hooks/install/generated/schema/test/CI/OpenSpec/agent surfaces inventoried.

### M3 / r8.3 - Thin complete Experimental vertical slice - PASS

Completed executable direct path:
`Direct Authority -> Assurance -> direct Topology -> command gate -> Experimental EvidenceReceipt -> Experimental AcceptanceVerdict`.

Verified 22 tests plus all M1 P0 fixtures, including state mutation, wrong-run/replay rejection, authorization BLOCKED behavior, required NOT_RUN rejection, artifact tampering, protected-path security, and action-qualified acceptance.

### M4 / r8.4 - Core promotion and module-boundary convergence - PASS

Promoted:
- Stable `AuthorityRef` v1 provider-neutral invariant;
- Stable bounded `AuthorizationGrant` v1;
- Stable `StateIdentity` v1.

Kept Experimental/local:
- `EvidenceReceipt`;
- `AcceptanceVerdict`;
- `AssurancePlan`, execution/topology plan shape, Context internals, `RuntimeResolution`, recurrence state, `ContextManifest`.

Verified explicit schema/version/migration/failure semantics and Assurance/Topology non-bypass boundaries.

### M5 / r8.5 - Context convergence and canonical knowledge lifecycle - PASS

Completed:
- canonical KB as sole durable project-knowledge owner;
- Context lifecycle as projection owner only;
- stable-ID rename/move/split/merge/retirement semantics;
- provenance/source freshness/reconciliation;
- deterministic manifest, whole-collection audit, root `AGENTS.md` projection.

No vector/embedding/RAG subsystem was introduced.

### M6 / r8.6 - OpenSpec first-class external SpecEngine - PASS

Completed:
- bounded external `OpenSpecAdapter` and Experimental `SpecEngine`;
- authority fingerprint profile excluding task bookkeeping while binding behavior-bearing artifacts/context/rules/referenced specs;
- fail-closed OpenSpec health/config/reference checks;
- guarded `spec archive` using existing Assurance/Authorization/Acceptance semantics.

Current compatibility baseline: OpenSpec 1.13.2. OpenSpec remains optional to base Harness Rig and external to core.

### M7 / r8.7 - Trusted repository enforcement - PASS

Completed:
- deterministic CI obligation artifact;
- strict same-subject `ci / required` validation;
- merge-group support;
- unprivileged fork PR boundary;
- governance-sensitive workflow/resolver/policy/oracle surfaces.

Remote GitHub ruleset/CODEOWNERS installation remains deployment state, not locally fabricated evidence.

### M8 / r8.8 - Host capability and topology qualification - PASS

Qualified Stable host:
- `local-subprocess` for clean process, process launch, runtime identity observation, and crash reconciliation only.

Still unsupported/unqualified on that adapter:
- fresh verifier;
- read-only worker;
- isolated/worktree worker;
- permission enforcement;
- isolated writer.

`CapabilitySet` and `RuntimeResolution` remain Experimental/module-owned.

### M9 / r8.9 - Gate platform, Playwright, architecture, mutation verification - PASS

Completed:
- Experimental provider-neutral `GateClaim` / `GateOutcome`;
- AST architecture gate;
- strict Playwright JSON/runtime provider semantics;
- bounded development mutation verification;
- invariant -> mutant -> detector mapping with red/green sensitivity evidence.

No generic gate registry, browser farm, mutation platform, or telemetry platform was added.

### M10 / r8.10 - Product CLI, migration completion, release provenance - PASS

Completed:
- compact product CLI: `init`, `doctor`, `spec status`, guarded `spec archive`, `verify`, `status`, `migrate`;
- `harness-rig/cli-envelope/v1` and explicit exit categories;
- config precedence defaults < user-global < project < CLI, with global policy weakening forbidden;
- process-group timeout/cancellation cleanup;
- atomic r8.9 -> r8.10 runtime/schema migration and rollback;
- deterministic synthetic history-map semantics without pretending M11 source maps exist;
- immutable release-record/checksum provenance with hosted repository verdict required for release eligibility.

M11 field and source-history qualification passed. The canonical repository
check passed 139 tests across nine modules; Context audit passed 44/44 and the
root projection is fresh. See
`verification/m11-history-qualification-status.json`.

## M11 / r8.11 - History, field hardening, and RigYard disposition - PASS

Execute in this exact milestone only:

- [x] **M11-T01** Disposition v0.3 isolated writers.
- [x] **M11-T02** Disposition harness mutation verification.
- [x] **M11-T03** Disposition v0.4 approved revision/traceability requirements.
- [x] **M11-T04** Disposition v0.5 static composition.
- [x] **M11-T05** Disposition v0.6 richer topology families.
- [x] **M11-T06** Disposition v0.7 distributed execution.
- [x] **M11-T07** Disposition v0.8 observability/effects.
- [x] **M11-T08** Claude native qualification is out of scope for now per
  user direction; it is not an M11 acceptance gate.
- [x] **M11-T09** Complete representative Codex Desktop/CLI field pilots and
  qualification with recorded limits. See
  `verification/m11-codex-field-pilot.json`.
- [x] **M11-T10** Obtain and validate object-complete AIBoarding, TacticSwitch, and Skill Kit histories.
- [x] **M11-T11** Add full source-native submodules under the approved prefixes at audited main commits; retain complete bundles and all source refs.
- [x] **M11-T12** Replace the rewritten-SHA crosswalk with exact source pins and bundle evidence; reconcile every ref, tag, and discrepancy in `verification/m11-changelog-reconciliation.json`.
- [x] **M11-T13** Retain raw source checks and the separate TacticSwitch
  one-file adapter result. AIBoarding's full patched suite and both runtime
  probes pass with workspace-local temporary files. The earlier sandbox
  failures came from Git Bash's user-profile temp path. See
  `verification/m11-legacy-check-results.json`.
- [x] **M11-T14** Inventory pinned source surfaces and disposition categories; verify exact source signature/tag objects against bundle evidence. See `verification/m11-source-repository-inventory/`, `verification/m11-imported-surface-dispositions.json`, and `verification/m11-object-fidelity-audit.json`.

Required verification:

- [x] **M11-V01** Every active RigYard proposal has exactly one Harness Rig disposition.
- [x] **M11-V02** Deferred features have explicit evidence triggers.
- [x] **M11-V03** Field-pilot evidence records authorized read-only and
  implementation pilots, outcomes, costs, and limits. See
  `verification/m11-codex-field-pilot.json`.
- [x] **M11-V04** In-scope proposals with no distinct value are deferred or
  kept optional. Bounded mutation verification remains for its distinct
  detector-gap evidence. No product code was added in the M11 diff from
  `2cd4cf2`; see `verification/m11-rigyard-dispositions.json`.
- [x] **M11-V05** Verify the single aggregate import-only commit changes only `.gitmodules` and the three exact source gitlinks. Commit `e9ce36ffe47598cbe9367035230794ad5cf3bb5a` passed; see `verification/m11-import-only-status.json`.
- [x] **M11-V06** Legacy failures and passing import-only verification are
  retained; all M11 acceptance gates have evidence. See
  `verification/m11-history-qualification-status.json`.
- [x] **M11-V07** `CHANGELOG.md` reconciles with actual source history; discrepancies are resolved or explicit. Evidence: `verification/m11-changelog-reconciliation.json`.
- [x] **M11-V08** Retained upstream signature verification matches exact bundled source commit objects; all source tag objects are inventoried. Local GPG/SSH revalidation limits are recorded.

M11 disposition defaults from the current plan:
- isolated writers: optional Topology capability, not default, not Stable without formal native evidence;
- mutation verification: keep as bounded development/field-hardening gate if it catches a distinct failure;
- persistent approved plan/revision traceability: admit only when a real persisted execution-plan product requires it;
- static composition: defer/earned; must compile away before approval/runtime if ever admitted;
- richer topology families: defer post-1.0 unless independently earned;
- distributed execution: defer post-1.0 unless a real cross-host workflow requires it;
- observability: retain only minimal diagnostic/audit observability; no telemetry platform;
- external-effect workflow platform: defer unless intentionally required;
- Claude native qualification: out of scope for now; reopen only after an explicit scope decision.

M11 full Git-history gate sequence:

```text
validate complete source bundles and ref inventories
-> pin source-native submodules at audited main commits
-> verify original commit signatures and tag objects against bundle evidence
-> inventory and disposition source operational surfaces
-> run raw legacy checks and any separately reviewed adapters
-> create and prove the single aggregate import-only commit
-> reconcile migration surfaces and CHANGELOG.md
-> complete Codex field qualification and V04 review
```

If required source history is unavailable or unverifiable: **M11 = BLOCKED and M12 cannot PASS.**

## M12 / r8.12 - 1.0 qualification and final simplification - PASS

Execution is in progress from baseline `bccbfcb7c4d03df843d7bc5a1a87a343d0b6c7d7`; checkpoint commit `978c361def2d2805951fd044aa82dedc73160bc4` retains the current evidence. See `verification/m12-verification-record.json` for exact results and limits.

Execution:
- [x] M12-T01 canonical deterministic suite: `python scripts/check.py` passes
  151 tests across nine milestone modules, Context audit (44 pages/rows), fresh
  projection, and `git diff --check`. The suite verifies canonical fingerprints
  are independent of LF/CRLF checkout line endings;
- [x] M12-T02 Context audit, byte-identical manifest, and fresh projection;
- [x] M12-T03 all P0 adversarial trust fixtures;
- [x] M12-T04 OpenSpec compatibility fixtures and strict change validation;
- [x] M12-T05 M7 CI obligation suite and local exact-SHA obligation resolution pass;
- [x] M12-T06 retained `local-subprocess` native evidence; Codex adapter unqualified;
- [x] M12-T07 gate-provider adversarial suite;
- [x] M12-T08 migration upgrade/rollback fixtures;
- [x] M12-T09 29 mocked hosted-API and attestation tests, including recomputed-
  digest tampering, dispatch limits, metadata validation, summary escaping, and
  workflow permission/environment controls;
- [x] M12-T10 fresh independent source review of published revision
  `11e43e1477c366ca570a1c4cbd2f75f9e668f429` passed with no source findings;
  earlier FAIL results remain preserved in the review record;
- [x] M12-T11 final feature-retirement review recorded.

Verification:
- [x] M12-V01 hosted `ci / required` passed on exact source revision
  `0b1ebfcae75c7fe665e08b25996cf8ae3c4d709d`, and independent source review
  passed on final published revision `11e43e1477c366ca570a1c4cbd2f75f9e668f429`;
  the active main ruleset requires the GitHub Actions check, and the protected
  attestation environment is configured with the solo project owner as reviewer;
- [x] M12-V02 supported trust invariant is demonstrably true within retained capability limits;
- [x] M12-V03 all eight retained proposal dispositions remain valid; no deferred feature mechanism was added.

M12 PASS records qualification of the product and its external enforcement
configuration; it does not claim that a release was signed or attested. Original
and follow-up FAIL reviews, later corrections, and review scope are recorded in
`verification/m12-independent-review.json` and
`verification/m12-verification-record.json`. The provenance record now requires
an exact-byte GitHub artifact attestation, validates live hosted CI including
the jobs count, and uses one captured byte snapshot for both verification and
dispatch. Artifact metadata is validated before it appears in the protected
approval summary. The companion release-provenance change is the bounded
product-change exception in the M12 proposal, design, and tasks.

The first public CI run on `2c7d59e` failed because the Context fingerprint
included checkout line endings: Windows generated CRLF while GitHub Actions
checked out LF. Commit `0b1ebfcae75c7fe665e08b25996cf8ae3c4d709d` normalizes line
endings before hashing and adds a regression test. `python scripts/check.py`
passed 151 tests, and hosted `ci / required` passed for that exact revision in
run `36365911407`. A fresh independent review of published revision
`11e43e1477c366ca570a1c4cbd2f75f9e668f429` found no source findings; it did not
independently query GitHub for CI or repository settings. An active repository
ruleset now applies to `main` and requires `ci / required` from GitHub Actions
integration `15368`, with no bypass actors. PR 1 passed that required check and
merged; the merge commit's main workflow run also passed. The classic
branch-protection endpoint returns 404 because enforcement is via the
ruleset. The
`release-provenance-attestation` environment now requires approval by the
repository owner, allows owner self-review, blocks administrator bypass, and
only permits protected branches. This is a personal-project approval gate, not
separation of duties. No release candidate was supplied, so no attestation was
dispatched. The source history is published at
`https://github.com/gustavo-meilus/harness-rig`.

1.0 requires stable canonical Context knowledge, exact evidence, OpenSpec integration, at least one genuinely Stable host, trusted repository enforcement, safe migration/release provenance, successful M11 history qualification, and final complexity retirement.

Not required for 1.0 unless newly earned: generic recurrence, adaptive model/effort optimization, all hosts Stable, shared OpenSpec Store backbone, static composition, richer topology families, distributed execution, external-effect platform, public plugin SDK/marketplace, generic telemetry, or vector/embedding/RAG infrastructure.

## Git reconstruction note

The handoff can reconstruct exact verified **r8.3-r8.10 package states** plus the matching progressive-plan state. Standalone r8.0-r8.2 package snapshots are not present. Therefore the first Git commit is an explicit consolidated `M0-M3 / r8.3` reconstruction baseline, followed by one exact snapshot commit per M4-M10. Do not split M0, M1, or M2 into invented historical trees.
