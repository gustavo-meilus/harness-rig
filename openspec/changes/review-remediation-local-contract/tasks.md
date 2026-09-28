# Review remediation tasks

## 1. Contract

- [x] 1.1 Validate the revised local, CI, and provenance delta specs with
  `openspec validate --strict` and keep M12 qualification marked REWORK.

## 2. Local product paths

- [x] 2.1 Remove grant issuance and authorized verdicts from `verify` and
  `direct`; verify focused CLI tests report local gate evidence only.
- [x] 2.2 Require explicit local archive confirmation and retain readiness,
  exact-state, and postcondition checks without grant issuance; verify archive
  negative and success tests.
- [x] 2.3 Clarify the retained grant schema's validation boundary and verify
  no local CLI path can report an authorization-bearing merge/archive verdict.

## 3. Repository CI

- [x] 3.1 Replace obligation resolution with unconditional ordinary and KB
  jobs plus a final native-results check; verify failure, skip, fork, and
  merge-group workflow cases.
- [x] 3.2 Remove unused resolver/policy code and update structural tests;
  verify no active production caller remains.
- [x] 3.3 Pin consequential Actions to reviewed full SHAs and verify all
  workflow `uses:` references resolve to full commits.

## 4. Provenance and identity

- [x] 4.1 Implement v3 `source_revision` release records and v1/v2 rejection
  for new releases; verify record and summary tests.
- [x] 4.2 Preserve exact-byte attestation, hosted-run, and artifact checks;
  verify wrong-source, changed-attempt, and altered-artifact cases.
- [x] 4.3 Reconcile CLI status, README, ROADMAP, live remediation status,
  CHANGELOG, and Context claims; verify one `r8.12` product revision and
  `python verification/context_kb.py audit .`.

## 5. Candidate qualification and release

- [ ] 5.1 Run the canonical suite, OpenSpec validation, migration and host
  checks, M11 source-history verification, and mechanism inventory; retain
  exact commands, results, limits, and candidate SHA.
- [ ] 5.2 Review one clean final candidate and verify its Git bundle can be
  cloned offline with matching tag, source commit, and tracked M11 inputs.
- [ ] 5.3 Verify hosted `ci / required` and ruleset settings for the exact
  candidate, attest the v3 record, verify artifact hashes, and publish the
  `v1.0.0` release only after the revised-scope review passes.
