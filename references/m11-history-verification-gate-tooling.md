---
id: harness-rig-m2-verification-gate-tooling
title: M11 history qualification verification tooling
summary: Prepared M11 verification tooling for reproducible mappings, legacy checks, import-only proof, surface inventory
  and CHANGELOG/history reconciliation.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- Harness Rig M2 retry 5 verification-gate tooling implementation and synthetic adversarial verification, 2026-09-25
- AIBoarding public README rechecked 2026-09-25 for canonical offline check `bash tests/run.sh`
- TacticSwitch public README rechecked 2026-09-25 for install/verify commands and current evidence limits
- Skill Kit public repository rechecked 2026-09-25; tests/scripts surfaces confirmed but no complete deterministic filtered-plugin
  command inferred
- 'Harness Rig remediation sequencing decision: CHANGELOG-backed M2 and deferred Git-history qualification in M11, 2026-09-25'
---
# Current role

This is **M11 qualification tooling**. It is retained from earlier migration preparation but is not required for M2 progression.

Primary purpose: reproducibility, source-native checks, import-only proof and imported-surface verification.

Root `CHANGELOG.md` is the traceability baseline that this tooling must reconcile against at M11.

# Status

M11 remains `BLOCKED` on the actual source-history inputs.

The tooling required to execute and evaluate **M11-V01–V04** is now implemented and passes synthetic/adversarial tests.

```text
M11-V01 reproducible history mappings:
  verifier tooling READY
  synthetic result PASS
  real-source result BLOCKED

M11-V02 legacy checks from imported prefixes:
  runner tooling READY
  synthetic PASS
  missing-required-tool BLOCKED fixture PASS
  real-source result BLOCKED

M11-V03 proof of import-only commits:
  verifier tooling READY
  valid import fixture PASS
  outside-prefix tamper rejected PASS
  real-source result BLOCKED

M11-V04 imported surface inventory:
  deterministic inventory tooling READY
  synthetic category fixture PASS
  real-source result BLOCKED
```

# M11-V01 — reproducibility

Tool:

```text
verification/m11-verify-reproducibility.py
```

It executes the prepared import pipeline twice from the same input histories and compares:

```text
commit-map.json
ref-map.json
tag-map.json
rewrite-report.json
verify-report.json
semantic bundle refs
```

The raw bundle byte stream is not used as the reproducibility invariant because Git pack serialization is an implementation
detail. The required invariant is the same rewritten history identity, mappings and refs.

Synthetic result: `PASS`.

# M11-V02 — legacy deterministic checks

Tool:

```text
verification/m11-run-legacy-checks.py
```

Properties:

- structured argv only; no shell-string construction;
- explicit repository-relative working directory;
- bounded captured output;
- unavailable required executable -> `BLOCKED`;
- nonzero deterministic check -> `FAIL`;
- zero exit -> `PASS`.

Current source-backed discovery:

## AIBoarding

Current public README explicitly identifies:

```text
bash tests/run.sh
```

as the deterministic repository suite.

The M11 check record therefore marks that check `READY`.

## TacticSwitch

The current README explicitly documents:

```text
python scripts/install.py ...
python scripts/verify_install.py ...
```

but the inspected public root/README does not establish one complete deterministic repository test command.

M11 therefore records full check discovery as pending the actual imported source rather than inventing a test command.

## Skill Kit

The current public root confirms `tests/` and `scripts/` and the relevant plugins, but the inspected root page does not state
one complete deterministic check command specifically covering the two filtered plugins.

M11 therefore defers exact deterministic-check discovery to the imported source.

Machine discovery record:

```text
verification/m11-legacy-check-discovery.json
```

Synthetic results:

```text
valid required check -> PASS
missing required executable -> BLOCKED
```

# M11-V03 — import-only proof

Tool:

```text
verification/m11-verify-import-only.py
```

For an explicit two-parent history-import merge commit it verifies:

1. exactly two parents;
2. diff against the pre-import parent changes only the authorized legacy prefix;
3. every tree entry from the rewritten imported parent is preserved exactly in the merge commit.

Synthetic results:

```text
valid unrelated-history import merge -> PASS
same shape plus BAD.txt outside legacy prefix -> FAIL
```

This prevents semantic Harness Rig changes from being smuggled into the history-import commit.

# M11-V04 — imported surface inventory

Tool:

```text
verification/m11-inventory-imported-surface.py
```

It deterministically inventories every path below an imported legacy prefix and classifies migration-relevant surfaces:

```text
licenses/notices
state
hooks
host/plugin manifests
install/update
generated/distribution
schemas/contracts
tests/evals
CI
OpenSpec
agent/role surfaces
```

The classification is an inventory aid, not a claim that path naming alone determines semantic ownership.

The real M11-V04 check still requires inspection of the imported sources and reconciliation against the source-side inventory.

# Full verification gate

Prepared coordinator:

```text
verification/m11-run-verification-gate.py
```

It combines M11-V01–V04 after:

- the real bundles have passed preflight;
- actual rewritten histories have been produced;
- explicit import merge commits exist;
- source-specific deterministic check plans have been confirmed from the imported repositories.

# Synthetic evidence

Machine record:

```text
verification/m11-verification-tooling-synthetic-evidence.json
```

Passed cases:

```text
V01 reproducibility
V02 deterministic check PASS
V02 required-tool unavailable -> BLOCKED
V03 valid import-only merge
V03 outside-prefix tamper rejected
V04 deterministic surface inventory
```

# Evidence boundary

This is **verification-tooling evidence**.

It does not change:

```text
M11-V01 real source: BLOCKED
M11-V02 real source: BLOCKED
M11-V03 real source: BLOCKED
M11-V04 real source: BLOCKED
```

until the actual Git histories are imported.

## Related

- [M11 source-history import orchestrator](m11-history-import-orchestrator.md)
- [M11 history rewrite and verification tooling](m11-history-rewrite-tooling.md)
- [M11 history-import execution status](m11-git-history-qualification-status.md)
