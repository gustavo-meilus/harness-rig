## Why

The initial independent M12 review found a fail-open verifier: it could report PASS for blocked or unvalidated records. A follow-up local patch then embedded M7 obligation JSON, but those files can be fabricated locally and do not establish hosted acceptance. Release eligibility must be tied to GitHub's live Actions run and required job for the exact source revision.

## What Changes

- Keep release-record/v2, but remove embedded M7 obligation/result objects as eligibility evidence.
- Bind the record to explicit GitHub OWNER/REPO, repository ID, workflow run ID, current attempt, `ci / required` job ID, source SHA, and artifact hashes.
- Query GitHub read-only through the installed `gh api` CLI during record creation and verification. Missing access or mismatches produce BLOCKED, never PASS.
- Report artifact integrity and hosted CI independently; overall PASS requires both.
- Retain rejection of v1 and BLOCKED records. Keep live ruleset and required-check source observation as a separate M12 gate.
- Eligible v2 records remain unsigned CANDIDATEs until a protected GitHub Actions workflow attests the exact record bytes. Verification requires that external attestation as well as artifact and hosted-CI checks.

## Capabilities

### Modified Capabilities

- `release-provenance`: release acceptance requires authenticated live GitHub Actions evidence.

## Impact

Affected code includes `prototype/harness_rig/release.py`, `verification/release_provenance.py`, the M10 release test module, and a protected manual GitHub Actions attestation workflow. Documentation and M12 evidence will preserve the original review failures and mark the current fix review pending. No push, release publication, or upstream history change is included.
