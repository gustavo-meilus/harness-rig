---
id: harness-rig-progressive-revision-record
title: Harness Rig progressive revision record
summary: Current progressive-remediation milestone status, verification result, evidence limits, and next permitted milestone.
version: planning-baseline-2026-09-25-r8.5
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation M0-M4 execution and verification, 2026-09-24 through 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient engineering doctrine, applied 2026-09-25
- Harness Rig M5 Context convergence implementation and adversarial lifecycle verification, 2026-09-25
- Local runtime evidence: Python 3.13.5, Git 2.47.3 and PyYAML 6.0.3, 2026-09-25
---
# Current revision

```text
milestone: M5
package revision: r8.5
result: PASS
date: 2026-09-25
next allowed milestone: M6
resume task: M6-T01
```

# M5 Context ownership

```text
Canonical KB owns
  durable project knowledge / stable IDs / provenance
  source reconciliation / material conflicts and gaps
  canonical-source freshness / llms.txt / manifest / structural integrity

Context lifecycle owns
  root AGENTS.md projection / host-facing projection
  projection freshness / onboarding-install-compression lifecycle
```

There is no second factual knowledge store or duplicate source-freshness ledger.

# M5 lifecycle semantics

- Rename/move preserves stable ID.
- Split keeps the original ID on the primary successor; distinct topics receive new IDs.
- Merge retains one surviving ID and retires absorbed IDs.
- Retired IDs cannot be reused for unrelated knowledge.
- Volatile source freshness compares source version/commit plus checked date; page `updated` is not freshness evidence.
- Reconciliation preserves conflicts and gaps and rejects unsupported conclusions.
- Root `AGENTS.md` is a rules/navigation projection stamped with the canonical-KB fingerprint.
- `manifest.jsonl` remains deterministically derived from canonical references.

# Runtime verification

```text
M3 regression suite: 22/22 PASS
M4 adversarial suite: 15/15 PASS
M5 Context suite: 14/14 PASS
combined unittest cases: 51/51 PASS
M1-F01 ... M1-F16 remain PASS through M3 regressions
M5-V01 ... M5-V05 PASS
canonical references / manifest rows: 39 / 39
collection audit: PASS
AGENTS projection freshness: FRESH
manifest regeneration: byte-identical
```

# Important boundary

M5 does not design or implement the M6 OpenSpec `SpecEngine`. It does not promote Context internals into stable core and does not
introduce vector search, embeddings, RAG, a semantic index, a database, or another orchestration layer.

`EvidenceReceipt` and `AcceptanceVerdict` remain Experimental shared contracts from M4.

# Next

Resume at **M6-T01 - Implement/refine DirectAuthorityProvider and OpenSpecAdapter**. M6 has not been executed.
