## 1. Dispositions and field evidence

- [x] 1.1 M11-T01–T07: Inventory every active RigYard proposal and record exactly one KEEP, ADAPT, REPLACE, DELETE, or DEFER disposition with evidence and a trigger for deferred work; verify against the proposal inventory that none are missing or duplicated. Evidence: verification/m11-rigyard-dispositions.json records 8 of 8 active proposals exactly once with triggers.
- [ ] 1.2 M11-T08: Record native Claude capability evidence only after checking Codex remains operational as the primary host; verify the retained host report separates observed, unavailable, and untested capabilities.
- [ ] 1.3 M11-T09: Run representative authorized Codex Desktop/CLI field
  pilots, retain trust-outcome and harness-cost observations, and record
  unavailable host actions as BLOCKED; verify each pilot record includes
  environment, task, outcome, and evidence links. The single Desktop task has
  a measured 133-test run; the bounded CLI-agent attempt failed with Windows
  socket error 10013 and unreachable HTTPS fallback. Model identity/token cost
  remain unavailable.
- [ ] 1.4 M11-V04: Use pilot evidence to remove or downgrade mechanisms with no distinct value; verify the final disposition list and resulting product diff agree.

## 2. Source-history qualification and import

- [x] 2.1 M11-T10: Copy the three complete, read-only source bundles into `verification/m11-source-bundles/`; verify origin, main SHA, all advertised refs, bundle digest, and full fsck using `verification/m11-history-input-preflight.py`. Preserve the previous external-bundle report as provenance and generate a repository-relative current report. Evidence: `verification/m11-source-bundle-manifest.json` and `verification/m11-history-input-preflight-current.json`.
- [x] 2.2 M11-T11: Add full AIBoarding, TacticSwitch, and Skill Kit source submodules at their approved legacy prefixes, pinned to the audited source main SHAs. Verify all original histories/tags remain unchanged and preserve old rewrite reports only as superseded experiments. Evidence: `.gitmodules`, `verification/m11-history-import-spec.json`, and bundle preflight.
- [x] 2.3 M11-T12: Replace the rewritten-SHA crosswalk in `CHANGELOG.md` with source repository, full-ref inventory, exact gitlink pin, and bundle evidence. Resolve or explicitly disposition every source ref/tag and changelog discrepancy. Evidence: `verification/m11-changelog-reconciliation.json`.
- [x] 2.4 M11-T13: Run legacy checks against source-native checkouts. Preserve
  TacticSwitch's raw failure and verify its one-file manifest patch on a
  disposable copy. Keep AIBoarding's five-file test-portability patch separate
  from source history. The user-provided native PowerShell run passed the full
  suite with the patch, which applies to the pinned bundle checkout. Evidence:
  `verification/m11-legacy-check-results.json`,
  `verification/m11-tacticswitch-adapter-verification.json`, and
  `verification/m11-aiboarding-test-adapter-verification.json`.
- [x] 2.5 M11-T13: Create the one-parent aggregate import-only commit with only
  `.gitmodules` and the three gitlinks; verify each pin against the bundle.
  Commit `e9ce36ffe47598cbe9367035230794ad5cf3bb5a` passed verification.
- [x] 2.6 M11-T14: Inventory imported licenses, state, hooks, install/update
  surfaces, generated files, schemas, tests, CI, OpenSpec, host manifests,
  tags, and signatures; verify every surfaced category has an explicit
  retain, adapt, replace, or historical-only disposition. The three pinned
  source-main inventories and category dispositions are in
  `verification/m11-source-repository-inventory/` and
  `verification/m11-imported-surface-dispositions.json`. All 21 source tag
  objects and the retained upstream verification for 25 signed commits match
  the tracked bundles; local trust revalidation remains unavailable. Prior
  rewrite inventories are superseded evidence.
- [x] 2.7 M11-V05: Verify the one-parent import commit changes only
  `.gitmodules` and the expected gitlinks, each pinned to the exact source main
  object. The import-only verifier passed; full bundle inventory is separate.
- [x] 2.8 M11-V06: Retain source and adapted legacy-check reports plus the
  import-only verification. Keep M11 BLOCKED while required gates remain
  unavailable; field qualification status is in
  `verification/m11-history-qualification-status.json`.
- [x] 2.9 M11-V07: Reconcile `CHANGELOG.md` against exact source refs, gitlink pins, and bundle evidence; resolve or explicitly record every discrepancy. Evidence: `verification/m11-changelog-reconciliation.json`.
- [x] 2.10 M11-V08: Verify retained upstream signature results against the exact signature-bearing commit objects in the bundles, verify all tag object IDs, and reconcile license, state, hook, install, and host surfaces. Record local trust limitations; block if authoritative signature evidence or source-object matching fails. Evidence: `verification/m11-source-signature-verification.json` and `verification/m11-imported-surface-dispositions.json`.

## 3. M11 qualification decision

- [x] 3.1 M11-V01–V02: Verify every active RigYard proposal has exactly one evidence-backed disposition and every deferred item has an observable trigger. Validation: 8 unique proposal IDs and 8 recorded triggers in verification/m11-rigyard-dispositions.json.
- [x] 3.2 M11-V03: Verify field-pilot evidence reports trust outcomes and harness cost, or retain a precise BLOCKED record for unavailable pilots. `verification/m11-codex-field-pilot.json` satisfies the BLOCKED-record branch only; M11-T09 remains incomplete.
- [x] 3.3 Final gate: Update verification/m11-history-qualification-status.json and ROADMAP.md from retained evidence; set M11 PASS only when all required criteria pass, otherwise record the exact blockers and keep M12 ineligible. Current result: BLOCKED; evidence is recorded in verification/m11-history-qualification-status.json.
