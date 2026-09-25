---
id: harness-rig-adr-state-identity
title: 'ADR: Experimental StateIdentity protocol'
summary: Accepted M1 protocol separating revision provenance, index state, worktree content, untracked content, and submodule
  state before Stable promotion.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation M1 trust-protocol review, 2026-09-24
- User-supplied Harness Rig adversarial architecture review, 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- RigYard acceptance evidence, durable worker evidence, result acceptance, attempt capability, workspace baseline source/tests
  inspected 2026-09-24
- Skill Kit more-with-less v1.0.2 canonical skill and playbook inspected 2026-09-24
- Git official status/diff/submodule documentation rechecked 2026-09-24
- Node.js official child_process documentation rechecked 2026-09-24
---
# Status

**Accepted for Experimental implementation in M1. Stable promotion is forbidden before M4.**

# Decision

`StateIdentity` is structured rather than one opaque HEAD/dirty hash.

```text
repository_id
revision:
  head_oid | UNBORN
  head_tree_oid | null
index:
  manifest_digest
worktree:
  tracked_manifest_digest
  untracked_nonignored_manifest_digest
submodules[]
content_id
state_id
```

Normative M1 distinction:

```text
revision provenance != repository content != staged/index state
```

A content-only gate may reuse evidence across different revision IDs only when policy explicitly permits it and all other
applicability conditions match. Lineage/release/CI claims can require exact revision equality.

# Repository identity

`repository_id` identifies the logical project/repository boundary and is not the absolute filesystem path. The final source
of this ID remains Experimental implementation work; Harness Rig must not silently claim a mutable remote URL is a globally
stable repository identity.

# Index

The logical Git index is part of state. Hash deterministic staged entries (path identity, stage, mode/type, object identity)
rather than physical `.git/index` bytes.

# Working tree

Tracked identity distinguishes regular-file bytes, symlink target, submodule/gitlink, deletion, and material type/mode
changes. Do not normalize checked-out bytes before hashing.

Untracked nonignored files participate in content identity.

Ignored/generated/cache files are excluded by default. When a gate consumes one, bind it in the receipt's material input
bindings instead of expanding repository state globally.

# Paths and symlinks

Use machine-readable NUL-delimited Git enumeration where applicable and hash byte-preserving path identities, not
shell/display quoting or platform separators.

A tracked symlink is identified as a symlink and by its link target. Dereferenced external content is not silently part of
repository state; a gate that consumes it binds that external target separately.

# Submodules

Submodules are explicit state components. Record the superproject gitlink, observed submodule HEAD and dirty/untracked
condition. If required submodule content is consumed, include/bind that content identity. Unknown required submodule state is
`BLOCKED`, never "unchanged."

# Worktrees and read failures

Capture the actual worktree under evaluation. Same HEAD in two worktrees is insufficient if index/content differs.

Failure to enumerate/read required state makes identity incomplete; incomplete identity cannot support PASS.

# Canonical serialization

Experimental `canonical-json-v1`:

```text
UTF-8 JSON
keys lexicographically sorted
path-record arrays sorted by byte-preserving path key
no insignificant whitespace
integers only
digests lowercase sha256:<64 hex>
```

Golden vectors are required before M4 Stable promotion.

# Mutation rule

```text
S0 = exact_state()
run gate
S1 = exact_state()

S1 != S0 -> MUTATED; the run does not certify S1
```

# Minimum-sufficient boundary

Do not add a global environment-state type, a central state DB, hashes for every ignored file, or atomic multi-repository
state without a demonstrated workflow requiring it.

## Related

- [EvidenceReceipt ADR](adr-evidence-receipt.md)
- [Trust fixtures](trust-protocol-adversarial-fixtures.md)
