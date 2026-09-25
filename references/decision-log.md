---
id: harness-rig-decision-log
title: Harness Rig decision log
summary: Current accepted planning decisions, open decisions, and the rationale that should remain stable during migration.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Consolidated Harness Rig analysis through 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Harness Rig expected-feature synthesis, refreshed 2026-09-21
- Skill Kit llm-knowledge-base-maintainer v1.1.0, SKILL.md and DEFAULT_LAYOUT.md, inspected 2026-09-24
- Harness Rig knowledge-base-first Context synthesis, refreshed 2026-09-24
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- Harness Rig progressive remediation M1 trust-protocol review, 2026-09-24
- User-supplied Harness Rig adversarial architecture review, 2026-09-24
- RigYard acceptance evidence, durable worker evidence, result acceptance, attempt capability, workspace baseline source/tests
  inspected 2026-09-24
- Skill Kit more-with-less v1.0.2 canonical skill and playbook inspected 2026-09-24
- Git official status/diff/submodule documentation rechecked 2026-09-24
- Node.js official child_process documentation rechecked 2026-09-24
- 'Harness Rig remediation sequencing decision: CHANGELOG-backed M2 and deferred Git-history qualification in M11, 2026-09-25'
---
# Accepted planning decisions

## D1 — One Harness Rig product/monorepo
## D2 — Minimum-sufficient control plane
## D3 — More With Less is the feature-admission doctrine

## D4 — Relevant Skill Kit migration scope includes two capabilities

```text
engineering-harness-adaptive
llm-knowledge-base-maintainer
```

No runtime dependency back to Skill Kit.

## D5 — Context combines AIBoarding + Skill Kit KB maintainer

AIBoarding owns lifecycle/freshness/agent guidance.

Skill Kit KB semantics own canonical Markdown references, stable IDs, provenance, source ingestion, reconciliation, `llms.txt`, `manifest.jsonl`, and integrity.

## D6 — No embedding/vector/RAG subsystem in expected Harness Rig

Knowledge uses the canonical Skill Kit model plus normal repository/text navigation.

A future reversal requires a new explicit architectural decision backed by demonstrated failure.

## D7 — Trust protocol before Stable kernel
## D8 — Exact-state correctness is P0
## D9 — Assurance and Topology remain separate
## D10 — OpenSpec is default first-class SpecEngine
## D11 — No hard external runtime/package dependency
## D12 — Specs are agreed intent, not runtime truth
## D13 — Authority and state are separate freshness dimensions
## D14 — Authority and authorization are separate
## D15 — One source of truth per knowledge class
## D16 — Playwright is a gate/sensor
## D17 — One required repository verdict
## D18 — CHANGELOG-first migration traceability; full Git-history qualification in M11
## D19 — Delay public plugin SDK
## D20 — Execution optimization comes after topology
## D21 — Runtime resolution is requested/resolved/observed
## D22 — Hosted ordinary quality belongs in 0.5
## D23 — Native host conformance belongs in 0.6
## D24 — Recurrence is earned and host-owned
## D25 — OpenSpec artifact graphs remain engine-owned
## D26 — OpenSpec validation is necessary but insufficient
## D27 — OpenSpec archive is a guarded external transition
## D28 — Significant features need retirement criteria
## D29 — One agent is default
## D30 — Hooks have a high admission bar
## D31 — Mature feature inventory is explicit
## D32 — RigYard proposal reconciliation is mandatory and source-backed

## D33 — StateIdentity separates revision provenance from content/overlay identity

## D34 — AuthorizationGrant supersedes action-only authorization scope; no general IAM is added

## D35 — EvidenceReceipt is a claim/applicability envelope; native evidence remains native

## D36 — AcceptanceVerdict is qualified by subject and decision_for and is not a bearer authorization

## D37 — Security/trust rules have one canonical knowledge owner, not a new subsystem

## D38 — M1 trust contracts remain Experimental until M4 promotion criteria

## D39 — M2 uses CHANGELOG-backed source consolidation

M2 progression depends on explicit source baselines, target ownership, migration surfaces and capability dispositions recorded
in root `CHANGELOG.md`, not on object-complete Git history.

## D40 — Full Git-history preservation is a late M11 qualification gate

The history-import/rewrite/mapping/legacy-check requirements remain fail-closed, but they block M12/1.0 rather than M3.

M11 must reconcile `CHANGELOG.md` against the actual source histories.

# Open decisions

- exact StateIdentity serialization;
- authority canonicalization;
- AuthorizationGrant implementation representation after M3 consumer evidence;
- exact SpecEngine API;
- OpenSpec compatibility;
- canonical KB discovery/location convention;
- Context freshness metadata strategy;
- additional deterministic KB lint rules if justified;
- first Stable host/spec adapter;
- final RuntimeResolution vocabulary;
- recurrence terminal model;
- Final disposition of every active RigYard OpenSpec proposal under milestone M11.

## Related

- [Skill Kit knowledge-base integration for the Harness Rig Context plane](skill-kit-knowledge-base-context.md)
- [Roadmap](roadmap.md)
