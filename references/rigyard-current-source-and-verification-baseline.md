---
id: harness-rig-rigyard-current-source-and-verification-baseline
title: RigYard current source and verification baseline
summary: Source-level classification of the supplied RigYard 0.1.1 snapshot, retained verification evidence, active OpenSpec
  changes, and historical status material.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- RigYard package.json, source, tests, docs, and OpenSpec change/spec files from the supplied snapshot
- Retained RigYard host/release verification artifacts from the supplied snapshot; not independently rerun in M0
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
---
# Scope

This page is the canonical source-level planning baseline for the user-supplied `rigyard_current.zip` snapshot inspected
2026-09-24.

It distinguishes current implementation, retained evidence, active proposals, and stale historical transition material.

The snapshot is authoritative for the files it contains. It does not contain `.git/`, so it cannot establish the live
repository's current branch, full history, or exact current commit beyond commit/tag identifiers recorded inside retained
documents.

# Snapshot shape

Observed snapshot inventory:

```text
package: rigyard 0.1.1
runtime: Node.js >=20
language: TypeScript / ESM
src files: 90
test files: 101
dist files: 360
OpenSpec files: 131
archived OpenSpec changes: 11
active OpenSpec changes: 8
```

The package scripts include build, lint, typecheck, unit/integration/contract/security/crash-recovery/e2e suites and a
live isolated-writer canary.

# Retained verification maturity

## Formally retained Codex/Linux v0.1 evidence

`docs/codex-host-evidence.json` uses schema:

```text
rigyard/codex-host-evidence/v1
```

and records a Linux local-filesystem observation with distinct workers, concurrency, structural result-only write denial,
independent results, one-use capability acceptance, replay/stale-result rejection, required-capability blocking,
interruption, and recovery.

`docs/v0.1-release-readiness.md` records the v0.1.0 public GitHub prerelease and exact retained release/candidate identities.

`docs/verification-evidence.md` records the retained v0.1.1 verification baseline and explicitly limits its native
qualification claim to the validated Codex/Linux local-filesystem target.

These are **retained project evidence**. M0 did not independently rerun the complete RigYard test/native-host matrix.

## Experimental/unqualified adapters

`docs/claude-code-host-readiness.json` and `docs/github-copilot-cli-host-readiness.json` both record:

```text
formalEvidenceEmitted: false
maturity: experimental
```

because their fixed executables were unavailable on the retained evidence host.

No Harness Rig plan may promote those adapters to a native-qualified/Stable claim without new evidence.

## Isolated writers

The `add-v0-3-isolated-parallel-writers` change is nearly task-complete and the source contains isolated-writer machinery.

However, `docs/codex-isolated-writer-host-evidence.md` explicitly states that no formal:

```text
rigyard/codex-isolated-writer-host-evidence/v1
```

packet is retained.

The 2026-09-01 live canary found a structural Bubblewrap boundary but hit Codex mutable-home/authentication constraints.
The project intentionally remains fail-closed for `isolated-write`.

Therefore:

```text
implemented/local evidence
!=
formal native qualification
!=
Stable claim
```

# Active OpenSpec changes

| Change | Checked tasks | Open tasks | Current evidence status |
|---|---:|---:|---|
| `add-harness-mutation-verification` | 0 | 12 | planned/unimplemented |
| `add-v0-3-isolated-parallel-writers` | 51 | 1 | implemented/local verification; formal isolated-writer host packet missing |
| `add-v0-4-approved-pipeline-evolution` | 0 | 34 | planned |
| `add-v0-5-static-composition` | 0 | 34 | planned |
| `add-v0-6-richer-topology` | 0 | 60 | planned |
| `add-v0-7-cross-host-distributed-execution` | 0 | 45 | planned |
| `add-v0-8-operational-observability-and-effects` | 0 | 50 | planned |
| `qualify-claude-code-native-execution` | 0 | 72 | active qualification proposal; blocked/unqualified |

Task counts are derived from the supplied `tasks.md` files and are evidence of proposal progress, not proof of feature
correctness.

# Archived changes

The snapshot contains 11 archived change directories, including MVP establishment/hardening, durable-result evidence,
foreground transition serialization, v0.2 adapter parity, v0.1 release preparation, OpenSpec brief normalization, and
versioning of core acceptance-check evidence.

Archived status establishes project history in the snapshot; it does not by itself prove current runtime behavior.

# Stale historical transition material

The snapshot retains documents whose status claims are older than the current release/evidence baseline, including:

```text
INITIAL_STATE.md
handoff.md
parts of GRILL_REPORT.md
```

Where those documents describe v0.1 as still blocked or refer to the old unarchived MVP change path, treat the claims as
historical transition context.

For current status prefer:

```text
README.md
ROADMAP.md
CHANGELOG.md
docs/v0.1-release-readiness.md
docs/verification-evidence.md
current OpenSpec change/spec files
current source/tests
```

# Harness Rig use

Harness Rig must use this snapshot in three ways:

1. **Implementation evidence** — reuse proven RigYard mechanisms before inventing cleaner generalized replacements.
2. **Proposal evidence** — inspect each active OpenSpec change but do not inherit it automatically.
3. **Negative evidence** — preserve explicit missing-native-evidence and fail-closed cases as design requirements.

Final proposal disposition belongs to progressive remediation milestone M11.

# Known evidence limits

M0 does not claim:

- independent rerun of all RigYard tests;
- independent rerun of native host canaries;
- exact live Git repository identity from the ZIP;
- implementation of active OpenSpec proposals whose tasks/source do not establish completion.

## Related

- [Current system baseline](current-system-baseline.md)
- [RigYard premise and minimum-sufficient feature admission](rigyard-premise-and-feature-admission.md)
- [Expected Harness Rig feature set and RigYard reconciliation contract](expected-harness-rig-feature-set.md)
- [Roadmap](roadmap.md)
- [Source register](source-register.md)
