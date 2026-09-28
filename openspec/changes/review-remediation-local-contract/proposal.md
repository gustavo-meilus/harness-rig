# Review remediation: local 1.0 contract

## Why

The final review found self-issued authorization and candidate-controlled CI.
Product identity also conflicts across surfaces, and no release was verified.
Narrow the 1.0 contract to guarantees this solo-maintained repository can
establish, then qualify one exact candidate.

## What Changes

- **BREAKING**: `verify`, `direct`, and `spec archive` become local operations.
  They no longer claim authenticated authorization or authorized acceptance.
- **BREAKING**: release records state source and hosted-CI facts. Old v2
  records cannot qualify a new release.
- Replace CI obligation resolution with unconditional tests and Context audit.
  The final check uses native job results and claims no independent oracle.
- Reconcile identity, pin Actions, reproduce M11 evidence, and release only
  after exact-candidate verification and attestation.

## Capabilities

### New Capabilities

- `local-verification`: Local command and guarded archive outcomes without
  an authenticated authorization claim.
- `repository-ci`: Required-check behavior and its self-modification limit.

### Modified Capabilities

- `release-provenance`: Bind artifacts and hosted CI facts to an exact source
  revision without representing CI as independent acceptance.

## Impact

CLI and archive machine outputs change. Release-record schema advances to v3.
CI stays in GitHub Actions. No new provider, service, or dependency is added.
