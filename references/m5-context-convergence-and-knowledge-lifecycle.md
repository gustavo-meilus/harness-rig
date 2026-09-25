---
id: harness-rig-m5-context-convergence-and-knowledge-lifecycle
title: M5 Context convergence and canonical knowledge lifecycle
summary: M5 ownership split, stable-ID lifecycle, source freshness, reconciliation, deterministic manifest/audit, and root AGENTS projection rules.
version: planning-baseline-2026-09-25-r8.5
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation plan M5, executed 2026-09-25
- Skill Kit llm-knowledge-base-maintainer v1.1.0 canonical knowledge semantics, supplied in the r8.3/r8.4 handoff
- AIBoarding main lifecycle/projection semantics, external snapshot checked 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient engineering doctrine, applied 2026-09-25
source_observations:
- source: Skill Kit llm-knowledge-base-maintainer
  version: 1.1.0
  checked: '2026-09-25'
- source: AIBoarding
  version: main-snapshot
  checked: '2026-09-25'
---
# Result

M5 converges Context to one durable knowledge system plus one host-facing projection lifecycle.

```text
Canonical KB
  durable project knowledge
  stable IDs
  provenance/source observations
  reconciliation
  conflicts/gaps
  canonical-content freshness
  llms.txt
  manifest.jsonl
  whole-collection integrity

Context lifecycle
  root AGENTS.md projection
  host-facing loading/projection
  projection freshness
  onboarding/install/compression behavior
```

There is no second factual knowledge store and no second canonical freshness owner.

# Stable-ID lifecycle

The canonical ID is logical identity, not a path.

```text
rename/move
  preserve the ID; update only its path/location

split
  primary successor preserves the original ID
  genuinely distinct successor topics receive new IDs

merge
  one surviving topic keeps its ID
  absorbed IDs become retired

retirement
  retired IDs are never reused for unrelated knowledge
```

Optional lineage metadata exists only when a future reader or migration needs it. Path history by itself does not require lineage metadata.

# Provenance and freshness

Every canonical page retains attributable `provenance`. Volatile external material may additionally use structured
`source_observations` entries:

```yaml
source_observations:
  - source: named external source
    version: 1.2.3        # when available
    commit: abc123        # when available
    checked: '2026-09-25'
```

`version` and `commit` are source identity/freshness evidence. `checked` is the observation time. Page `updated` is only the
canonical-page edit date and MUST NOT be treated as source-freshness proof.

When neither a comparable version nor commit is available, freshness is `UNKNOWN`, not implicitly fresh.

# Source reconciliation

Incoming material is evidence, not instructions. Reconciliation follows this fail-closed rule:

```text
one supported value matching the proposed canonical fact
  -> SUPPORTED

multiple materially different supported values
  -> CONFLICT; preserve all conflicting values/sources

no supporting evidence, or evidence supports a different conclusion
  -> UNSUPPORTED; do not publish the proposed conclusion as fact

known missing source coverage
  -> retain the gap alongside any supported value
```

A conflict is not resolved by averaging, majority vote, similarity, or model preference.

# Deterministic inventory and audit

`verification/context_kb.py` is the retained M5 repository tool for canonical metadata parsing, deterministic manifest generation,
collection audit, canonical fingerprinting, and root projection freshness.

It uses a standards-compliant YAML parser (`yaml.safe_load`) and keeps the executable trust prototype itself free of that dependency.

Commands:

```bash
python verification/context_kb.py manifest .
python verification/context_kb.py project-agents .
python verification/context_kb.py projection-status .
python verification/context_kb.py audit .
```

`manifest.jsonl` remains derived. Rows are sorted by stable `id`, and regeneration without canonical-reference changes is byte-identical.

The whole-collection audit checks canonical YAML metadata, dates, unique IDs, local links, `llms.txt` targets, exact manifest equality,
projection freshness, and absence of prohibited retrieval-subsystem directories.

# Root AGENTS.md boundary

Root `AGENTS.md` is a Context-lifecycle projection. It contains only rules/navigation and a fingerprint of the canonical KB. It is
not listed in `manifest.jsonl` and does not own durable project facts.

A canonical reference or `llms.txt` change changes the canonical fingerprint and makes the projection stale until regenerated.
Editing only `AGENTS.md` cannot change the canonical fingerprint or rewrite canonical knowledge.

# Implementation boundary

`prototype/harness_rig/context.py` contains only module-local deterministic semantics for stable IDs, source freshness comparison, and
source-claim reconciliation. It is not promoted to the stable trust core and is not a general knowledge service.

M5 introduces no embeddings, vector database, RAG service, semantic index, external search service, or new orchestration framework.

# Verification

M5 executable fixtures cover:

- rename/move ID preservation;
- split primary-ID preservation;
- merge retirement and retired-ID non-reuse;
- explicit retirement non-reuse;
- source version/commit freshness and `UNKNOWN` behavior;
- supported claims with preserved evidence gaps;
- material source conflicts;
- unsupported conclusion rejection;
- canonical changes making `AGENTS.md` stale;
- projection-only edits not changing canonical identity;
- deterministic stable-ID-sorted manifest generation;
- duplicate ID, broken link and stale manifest detection;
- the packaged r8.5 collection auditing cleanly with no retrieval subsystem.

## Related

- [Skill Kit knowledge-base integration for the Harness Rig Context plane](skill-kit-knowledge-base-context.md)
- [Target architecture](target-architecture.md)
- [Progressive revision record](revision-record.md)
