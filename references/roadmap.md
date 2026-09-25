---
id: harness-rig-roadmap
title: Harness Rig implementation roadmap
summary: Ordered release roadmap from governance and exact-state evidence through monorepo migration, host conformance, Playwright
  integration, productization, and 1.0.
version: planning-baseline-2026-09-25-r8.8
updated: '2026-09-25'
provenance:
- Consolidated Harness Rig planning analysis through 2026-09-21
- Current AIBoarding, TacticSwitch, and Adaptive Engineering Harness implementation findings
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
- Harness Rig progressive remediation M2 execution attempt, 2026-09-24
- Public GitHub repository pages for AIBoarding, TacticSwitch, and Skill Kit rechecked 2026-09-24
- Local git 2.47.3 available; outbound git fetch failed because github.com DNS/network access is unavailable in the execution
  environment, 2026-09-24
- 'Harness Rig remediation sequencing decision: CHANGELOG-backed M2 and deferred Git-history qualification in M11, 2026-09-25'
- Harness Rig M3 experimental direct vertical-slice implementation and executable verification, 2026-09-25
- 'Local runtime evidence: Python 3.13.5 and Git 2.47.3, 2026-09-25'
- Harness Rig M4 core-promotion implementation and verification, 2026-09-25
- Harness Rig M5 Context convergence implementation and verification, 2026-09-25
- Harness Rig M6 OpenSpec SpecEngine implementation and verification, 2026-09-25
- Harness Rig M7 trusted repository enforcement implementation and verification, 2026-09-25
- Harness Rig M8 local-process host qualification and topology-boundary verification, 2026-09-25
---
# Progressive remediation overlay

```text
M0 / r8.0 PASS
M1 / r8.1 PASS
M2 / r8.2 PASS — CHANGELOG-backed source consolidation baseline
M3 / r8.3 PASS — thin complete Experimental direct vertical slice
M4 / r8.4 PASS — partial Stable core promotion and module-boundary convergence
M5 / r8.5 PASS — canonical Context knowledge/lifecycle ownership convergence
M6 / r8.6 PASS — OpenSpec first-class external SpecEngine and guarded archive
M7 / r8.7 PASS — same-subject trusted repository enforcement
M8 / r8.8 PASS — narrow local-process host capability and topology qualification
next: M9 gate platform, Playwright, architecture, and mutation verification
```

Full Git-history preservation is deferred to **M11**, before M12 / 1.0 qualification.

`AuthorityRef`, `AuthorizationGrant`, and `StateIdentity` are Stable v1. `EvidenceReceipt` and `AcceptanceVerdict` remain Experimental shared pending earned consumers.

# Roadmap rule

Canonical LLM-ready knowledge management is a **first-class Context responsibility**, not an optional future retrieval feature.

Migration traceability is progressive:

```text
M2  -> CHANGELOG + source provenance + capability dispositions
M11 -> full Git-history qualification and CHANGELOG reconciliation
```

# Releases

| Release | Primary result |
|---|---|
| `0.0.x` | Constitution, knowledge ownership, feature-admission |
| `0.1` | Small authority/state/evidence kernel |
| `0.2` | CHANGELOG-backed source consolidation baseline |
| `0.3` | Exact state/evidence + deterministic KB integrity |
| `0.4` | Context/Assurance/Topology convergence + KB reconciliation |
| `0.5` | Canonical CI including KB integrity |
| `0.6` | Host/SpecEngine capability platform |
| `0.7` | OpenSpec, architecture, Playwright first-class integrations |
| `0.8` | Product CLI, migration, distributions |
| `0.9` | Field hardening + full source-history qualification |
| `1.0` | Stable minimum-sufficient platform with qualified source provenance |

# 0.2 — source consolidation

Record and reconcile:

```text
AIBoarding
  -> Context lifecycle

Skill Kit llm-knowledge-base-maintainer
  -> Context canonical knowledge

TacticSwitch
  -> Topology

Skill Kit engineering-harness-adaptive
  -> Assurance
```

Use root `CHANGELOG.md` plus canonical source/provenance records.

Do not retain a runtime dependency on Skill Kit.

Full history preservation is not a 0.2 blocker.

# 0.3 — State/evidence + KB integrity

Fix exact-state defects and implement deterministic KB checks.

# 0.4 — Context convergence

Implemented in M5/r8.5: inspect-before-mutate, search-before-create, provenance/source observations, reconciliation, stable-ID lifecycle, freshness/drift, deterministic manifest/audit, root AGENTS projection freshness, and progressive disclosure.

# 0.5 — Repository enforcement

Add KB integrity to the canonical quality path and one repository verdict.

# 0.6 — Capability platform

Harness Doctor covers hosts, SpecEngine, gates, and Context/KB health.

# 0.7 — First-class integrations

Deliver OpenSpec, direct authority, command/test, knowledge integrity, architecture, Playwright and GitHub CI adapters/gates.

# 0.8 — Productization

Compact CLI, migration, distributions and release provenance.

# 0.9 — field hardening and source-history qualification

Run field pilots and simplification review.

Then execute the late source-history qualification:

```text
obtain object-complete source histories
rewrite/import to isolated legacy prefixes where required
produce old->new maps
verify tree equivalence
run relevant legacy checks
prove import-only merges
reconcile licenses/state/hooks/install surfaces
reconcile CHANGELOG.md against source history
resolve signed commit/tag fidelity requirements
```

This qualification must PASS before 1.0.

# 1.0

Require stable canonical Context knowledge, exact evidence, OpenSpec integration, at least one stable host, trusted CI,
migration/release provenance, successful M11 source-history qualification, and complexity retirement governance.

# First 15 PRs

1. Repository skeleton + constitution.
2. Feature-admission/retirement/change classes.
3. Core contracts.
4. StateIdentity.
5. Authority/state adversarial fixtures.
6. EvidenceReceipt.
7. Staleness/mutation tests.
8. AIBoarding source baseline + CHANGELOG migration entry.
9. TacticSwitch source baseline + CHANGELOG migration entry.
10. Skill Kit KB maintainer + Adaptive Harness source baselines and dispositions.
11. Converge legacy state + Context ownership.
12. Deterministic canonical knowledge integrity.
13. Assurance + Topology contract convergence.
14. Root affected-module CI + `ci / required`.
15. Governance/feature-admission checker.

# Next PRs

16. Direct/manual SpecEngine.
17. OpenSpec adapter.
18. OpenSpec authority fingerprint/spec-impact.
19. OpenSpec validation/config/archive guard.
20. Context source-ingest/reconciliation/audit.
21. Host Doctor/native conformance.
22. Architecture gate.
23. Playwright vertical slice.
24. Unified migration/distributions.
25. First real-project pilot + simplification review.
26. Full source-history qualification + CHANGELOG reconciliation.

## Related

- [History migration and monorepo plan](history-migration-and-monorepo-plan.md)
- [M2 source-surface inventory and capability dispositions](m2-source-surface-inventory-and-dispositions.md)
- [M11 Git-history qualification status](m11-git-history-qualification-status.md)
