# Release provenance delta

## ADDED Requirements

### Requirement: V3 records bind source and hosted CI facts

A new release record MUST use `harness-rig/release-record/v3` and a factual
`source_revision` field. It MUST bind artifact paths, sizes, and SHA-256 hashes;
repository ID; hosted run, attempt, and required job IDs; and build identity.
Creation MUST yield CANDIDATE or BLOCKED, never release qualification. The
hosted run MUST be an authenticated GitHub API observation of a completed,
successful `push` run on `main` for the exact source SHA, from the required
workflow with one successful `ci / required` job in its current attempt.
This observation MUST NOT imply independent workflow integrity.

#### Scenario: Matching hosted run

- **WHEN** the API data matches every recorded source, run, and job identity
- **THEN** creation yields a CANDIDATE with those facts bound

#### Scenario: Missing or mismatched hosted run

- **WHEN** API access is unavailable or a required identity or result differs
- **THEN** creation yields BLOCKED and never release qualification

### Requirement: V3 verification separates provenance from acceptance

Verification MUST read record bytes once and attest those same bytes. It MUST
report artifact integrity, hosted CI observation, and attestation separately.
Overall provenance PASS requires all three PASS. It MUST re-fetch the recorded
run and reject changed attempts. Attestation MUST be scoped to the release
attestation workflow on `main`. V1, v2, BLOCKED, malformed, unsigned, and
mismatched records MUST NOT qualify a new release. Provenance PASS MUST NOT be
described as independent source acceptance.

#### Scenario: Valid attested record

- **WHEN** exact v3 bytes are attested and artifact and hosted-run checks pass
- **THEN** provenance reports PASS without an independent-acceptance claim

#### Scenario: Modified artifact or record

- **WHEN** an artifact differs, record bytes change, or attestation is missing
- **THEN** overall provenance does not report PASS

#### Scenario: Legacy record

- **WHEN** a v1 or v2 record is supplied for a new release
- **THEN** verification reports it ineligible without silently upgrading it

### Requirement: Source artifact is independently reproducible

A 1.0 source release MUST include a Git bundle made from the exact tagged
candidate and a recorded SHA-256 digest. An independent verifier MUST be able
to clone it offline, resolve the release tag to the recorded source commit,
and inspect the tracked M11 source bundles and maps.

#### Scenario: Exact source bundle

- **WHEN** the bundle is cloned and its tag, commit, and digest match the record
- **THEN** the source-artifact relationship is established

#### Scenario: Wrong source bundle

- **WHEN** the bundle digest or resolved release commit differs
- **THEN** release qualification fails

## MODIFIED Requirements

### Requirement: Ruleset evidence remains separate

A successful Actions run MUST NOT prove that repository rulesets require
`ci / required` from GitHub Actions. Live enforcement settings and check source
MUST be observed separately. Even then, the candidate-controlled workflow
MUST NOT be represented as an independent oracle in the revised 1.0 contract.

#### Scenario: Hosted run passes without observed enforcement

- **WHEN** a valid run exists but repository rulesets have not been observed
- **THEN** the hosted-run check MAY pass, but release qualification remains
  blocked on the separate settings observation

#### Scenario: Ruleset is observed

- **WHEN** `ci / required` is required from GitHub Actions
- **THEN** the record states that fact without claiming immutable workflow logic

## REMOVED Requirements

### Requirement: Release records require live hosted CI acceptance

**Reason**: Candidate-controlled CI is observed project CI, not an independent
acceptance oracle.

**Migration**: Create v3 records using `source_revision`; retain v2 as history.

#### Scenario: Existing v2 record

- **WHEN** a v2 record is inspected
- **THEN** it is not promoted into a v3 release candidate

### Requirement: Verification requires record attestation

**Reason**: The v2 requirement names overall PASS without the narrower v3
provenance boundary.

**Migration**: Use v3 verification, retaining exact-byte attestation and the
artifact and hosted-run checks.

#### Scenario: Existing verification result

- **WHEN** a v2 result is used for a new release
- **THEN** it is ineligible for v3 release qualification
