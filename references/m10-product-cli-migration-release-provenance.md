---
id: harness-rig-m10-product-cli-migration-release-provenance
title: M10 product CLI, migration completion, and release provenance
summary: Historical M10 product CLI and migration, with the current r8.12 local evidence and v3 provenance correction.
version: review-remediation-2026-09-28-r8.12
updated: '2026-09-28'
provenance:
- Harness Rig M10 implementation and adversarial verification, 2026-09-25
- Harness Rig M2 source-disposition and M11 history-qualification separation retained through M10
- 'M12 release-provenance correction: live authenticated GitHub Actions API acceptance and mocked regression verification, 2026-09-27'
- Skill Kit More With Less v1.0.2 minimum-sufficient productization doctrine applied 2026-09-25
- Harness Rig final review and local-contract OpenSpec remediation, 2026-09-28
---
# Result

M10 completed with **PASS** at revision `r8.10` for the product CLI, runtime/schema migration, and release-provenance boundary.

The current r8.12 product CLI reports local `verify`/`direct` gate evidence
without issuing a grant or merge verdict. Archive requires explicit local
confirmation and checks readiness, exact state, and postconditions without
an authenticated archive authorization claim. New release records use v3;
the earlier v1/v2 contracts remain historical.

M10 does not claim M11 source-history qualification or a releasable 1.0 state. It makes those prerequisites explicit and machine-readable instead of silently treating them as complete.

# Compact CLI

The product-facing command set is:

```text
harness-rig init
harness-rig doctor
harness-rig spec status
harness-rig spec archive
harness-rig verify
harness-rig status
harness-rig migrate
```

The r8.9 raw JSON forms for direct verification, `doctor`, and guarded `spec archive` remain compatibility surfaces. M10 automation-facing commands use `harness-rig/cli-envelope/v1`; `doctor --json-v1` and `spec archive --json-v1` provide the versioned envelope without invalidating the retained older shapes.

# Machine contract and exit categories

`harness-rig/cli-envelope/v1` contains:

```text
schema
command
outcome
exit_code
data
reasons
compatibility
```

Documented categories are:

```text
0   PASS
2   BLOCKED
3   FAIL
4   INVALID
5   ERROR
124 TIMEOUT
130 CANCELLED
```

Unknown envelope versions and unknown fields fail closed. The loader deterministically recognizes the two retained r8.9 JSON shapes and wraps them as v1 compatibility records.

# Configuration

The only product config schema is `harness-rig/config/v1`:

```text
noninteractive
openspec_executable
timeout_seconds
```

Precedence is:

```text
defaults < user-global < project < explicit CLI override
```

User-global config is deliberately unable to define repository policy. Repository policy remains owned by canonical project/governance files. A global `policy` key or any unknown field is rejected, so user configuration cannot silently weaken `ci / required`, architecture rules, authorization, or gate requirements.

Project configuration lives at `.harness-rig/config.json`. User-global discovery uses `HARNESS_RIG_GLOBAL_CONFIG`, then `XDG_CONFIG_HOME/harness-rig/config.json`, then `~/.config/harness-rig/config.json`.

No M10 command requires an interactive prompt. Missing capabilities or unsafe/malformed configuration produce `BLOCKED`/`INVALID` machine outcomes instead of falling back or asking for input.

# Timeout and cancellation cleanup

The direct verifier now uses a small argv-only process runner that launches a dedicated process group on POSIX. Timeout and cancellation terminate the whole child group before control returns. Tests prove a spawned descendant cannot survive the parent timeout to write a delayed sentinel.

This mechanism is intentionally scoped to the product direct-verifier path. M10 does not create a general process supervisor.

# Migration completion model

M10 distinguishes two meanings of completion:

```text
runtime/schema migration complete
  = current Harness Rig ownership/state/hook/distribution rules converge locally

1.0/source-history migration complete
  = runtime/schema complete + M11 object-complete history qualification PASS
```

