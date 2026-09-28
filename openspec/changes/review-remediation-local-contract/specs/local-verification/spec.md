# Local verification

## Purpose

Defines the evidence a local operator can obtain from command verification and
guarded OpenSpec archive without claiming authenticated action authorization.

## ADDED Requirements

### Requirement: Local command verification states only observed evidence

`verify` and `direct` MUST NOT issue an authorization grant or return an
authorization-bearing acceptance verdict. They MUST report the command gate
result with its authority and state bindings and identify it as local evidence.

#### Scenario: Passing local command

- **WHEN** a local command gate passes for the observed authority and state
- **THEN** the command reports local PASS evidence without merge authorization

#### Scenario: Failed or stale local command

- **WHEN** the gate fails or its authority or state binding is stale
- **THEN** the command fails closed and reports no authorized verdict

### Requirement: Archive is an explicit local guarded transition

`spec archive` MUST require explicit local confirmation before mutation. It
MUST preserve readiness, exact pre-state, transition, and postcondition checks,
and MUST NOT issue a grant or claim authenticated archive authorization.

#### Scenario: Archive without confirmation

- **WHEN** the local confirmation flag is absent
- **THEN** archive returns BLOCKED without mutation

#### Scenario: Archive precondition changes

- **WHEN** readiness fails or the observed authority or state changes
- **THEN** archive returns BLOCKED without an authorized acceptance claim

#### Scenario: Archive transition fails

- **WHEN** OpenSpec archive or its postconditions fail
- **THEN** the result records the transition evidence and reports BLOCKED

### Requirement: Grant data does not authenticate its issuer

The retained grant schema and validator MUST be described as structural and
contextual checks only. No local CLI result may use them as proof that an
issuer or principal was independently authenticated.

#### Scenario: Caller supplies a matching grant

- **WHEN** a caller supplies grant fields that match local context
- **THEN** local CLI commands still report no authenticated authorization
