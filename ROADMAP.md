# Harness Rig execution roadmap

**Current verified revision:** r8.10  
**Completed:** M0-M10 PASS  
**Next:** M11-T01  
**Final planned qualification:** M12 / 1.0

This root file is the Git/Codex execution projection requested for the repository handoff. The detailed milestone source of truth remains `PROGRESSIVE_REMEDIATION_PLAN.md`; durable architecture knowledge remains under `references/` and is indexed by `llms.txt`.

## Operating priorities after Git transformation

- Codex Desktop/CLI is the **primary operational and native-qualification target**.
- Claude Code is the **secondary platform** and is qualified after the Codex path is genuinely operational.
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

Verified 133/133 tests through M10. Full source-history qualification remains `PENDING_M11`.

## M11 / r8.11 - RigYard disposition, source-history qualification, field hardening - NEXT

Execute in this exact milestone only:

- [ ] **M11-T01** Disposition v0.3 isolated writers.
- [ ] **M11-T02** Disposition harness mutation verification.
- [ ] **M11-T03** Disposition v0.4 approved revision/traceability requirements.
- [ ] **M11-T04** Disposition v0.5 static composition.
- [ ] **M11-T05** Disposition v0.6 richer topology families.
- [ ] **M11-T06** Disposition v0.7 distributed execution.
- [ ] **M11-T07** Disposition v0.8 observability/effects.
- [ ] **M11-T08** Qualify Claude natively as the secondary host target. Codex is primary and must be operational first.
- [ ] **M11-T09** Run representative field pilots and simplification review, prioritizing Codex Desktop/CLI as the primary real-host path.
- [ ] **M11-T10** Obtain and validate object-complete AIBoarding, TacticSwitch, and Skill Kit histories.
- [ ] **M11-T11** Execute history-preserving rewrite/import into isolated legacy prefixes where required.
- [ ] **M11-T12** Produce reproducible source -> rewritten commit/tag maps and reconcile them against `CHANGELOG.md`.
- [ ] **M11-T13** Run relevant legacy deterministic checks and verify import-only commits/tree equivalence.
- [ ] **M11-T14** Reconcile licenses/state/hooks/install surfaces and signed commit/tag fidelity requirements.

Required verification:

- [ ] **M11-V01** Every active RigYard proposal has exactly one Harness Rig disposition.
- [ ] **M11-V02** Deferred features have explicit evidence triggers.
- [ ] **M11-V03** Field pilots measure trust outcomes and harness cost.
- [ ] **M11-V04** Mechanisms with no distinct value are deleted/downgraded.
- [ ] **M11-V05** History mappings are reproducible and mapped trees/topology match source histories.
- [ ] **M11-V06** Relevant legacy checks and import-only verification pass or produce explicit BLOCKED evidence.
- [ ] **M11-V07** `CHANGELOG.md` reconciles with actual source history; discrepancies are resolved or explicit.
- [ ] **M11-V08** License/state/hook/install/tag/signature provenance is retained or explicitly dispositioned.

M11 disposition defaults from the current plan:
- isolated writers: optional Topology capability, not default, not Stable without formal native evidence;
- mutation verification: keep as bounded development/field-hardening gate if it catches a distinct failure;
- persistent approved plan/revision traceability: admit only when a real persisted execution-plan product requires it;
- static composition: defer/earned; must compile away before approval/runtime if ever admitted;
- richer topology families: defer post-1.0 unless independently earned;
- distributed execution: defer post-1.0 unless a real cross-host workflow requires it;
- observability: retain only minimal diagnostic/audit observability; no telemetry platform;
- external-effect workflow platform: defer unless intentionally required;
- Claude: host-specific secondary qualification; must not block 1.0 if Codex is genuinely Stable.

M11 full Git-history gate sequence:

```text
validate object-complete histories
-> rewrite/import to isolated legacy prefixes
-> generate source->rewritten commit/tag maps
-> verify tree/topology equivalence
-> run relevant legacy deterministic checks
-> prove import-only commits
-> reconcile migration surfaces
-> reconcile CHANGELOG.md against actual history
-> resolve signed commit/tag fidelity requirements
```

If required source history is unavailable or unverifiable: **M11 = BLOCKED and M12 cannot PASS.**

## M12 / r8.12 - 1.0 qualification and final simplification - PENDING M11

Execution:
- [ ] M12-T01 full deterministic repository suite;
- [ ] M12-T02 KB self-validation;
- [ ] M12-T03 all P0 adversarial trust fixtures;
- [ ] M12-T04 OpenSpec compatibility fixtures;
- [ ] M12-T05 CI obligation meta-suite;
- [ ] M12-T06 retained native evidence for at least one Stable host;
- [ ] M12-T07 gate-provider adversarial suite;
- [ ] M12-T08 migration upgrade/rollback fixtures;
- [ ] M12-T09 release provenance smoke;
- [ ] M12-T10 fresh-context architecture review;
- [ ] M12-T11 final feature-retirement review.

Verification:
- [ ] M12-V01 no unresolved P0/P1 issue invalidates 1.0;
- [ ] M12-V02 supported trust invariant is demonstrably true;
- [ ] M12-V03 final product is smaller than the union of imported/planned systems.

1.0 requires stable canonical Context knowledge, exact evidence, OpenSpec integration, at least one genuinely Stable host, trusted repository enforcement, safe migration/release provenance, successful M11 history qualification, and final complexity retirement.

Not required for 1.0 unless newly earned: generic recurrence, adaptive model/effort optimization, all hosts Stable, shared OpenSpec Store backbone, static composition, richer topology families, distributed execution, external-effect platform, public plugin SDK/marketplace, generic telemetry, or vector/embedding/RAG infrastructure.

## Git reconstruction note

The handoff can reconstruct exact verified **r8.3-r8.10 package states** plus the matching progressive-plan state. Standalone r8.0-r8.2 package snapshots are not present. Therefore the first Git commit is an explicit consolidated `M0-M3 / r8.3` reconstruction baseline, followed by one exact snapshot commit per M4-M10. Do not split M0, M1, or M2 into invented historical trees.
