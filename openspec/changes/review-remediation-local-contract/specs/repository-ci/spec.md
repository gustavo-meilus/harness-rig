# Repository CI

## Purpose

Defines a factual GitHub Actions project check for tests and Context integrity,
including the limit of a workflow that a candidate revision may edit.

## ADDED Requirements

### Requirement: Required check reports mandatory job results

For pull requests, main pushes, manual dispatches, and merge groups, ordinary
tests and Context audit MUST run unconditionally. `ci / required` MUST fail
when either prerequisite fails, skips, or is cancelled. Fork pull requests
MUST run without repository secrets or write permissions.

#### Scenario: Both prerequisites pass

- **WHEN** ordinary tests and Context audit succeed for the run
- **THEN** `ci / required` succeeds for that run

#### Scenario: A prerequisite does not succeed

- **WHEN** either prerequisite fails, skips, or is cancelled
- **THEN** `ci / required` fails

#### Scenario: Merge queue evaluates a candidate

- **WHEN** GitHub requests merge-group checks
- **THEN** the workflow runs against that merge-group revision

### Requirement: CI does not claim an independent acceptance oracle

The product MUST disclose that candidate-controlled workflow changes can alter
the logic that emits `ci / required`. A successful check or required-check
ruleset MUST NOT be represented as independent authorization or review of
those changes.

#### Scenario: Candidate modifies its workflow

- **WHEN** a candidate changes the required workflow or its tests
- **THEN** its check result remains project CI evidence, not an independent
  protected-oracle verdict
