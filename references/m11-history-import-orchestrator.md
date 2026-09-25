---
id: harness-rig-m2-import-orchestrator
title: M11 source-history import orchestrator
summary: Prepared source-aware M11 pipeline for source-history preflight, rewrite, independent verification, import bundles
  and target staging.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Harness Rig M2 retry 4 import-orchestrator implementation and synthetic end-to-end verification, 2026-09-25
- Git 2.47.3 native bundle/clone/fsck/plumbing used for synthetic import-pipeline evidence, 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient migration-tooling doctrine retained, 2026-09-25
- 'Harness Rig remediation sequencing decision: CHANGELOG-backed M2 and deferred Git-history qualification in M11, 2026-09-25'
---
# Current role

This is **M11 qualification tooling**. It is retained from earlier migration preparation but is not required for M2 progression.

Primary purpose: source preflight, three-source orchestration, verified import bundles and explicit target staging.

Root `CHANGELOG.md` is the traceability baseline that this tooling must reconcile against at M11.

# Status

M11 remains `BLOCKED` on the real source histories, but its prepared import pipeline is now implemented and synthetically verified.

```text
source-aware preflight: IMPLEMENTED
history rewriter: IMPLEMENTED
independent verifier: IMPLEMENTED
three-source orchestrator: IMPLEMENTED
rewritten import bundles: IMPLEMENTED
target staging helper: IMPLEMENTED
synthetic end-to-end pipeline: PASS
real source imports: BLOCKED
```

# Pipeline

`verification/m11-run-history-imports.py` accepts the three source bundles, validates them, mirror-clones them into disposable repositories, rewrites history, verifies every old→new mapping, emits verified rewritten import bundles, and writes an import summary.

`verification/m11-fetch-import-bundles.py` stages those rewritten histories under namespaced refs in a target Harness Rig repository without auto-merging them. The final merge remains explicit so semantic refactoring cannot be hidden in import automation.

# Preflight

Preflight v2 requires a readable Git history, `refs/heads/main`, a non-empty main history, full clone/fsck integrity, and the two relevant Skill Kit plugin paths.

# Synthetic evidence

`verification/m11-import-orchestrator-synthetic-evidence.json` records PASS for the complete three-source flow, target staging, branch/merge preservation, executable modes, symlinks, Skill Kit path filtering, and explicit annotated-tag fidelity limits.

# Fidelity limit

Rewritten commit IDs necessarily change. Cryptographic commit signatures and annotated-tag object/signature identity are not preserved by the current rewrite. `tag-map.json` records the source object and `annotation_preserved: false`.

The real histories must be inspected for whether stronger signed provenance is required before M11 PASS.

# Current real-input state

The current preflight is still BLOCKED because `aiboarding.bundle`, `tacticswitch.bundle`, and `skill-kit.bundle` are absent.

Synthetic PASS validates the mechanism only; it does not satisfy M11-T01–T04 or M11-V01–V04.

## Related

- [M11 history-import execution status](m11-git-history-qualification-status.md)
- [M11 history rewrite and verification tooling](m11-history-rewrite-tooling.md)
- [History migration and monorepo plan](history-migration-and-monorepo-plan.md)
