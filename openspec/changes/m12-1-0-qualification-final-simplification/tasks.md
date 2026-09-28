## 1. Deterministic qualification

- [x] 1.1 Record the M12 baseline revision and verify the three audited source
  gitlink pins are unchanged.
- [x] 1.2 Run `python -m unittest prototype.tests.test_m3_vertical_slice` for
  the P0 trust fixtures; retain the result.
- [x] 1.3 Run `python -m unittest prototype.tests.test_m6_openspec_spec_engine`
  and strict validation of this OpenSpec change; retain both results.
- [x] 1.4 Bind the passing M7 enforcement suite and local CI obligation
  resolution to M12 commit `978c361def2d2805951fd044aa82dedc73160bc4`.
  The accepted hosted verdict remains task 2.2.
- [x] 1.5 Run `python -m unittest prototype.tests.test_m9_gate_platform` and
  `python -m unittest prototype.tests.test_m10_product_cli_migration_release`;
  retain the results.
- [x] 1.6 Run `python scripts/check.py` after all evidence and Context updates;
  record suite counts, Context audit, projection status, and diff check.

## 2. Host and release evidence

- [x] 2.1 Run `harness-rig doctor --json-v1` on the current Windows host and
  retain only observed `local-subprocess` capabilities.
- [x] 2.2 Obtain an accepted hosted `ci / required` verdict bound to the exact
  M12 source revision. Run `36365911407` passed on source revision
  `0b1ebfcae75c7fe665e08b25996cf8ae3c4d709d`; ruleset enforcement was later
  confirmed on `main` and exercised by PR 1.
- [x] 2.3 Run the missing-verdict release smoke and retain its fail-closed
  result. The accepted-verdict path is conditional on 2.2 and remains unrun;
  tamper rejection is covered by the M10 release-provenance suite.
- [x] 2.4 Trace M12 release-provenance evidence to the behavior contract in
  `release-provenance-fail-closed`; verify its strict OpenSpec validation and
  focused test evidence without duplicating its requirements.

## 3. Final reviews and decision

- [x] 3.1 Complete a fresh independent architecture review of the final
  package. The review of published revision
  `11e43e1477c366ca570a1c4cbd2f75f9e668f429` reported no source findings.
- [x] 3.2 Complete the feature-retirement review and retain each final
  mechanism disposition with its evidence or reopening trigger.
- [x] 3.3 Verify M12-V01: no unresolved P0/P1 issue invalidates a 1.0 claim.
  The fresh independent source review reported no findings; hosted CI,
  required-check enforcement, and the protected attestation environment were
  observed separately.
- [x] 3.4 Verify M12-V02: the supported trust invariant holds end to end and
  unsupported capabilities fail closed.
- [x] 3.5 Verify M12-V03: the final product is smaller than the union of
  imported and planned systems; record the comparison.
- [x] 3.6 Create `verification/m12-verification-record.json` with each task,
  verifier outcome, source revision, evidence path, limitations, and final
  `PASS` or precise `BLOCKED` result; update roadmap and execution projections.