The current migration state is `harness-rig/migration-state/v1`. The supported product upgrade is `r8.9 -> r8.10`; downgrade is an explicit rollback operation rather than an arbitrary target version.

The migration checker fails closed on:

- interrupted `APPLYING` journals;
- legacy markers mixed with a completed new state;
- duplicate hook ownership;
- unknown migration-state schemas;
- unsupported source/target revision pairs.

Migration state is written atomically. The complete r8.10 state retains `history_qualification = PENDING_M11`; this is deliberate and must not be converted to PASS before M11.

A small `harness-rig/history-map/v1` lookup helper is executable against synthetic mappings so old-to-new lookup semantics are tested without fabricating the real AIBoarding/TacticSwitch/Skill Kit mappings that M11 still owns.

# Release provenance

`harness-rig/release-record/v3` binds:

```text
explicit GitHub OWNER/REPO and API-returned repository ID
factual source_revision
workflow run ID and current attempt
unique ci / required job ID for that attempt
build workflow identity and creation time
artifact path/size/SHA-256
record integrity ID
```

Creation and verification use authenticated, read-only `gh api` calls. The run
must be completed and successful for `push` on `main`, the exact source SHA,
and `.github/workflows/ci-required.yml`; its recorded attempt must contain
exactly one completed successful `ci / required` job. Verification re-fetches
the run and attempt-specific jobs, so a rerun invalidates an older record.
Missing run or API access, malformed responses, and mismatches produce a
BLOCKED candidate, never PASS. An eligible record is still an unsigned
CANDIDATE. Candidate-controlled CI is observed project evidence, not an
independent acceptance oracle.

Use `verification/release_provenance.py attest` to submit the validated
candidate bytes to `.github/workflows/release-record-attestation.yml`. The serialized
UTF-8 input is limited to 60,000 bytes. The workflow validates record
integrity and live hosted CI, validates artifact paths as safe single
filenames, requires a non-negative integer size and 64-character lowercase
SHA-256 digest, then writes the approval summary through a Markdown-safe
renderer. It requires approval through the `release-provenance-attestation`
environment before attesting the same bytes.

Verification reads the record bytes once, parses that snapshot, and verifies
the attestation against the same bytes from a private temporary file. The CLI
does not reread the selected record path during verification. Verification
reports artifact integrity, hosted CI, and attestation separately;
overall PASS requires all three. `gh attestation verify` is scoped to the
explicit repository, signing workflow, and `refs/heads/main`. It rejects
blocked, unsigned, and legacy v1/v2 records. A valid attestation detects edits
after signing, but does not prove that the signing workflow built the listed
artifacts; the solo owner's approval records the approved hashes without
separation of duties. The checkout has no
Git remote, so callers must supply `OWNER/REPO`; no identity is inferred. Live
branch/ruleset settings and the required-check source remain a separate M12
gate. Local mocked API and attestation tests make no network requests and do
not establish hosted acceptance or repository enforcement.

# Verification

M10 adversarial coverage proves:

- noninteractive missing OpenSpec -> `BLOCKED`;
- malformed project config blocks before executing the verifier;
- global config cannot introduce repository-policy overrides;
- timeout kills descendant processes;
- cancellation executes the same cleanup boundary;
- interrupted and mixed old/new migration state fail closed;
- duplicate hooks are detected;
- supported upgrade/rollback is explicit and arbitrary downgrade is rejected;
- old-to-new mapping lookup works on deterministic synthetic evidence;
- candidate records bind artifact hashes to live CI; verified records also
  require an exact-byte GitHub attestation;
- release eligibility remains blocked when an accepted repository verdict is absent.

# Deferred boundary

M11 still owns object-complete source histories, real source->rewritten commit/tag maps, import-only/tree-equivalence checks, legacy deterministic checks, license/state/hook/install reconciliation, signed commit/tag fidelity, and CHANGELOG-to-history reconciliation.

M10 must not be used as evidence that those M11 requirements have passed.
