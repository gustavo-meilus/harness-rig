---
id: harness-rig-m10-product-cli-migration-release-provenance
title: M10 product CLI, migration completion, and release provenance
summary: Implemented r8.10 compact product CLI, versioned machine contract, fail-closed configuration, bounded migration state, process cleanup, and deterministic release provenance.
version: planning-baseline-2026-09-25-r8.10
updated: '2026-09-25'
provenance:
- Harness Rig M10 implementation and adversarial verification, 2026-09-25
- Harness Rig M2 source-disposition and M11 history-qualification separation retained through M10
- Harness Rig M7 repository verdict contract reused as the release acceptance prerequisite
- Skill Kit More With Less v1.0.2 minimum-sufficient productization doctrine applied 2026-09-25
---
# Result

M10 completed with **PASS** at revision `r8.10` for the product CLI, runtime/schema migration, and release-provenance boundary.

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

`harness-rig/release-record/v1` binds:

```text
accepted source revision
accepted repository verdict
build workflow identity
creation time
artifact path/size/SHA-256
optional attestation reference
record integrity ID
```

A record with no accepted repository verdict is `BLOCKED`; local tests do not impersonate hosted `ci / required` acceptance. `verification/release_provenance.py` builds or verifies immutable records. Rewriting a release record with different content is rejected, and artifact tampering is detected by size/SHA-256 mismatch.

Attestation is an optional reference only. M10 introduces no signing service or new attestation platform because no current consumer requires one.

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
- release records bind build outputs and detect tampering;
- release eligibility remains blocked when an accepted repository verdict is absent.

# Deferred boundary

M11 still owns object-complete source histories, real source->rewritten commit/tag maps, import-only/tree-equivalence checks, legacy deterministic checks, license/state/hook/install reconciliation, signed commit/tag fidelity, and CHANGELOG-to-history reconciliation.

M10 must not be used as evidence that those M11 requirements have passed.
