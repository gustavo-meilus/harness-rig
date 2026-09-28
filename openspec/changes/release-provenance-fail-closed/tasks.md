## 1. Hosted release acceptance

- [x] 1.1 Replace embedded M7 eligibility payloads with v2 repository ID, run ID, current attempt, required job ID, source SHA, and artifact hashes.
- [x] 1.2 Implement authenticated read-only `gh api` lookup at record creation and verification; fail closed on missing access, mismatch, malformed or truncated responses, and reruns.
- [x] 1.3 Return separate artifact-integrity and hosted-CI results; overall PASS requires both; reject v1 and BLOCKED records.
- [x] 1.4 Replace synthetic-proof tests with offline mocked GitHub API cases for valid acceptance, repository/SHA/workflow/event/branch/job/attempt mismatches, unsuccessful/unavailable runs, blocked/v1 records, and tampering.

## 2. Documentation and M12 evidence

- [x] 2.1 Update CLI documentation and canonical release/governance references; refresh Context projections and audit if canonical references change.
- [x] 2.2 Preserve the original independent-review FAIL and mark review of the new source pending; retain hosted CI and enforcement as separate external gates; preserve audited legacy pins.
- [x] 2.3 Run focused release tests, strict OpenSpec validation, Context audit/projection checks, `python scripts/check.py`, and `git diff --check`.

## 3. Trusted record anchor

- [x] 3.1 Change eligible records to unsigned CANDIDATE status; parse one
  captured record-byte snapshot and verify the same bytes with `gh attestation
  verify`; require artifact integrity, hosted CI, and attestation for overall
  PASS.
- [x] 3.2 Add the protected manual attestation workflow with candidate/live-CI validation, reviewer-visible artifact summary, exact-byte handoff, narrowly scoped job permissions, and required environment.
- [x] 3.3 Add `attest` dispatch CLI with explicit repository, exact JSON input, and 60,000-byte serialization cap; document the signer workflow and guarantee limits.
- [x] 3.4 Test valid/missing/invalid/scoped attestations, recomputed-digest
  tampering, record-path mutation during verify and dispatch, dispatch
  size/serialization, workflow policy, and existing API and artifact cases
  without network access.
- [x] 3.5 Update M12 review and verification evidence, roadmap, and canonical
  references; preserve audited legacy pins and carry forward M12's final
  evidence-based result. M12 is now recorded as PASS with limits after its
  qualification gates passed.
- [x] 3.6 Run focused tests, strict OpenSpec validation, Context audit/projection, `python scripts/check.py`, and `git diff --check`.
- [x] 3.7 Validate artifact path, non-negative integer size, and 64-character
  SHA-256 before signing. Use a tested renderer that safely encodes every
  record-derived approval-summary value; offline tests reject malformed
  metadata and Markdown injection.
