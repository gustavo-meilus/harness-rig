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

- [x] 2.1 M11-T10: Snapshot AIBoarding, TacticSwitch, and Skill Kit as full Git bundles from read-only source clones; retain source origin, HEAD, shallow status, ref inventory, fsck result, bundle digest, and upstream-ref comparison where accessible; run python verification/m11-history-input-preflight.py --dir <inputs-dir> --json and require PASS for each source before import. Evidence: verification/m11-history-input-preflight-current.json; complete bundles include all public branches, tags, and advertised pull-request heads.
- [x] 2.2 M11-T11: Run python verification/m11-run-history-imports.py --inputs-dir <inputs-dir> --work-dir <work-dir> --output-dir <output-dir>; retain each commit/ref/tag map and independent rewrite report, and verify rewritten trees and parent topology with verification/m11-verify-rewrite.py. Evidence and maps: verification/m11-history-maps/. Rewritten bundles are staged only in namespaced refs; import-only commits remain gated.
- [x] 2.3 M11-T12: Reconcile source-to-rewritten commit and tag maps with CHANGELOG.md; retain a discrepancy report and verify every source ref/tag is mapped or explicitly dispositioned. Evidence: CHANGELOG.md M11 crosswalk and verification/m11-changelog-reconciliation.json; all 122 commits, 20 branch/PR refs, and 21 tags are mapped, with fidelity and TacticSwitch gate discrepancies recorded as blockers.
- [x] 2.4 M11-T13: Run python verification/m11-verify-reproducibility.py --inputs-dir <inputs-dir> --json and relevant discovered legacy checks; verify two rewrite runs produce equivalent maps and reports, and report unavailable checks as BLOCKED. Reproducibility passed; AIBoarding and Skill Kit checks passed; TacticSwitch failed 1/200 because MANIFEST.sha256 is stale. See verification/m11-legacy-check-results.json. The checks were executed and the failure is recorded; this does not pass the import gate.
- [ ] 2.5 M11-T13: Stage verified output bundles with python verification/m11-fetch-import-bundles.py --target-repo . --imports-dir <output-dir>; create separately reviewable import-only commits under approved legacy prefixes and verify each with verification/m11-verify-import-only.py.
- [ ] 2.6 M11-T14: Inventory imported licenses, state, hooks, install/update
  surfaces, generated files, schemas, tests, CI, OpenSpec, host manifests,
  tags, and signatures; verify every surfaced category has an explicit
  retain, adapt, replace, or historical-only disposition. Partial evidence:
  `verification/m11-imported-surface-dispositions.json` inventories staged
  main-tip trees and dispositions each category; all 21 source tag objects were
  confirmed in the available bundles, but local commit-signature verification
  is blocked by host trust configuration and rewritten signature/tag fidelity
  remains blocked. See `verification/m11-object-fidelity-audit.json`.
- [x] 2.7 M11-V05: Retain reproducibility, tree-equivalence, parent-topology, and source-ref mapping reports; require all verifiers to pass before accepting imports.
- [x] 2.8 M11-V06: Retain legacy-check and import-only reports; mark M11 BLOCKED if any required check fails or cannot run. Evidence: `verification/m11-import-only-status.json` records import-only verification as NOT_RUN because no import-only commits were created; M11 remains BLOCKED.
- [x] 2.9 M11-V07: Reconcile CHANGELOG.md against source histories and retained maps; verify every discrepancy is resolved or explicitly recorded. Evidence: verification/m11-changelog-reconciliation.json; signature, tag-object, and TacticSwitch gate gaps remain explicitly open.
- [x] 2.10 M11-V08: Retain license, state, hook, install, tag, annotation, and signature provenance; explicitly block if required fidelity cannot be demonstrated. Evidence: `verification/m11-imported-surface-dispositions.json` and `verification/m11-object-fidelity-audit.json`; fidelity remains explicitly BLOCKED.

## 3. M11 qualification decision

- [x] 3.1 M11-V01–V02: Verify every active RigYard proposal has exactly one evidence-backed disposition and every deferred item has an observable trigger. Validation: 8 unique proposal IDs and 8 recorded triggers in verification/m11-rigyard-dispositions.json.
- [x] 3.2 M11-V03: Verify field-pilot evidence reports trust outcomes and harness cost, or retain a precise BLOCKED record for unavailable pilots. `verification/m11-codex-field-pilot.json` satisfies the BLOCKED-record branch only; M11-T09 remains incomplete.
- [x] 3.3 Final gate: Update verification/m11-history-qualification-status.json and ROADMAP.md from retained evidence; set M11 PASS only when all required criteria pass, otherwise record the exact blockers and keep M12 ineligible. Current result: BLOCKED; evidence is recorded in verification/m11-history-qualification-status.json.
