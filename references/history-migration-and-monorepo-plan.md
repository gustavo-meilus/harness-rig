---
id: harness-rig-history-migration-and-monorepo-plan
title: History migration and monorepo plan
summary: History-preserving repository consolidation plan that separates source migration from architectural refactoring and
  runtime consolidation.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- git-filter-repo documentation, accessed 2026-09-21
- Current AIBoarding, TacticSwitch, and Skill Kit repository layouts, assessed 2026-09-21
- Skill Kit llm-knowledge-base-maintainer v1.1.0, SKILL.md and DEFAULT_LAYOUT.md, inspected 2026-09-24
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- Harness Rig progressive remediation M2 execution attempt, 2026-09-24
- Public GitHub repository pages for AIBoarding, TacticSwitch, and Skill Kit rechecked 2026-09-24
- Local git 2.47.3 available; outbound git fetch failed because github.com DNS/network access is unavailable in the execution
  environment, 2026-09-24
- Harness Rig M2 retry execution and source-surface inventory, 2026-09-25
- GitHub public repository pages for gustavo-meilus/aiboarding, tacticswitch, and skill-kit rechecked 2026-09-25
- Second local git ls-remote retry against GitHub failed at DNS resolution, 2026-09-25
- Harness Rig M2 retry 3 native-Git migration tooling implementation and synthetic verification, 2026-09-25
- Git 2.47.3 native plumbing used for synthetic history rewrite/verification, 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient migration-tooling rule retained, 2026-09-25
- 'Harness Rig remediation sequencing decision: CHANGELOG-backed M2 and deferred Git-history qualification in M11, 2026-09-25'
---
# Migration strategy

Harness Rig uses a two-phase migration/provenance strategy.

```text
M2
  CHANGELOG-backed source consolidation baseline

M11
  full Git-history qualification / reconciliation
```

This avoids blocking early implementation on object-complete source histories while preserving a late release-quality
history/provenance gate before 1.0.

# M2 — CHANGELOG-backed source consolidation

M2 requires:

```text
source/capability identity
source checked/reconciled date
target Harness Rig owner
KEEP / ADAPT / REPLACE / DELETE_AFTER_MIGRATION / HISTORICAL_ONLY disposition
migration-surface inventory
material semantic-change ledger in root CHANGELOG.md
```

M2 does **not** require:

```text
Git bundles
history rewriting
old→new commit maps
tag rewriting
import-only merge commits
legacy checks from rewritten prefixes
```

Those requirements are deferred to M11.

# CHANGELOG rule

Root `CHANGELOG.md` is the near-term migration ledger.

Every material source-derived change should be attributable to:

```text
source project/capability
source location/snapshot
date
target module
disposition
semantic change
verification/evidence
```

Do not silently port source behavior without recording the migration/convergence decision.

# M11 — full source-history qualification

Before final 1.0 qualification, M11 must reconcile the CHANGELOG against object-complete source histories.

Target source histories:

```text
AIBoarding
TacticSwitch
Skill Kit relevant paths:
  plugins/llm-knowledge-base-maintainer/
  plugins/engineering-harness-adaptive/
```

RigYard history is required only if Harness Rig chooses to preserve it as part of the final product migration rather than
using its supplied source/evidence snapshot as an external source baseline.

# Late history prefixes

If imported, use isolated legacy prefixes:

```text
legacy/aiboarding/
legacy/tacticswitch/
legacy/skill-kit/
```

For Skill Kit, retain both relevant plugin paths in one filtered history so a source commit touching both capabilities remains
one source event.

# M11 history evidence

M11 retains:

```text
source repository/ref inventory
source -> rewritten commit mapping
source tag -> namespaced tag mapping
filter/rewrite tool version
filter arguments
tree-equivalence verification
legacy deterministic-check evidence
import-only proof
license/state/hook/install reconciliation
CHANGELOG <-> history reconciliation
```

# Existing migration tooling

The already-implemented native-Git migration tooling is retained as **M11 qualification tooling**, not an M2 progression
requirement.

See:

- [M11 Git-history qualification status](m11-git-history-qualification-status.md)
- [M11 history rewrite tooling](m11-history-rewrite-tooling.md)
- [M11 history import orchestrator](m11-history-import-orchestrator.md)
- [M11 history verification gate tooling](m11-history-verification-gate-tooling.md)

# Completion model

M2 completion means:

```text
the source baselines, ownership, dispositions and migration surfaces are explicit
and recorded in CHANGELOG.md
```

M11 completion means:

```text
the late source-history provenance has been reconciled and independently verified
before M12 / 1.0 qualification
```

This separation preserves traceability without forcing historical Git mechanics to block the architectural vertical slice.

## Related

- [M2 source-surface inventory and capability dispositions](m2-source-surface-inventory-and-dispositions.md)
- [Roadmap](roadmap.md)
