---
id: harness-rig-m2-history-rewrite-tooling
title: M11 history rewrite and verification tooling
summary: Prepared native-Git migration-only rewrite and independent verification tooling retained for M11 source-history qualification.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Harness Rig M2 retry 3 native-Git migration tooling implementation and synthetic verification, 2026-09-25
- Git 2.47.3 native plumbing used for synthetic history rewrite/verification, 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient migration-tooling rule retained, 2026-09-25
- Harness Rig M2 retry 4 import-orchestrator implementation and synthetic end-to-end verification, 2026-09-25
- Git 2.47.3 native bundle/clone/fsck/plumbing used for synthetic import-pipeline evidence, 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient migration-tooling doctrine retained, 2026-09-25
- 'Harness Rig remediation sequencing decision: CHANGELOG-backed M2 and deferred Git-history qualification in M11, 2026-09-25'
---
# Current role

This is **M11 qualification tooling**. It is retained from earlier migration preparation but is not required for M2 progression.

Primary purpose: history rewrite, mapping, tree/topology verification and fidelity-limit handling.

Root `CHANGELOG.md` is the traceability baseline that this tooling must reconcile against at M11.

# Status

M11 remains `BLOCKED` on the real source Git histories, but the migration-tooling layer is now implemented and synthetically verified.

```text
real AIBoarding import: BLOCKED
real TacticSwitch import: BLOCKED
real Skill Kit import: BLOCKED
history rewrite tooling: IMPLEMENTED
rewrite verifier: IMPLEMENTED
synthetic integration suite: PASS
```

# Why native Git plumbing

The earlier plan named `git-filter-repo` as the preferred migration tool. It is not installed in the execution environment.

Rather than adding an unavailable migration dependency, preparation implements a small **migration-only** rewriter using Git's
native plumbing commands:

```text
rev-list
ls-tree
read-tree
update-index
write-tree
commit-tree
update-ref
```

This does not become Harness Rig runtime infrastructure.

The tool is acceptable only because it is bounded to M11, produces explicit mapping evidence, and is verified independently.
If the real source histories expose a case it cannot preserve safely, M11 returns `REWORK/BLOCKED` rather than expanding the
tool silently.

# Tooling

```text
verification/m11-history-rewriter.py
verification/m11-verify-rewrite.py
verification/m11-history-input-preflight.py
```

## Rewriter

The rewriter operates only on a **disposable verified source clone**.

For every source commit reachable from the captured heads/tags it creates one rewritten commit whose tree is:

```text
selected source paths
  -> moved below the configured legacy prefix
```

It preserves:

```text
parent topology
author identity/time
committer identity/time
commit message
blob/object identities
file modes
symlink entries
gitlink entries
one rewritten commit per source commit
```

It records:

```text
commit-map.json
ref-map.json
tag-map.json
rewrite-report.json
```

## Filtered Skill Kit history

Skill Kit uses a single filtered history containing:

```text
plugins/llm-knowledge-base-maintainer/**
plugins/engineering-harness-adaptive/**
LICENSE
```

under:

```text
legacy/skill-kit/
```

The rewriter keeps a one-to-one source commit chronology, including commits whose selected tree does not change. This avoids
duplicating a source commit that touched both relevant plugins and keeps the old→new map total.

Unrelated Skill Kit file content is not present in rewritten trees.

# Known migration fidelity limit

Rewriting necessarily changes commit IDs.

Current M11 tooling does **not** preserve cryptographic commit signatures or annotated-tag object/signature identity.
Namespaced imported tags point to the mapped rewritten commit, and `tag-map.json` records the original tag object/peeled
commit plus the limitation:

```text
annotation_preserved: false
```

Before real import acceptance, M11 must inspect whether any relevant release/tag requires stronger annotation/signature
preservation. If so, enhance the migration tool or retain that information as separate provenance before PASS.

# Independent verifier

`m11-verify-rewrite.py` independently compares each mapping against the source repository:

```text
expected filtered/prefixed tree == rewritten tree
mapped parent topology == rewritten parent topology
author metadata preserved
committer metadata preserved
commit message preserved
```

A wrong mapping fails.

# Synthetic verification

preparation executed three synthetic cases:

1. **Full source history** — branch, merge, and annotated source tag; prefix rewrite verified.
2. **Skill-Kit-style filtered history** — unrelated file changes excluded while all source commits remain mapped.
3. **Tampered map** — verifier deliberately receives a wrong mapping and rejects it.

Machine evidence:

```text
verification/m11-synthetic-migration-tooling-evidence.json
```

Result:

```text
PASS
```

This PASS applies to the migration tooling, not to M11's real source-history imports.

# Remaining M11 requirement

Real bundles/repositories are still required:

```text
aiboarding.bundle
tacticswitch.bundle
skill-kit.bundle
```

Once attached:

1. run `m11-history-input-preflight.py`;
2. clone each verified bundle to a disposable source repository;
3. run `m11-history-rewriter.py` with the import spec;
4. run `m11-verify-rewrite.py`;
5. inspect tag/signature limitations;
6. merge verified rewritten refs into Harness Rig;
7. run legacy checks from imported prefixes;
8. complete M11-V01–V04.

## Related

- [M11 history-import execution status](m11-git-history-qualification-status.md)
- [M11 source-surface inventory and capability dispositions](m2-source-surface-inventory-and-dispositions.md)
- [History migration and monorepo plan](history-migration-and-monorepo-plan.md)

# preparation — prepared import pipeline

The low-level migration helpers are now driven by [M11 source-history import orchestrator](m11-history-import-orchestrator.md), which passed synthetic three-source end-to-end verification.
