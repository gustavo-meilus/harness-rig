# Release Provenance Specification

## Purpose
Release records bind artifacts to the source revision and an accepted hosted GitHub Actions run for that revision.

## Requirements

### Requirement: Release records require live hosted CI acceptance
Creation MUST mark an eligible release record `CANDIDATE`, never PASS. It MUST bind the GitHub repository ID, workflow run ID, attempt number, required job ID, source SHA, and artifact hashes. Local M7 obligation or result JSON MUST NOT establish hosted acceptance. Candidate eligibility MUST require authenticated `gh api` evidence for the explicit repository and one completed, successful `push` run on `main` for the exact source SHA, from `.github/workflows/ci-required.yml`, with exactly one completed, successful `ci / required` job in the run's current attempt.

#### Scenario: Valid hosted run
- **WHEN** the GitHub API reports the expected repository, exact SHA, required workflow, `push` on `main`, successful completed run, and one matching successful required job
- **THEN** record creation MUST mark it CANDIDATE and persist the repository ID, run ID, attempt, and job ID

#### Scenario: Missing run or unavailable GitHub API
- **WHEN** no run is supplied, the run is unavailable, authentication/API access fails, or the response is malformed
- **THEN** creation MAY persist an immutable BLOCKED candidate and MUST NOT mark it PASS

#### Scenario: Mismatched hosted run
- **WHEN** repository identity, source SHA, workflow, event, branch, run result, attempt, job identity, or job result does not match the requirement
- **THEN** creation MUST produce BLOCKED and MUST NOT mark the record PASS

### Requirement: Verification requires record attestation
The verifier MUST read the record bytes once, parse that snapshot, and use the same bytes for `gh attestation verify` via a private temporary file. It MUST NOT reread the user-selected record path after parsing. It MUST report artifact integrity, hosted CI, and attestation as separate outcomes and MUST report overall PASS only when all three pass. Verification MUST re-fetch the run and jobs for the recorded attempt and reject a rerun that changed the run's current attempt. Attestation verification MUST be scoped to the explicit repository, `.github/workflows/release-record-attestation.yml`, and `refs/heads/main`. V1, BLOCKED, malformed, unavailable, unsigned, or mismatched records MUST NOT report PASS.

#### Scenario: Valid attested release record
- **WHEN** artifact hashes pass, live GitHub data revalidates the recorded repository, run, attempt, source, workflow, event, branch, and job, and the exact record bytes have a valid attestation from the required workflow on main
- **THEN** artifact integrity, hosted CI, attestation, and overall outcomes MUST be PASS

#### Scenario: Unsigned candidate
- **WHEN** verification receives a valid but unattested CANDIDATE record
- **THEN** attestation and overall outcomes MUST NOT be PASS

#### Scenario: Recomputed record digest
- **WHEN** an editor changes artifact metadata and recomputes the unkeyed record ID after the original record bytes were attested
- **THEN** attestation verification MUST fail for the changed bytes and overall verification MUST NOT be PASS

#### Scenario: Record path changes during verification
- **WHEN** the selected record file changes after its bytes have been read
- **THEN** verification MUST parse and attest only the captured byte snapshot, and MUST NOT report PASS for different bytes

#### Scenario: Artifact tampering
- **WHEN** an artifact is missing or its size or digest differs
- **THEN** artifact integrity MUST be FAIL and overall verification MUST NOT be PASS, independently of hosted CI result

#### Scenario: Run rerun or hosted mismatch
- **WHEN** the recorded run's current attempt differs or the API data no longer matches the record
- **THEN** hosted CI MUST be BLOCKED and overall verification MUST NOT be PASS

#### Scenario: Legacy or BLOCKED record
- **WHEN** verification receives a v1 or integrity-valid BLOCKED record
- **THEN** verification MUST reject it and MUST NOT report PASS

### Requirement: Ruleset evidence remains separate
A successful Actions run MUST NOT be treated as proof that repository rulesets require `ci / required` from GitHub Actions. M12 MUST retain separate live observation of enforcement settings and required-check source.

#### Scenario: Hosted run passes without observed enforcement
- **WHEN** a valid workflow run exists but repository ruleset settings have not been observed
- **THEN** release provenance MAY pass its run check, but M12 qualification MUST remain blocked on the separate enforcement gate

### Requirement: Candidate signing is manually approved and least-privileged
The attestation CLI MUST read candidate bytes once, validate that parsed snapshot, and dispatch those same bytes. The attestation workflow MUST be manually dispatched on `main`, validate candidate integrity and live hosted CI before signing, and require the `release-provenance-attestation` environment. Its signing job MUST use only `contents: read`, `id-token: write`, `attestations: write`, and `artifact-metadata: write`; `actions: read` needed for API validation MUST be scoped to a separate validation job. Workflow dispatch input MUST be rejected above 60,000 serialized UTF-8 bytes. The workflow MUST report the candidate source and artifact hashes for reviewer inspection. The attestation proves only the approved manifest bytes; it MUST NOT claim the signing workflow built the listed artifacts.

Before signing, candidate artifact metadata MUST be validated: path MUST be a safe single filename, size MUST be a non-negative integer (booleans are invalid), and SHA-256 MUST be exactly 64 lowercase hexadecimal characters. The reviewer summary MUST encode every record-derived value as safe Markdown text, including artifact path, size, and digest.

#### Scenario: Candidate approval and signing
- **WHEN** a valid candidate passes live-CI validation and an authorized reviewer approves the protected environment
- **THEN** the signing job MUST attest the same bytes validated by the first job

#### Scenario: Dispatch limit or validation failure
- **WHEN** serialized dispatch input exceeds 60,000 bytes or candidate/live-CI validation fails
- **THEN** no attestation MUST be produced

#### Scenario: Invalid artifact metadata
- **WHEN** a candidate contains an unsafe artifact path, a negative or non-integer size, or a malformed SHA-256 value
- **THEN** candidate validation MUST fail before the reviewer summary is written or any attestation is produced

#### Scenario: Markdown-sensitive metadata in approval summary
- **WHEN** otherwise valid candidate metadata contains Markdown-sensitive characters
- **THEN** the reviewer summary MUST render the literal values without creating Markdown structure or changing the displayed metadata
