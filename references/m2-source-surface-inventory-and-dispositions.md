---
id: harness-rig-m2-source-surface-inventory
title: M2 source-surface inventory and capability dispositions
summary: Source-backed M2 inventory and KEEP/ADAPT/REPLACE/RETIRE decisions for AIBoarding, TacticSwitch, and the relevant
  Skill Kit plugins before Git-history import.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Harness Rig M2 retry execution and source-surface inventory, 2026-09-25
- GitHub public repository pages for gustavo-meilus/aiboarding, tacticswitch, and skill-kit rechecked 2026-09-25
- Second local git ls-remote retry against GitHub failed at DNS resolution, 2026-09-25
- 'Harness Rig remediation sequencing decision: CHANGELOG-backed M2 and deferred Git-history qualification in M11, 2026-09-25'
---
# Status

This page completes the **source-side** migration inventory and capability classification possible before Git histories are
available.

It does not claim that history-preserving imports have occurred.

```text
M2-T01–T04 source baselines recorded in CHANGELOG: DONE
M2-T05 migration inventory / CHANGELOG trace: DONE
M2-T06 capability classification: DONE
```

# AIBoarding source surface

Public repository root rechecked 2026-09-25.

Observed top-level migration-relevant surfaces include:

```text
.agents/skills/
.aiboarding/
.claude-plugin/
.claude/
.codex-plugin/
.github/
hooks/
openspec/
skills/
templates/
tests/
tools/
AGENTS.md
CLAUDE.md
CHANGELOG.md
CONTRIBUTING.md
LICENSE
README.md
RELEASE-NOTES.md
```

Current public documentation describes:

- canonical `AGENTS.md` plus thin `CLAUDE.md`;
- `.aiboarding/state.json` lifecycle state;
- deterministic drift/update/audit/compression behavior;
- optional lifecycle hooks;
- Claude/Codex distribution surfaces;
- deterministic test suite plus bounded live-runtime evidence;
- MIT license.

## Disposition

```text
Context lifecycle / projection / onboarding:
  ADAPT

canonical factual knowledge that overlaps Harness Rig KB:
  CONVERGE INTO Context canonical knowledge owner

AGENTS.md projection:
  KEEP AS DERIVED/PROJECT-FACING SURFACE

.aiboarding state:
  MIGRATE ONLY WHAT IS STILL REQUIRED
  DO NOT KEEP AS A SECOND CANONICAL KNOWLEDGE/FRESHNESS SOURCE

hooks:
  RETAIN ONLY SURGICAL LIFECYCLE INVARIANTS THAT STILL EARN THEIR PLACE

legacy aliases/layout:
  MIGRATION COMPATIBILITY ONLY; RETIRE AFTER SUPPORTED WINDOW

native-runtime evidence:
  KEEP AS SOURCE-SPECIFIC EVIDENCE / DO NOT GENERALIZE BEYOND OBSERVED HOSTS
```

# TacticSwitch source surface

Public repository root rechecked 2026-09-25.

Observed migration-relevant surfaces include:

```text
.agents/skills/
.aiboarding/
.codex/
.github/
.orchestration/codex-capabilities/
benchmarks/
docs/
openspec/
references/
scripts/
templates/
tests/
AGENTS.md
CLAUDE.md
INSTALL.md
LICENSE
MANIFEST.sha256
README.md
SECURITY.md
USAGE.md
VERSION
manifest.json
```

Current public documentation describes:

- R0–R4 minimum-sufficient routing;
- direct work as default;
- fresh verifier semantics;
- one active writer for overlapping boundaries;
- fail-closed required worker/isolation behavior;
- installation/migration tooling;
- deterministic checksum manifest;
- experimental Codex/Claude/Copilot native support with explicit evidence gaps;
- MIT license.

## Disposition

```text
routing/topology protocol:
  ADAPT INTO Harness Rig Topology

one-writer / context-affinity / fresh-verifier semantics:
  KEEP SEMANTICS

risk / required-evidence policy:
  MOVE/KEEP IN Assurance, NOT Topology

repository/source state identity:
  REPLACE WITH Harness Rig StateIdentity

evidence acceptance:
  REPLACE/ADAPT TO Harness Rig EvidenceReceipt + AcceptanceVerdict

host capability observations:
  MOVE/ADAPT TO HostAdapter evidence

install/migration tooling:
  KEEP ONLY WHAT REMAINS NECESSARY AFTER MONOREPO CONVERGENCE

experimental host support claims:
  PRESERVE MATURITY/EVIDENCE BOUNDARIES; DO NOT PROMOTE BY IMPORT
```

# Skill Kit source surface

Public repository root rechecked 2026-09-25.

Observed top-level migration-relevant surfaces include:

```text
.agents/
.claude-plugin/
.github/
docs/
openspec/
plugins/
scripts/
tests/
LICENSE
README.md
SECURITY.md
```

The repository publicly identifies both relevant plugins:

```text
plugins/llm-knowledge-base-maintainer/
plugins/engineering-harness-adaptive/
```

The repository is MIT licensed.

# Skill Kit LLM knowledge-base maintainer disposition

```text
canonical Markdown references:
  KEEP SEMANTICS

stable logical IDs:
  KEEP

source-as-evidence discipline:
  KEEP

search-before-create:
  KEEP

reconciliation:
  KEEP

conflicts/evidence gaps:
  KEEP

llms.txt:
  KEEP AS CURATED NAVIGATION

manifest.jsonl:
  KEEP AS DERIVED EXHAUSTIVE INVENTORY

whole-collection structural integrity:
  KEEP

runtime dependency on Skill Kit:
  DO NOT RETAIN

plugin packaging/marketplace metadata:
  HISTORICAL / MIGRATION INPUT ONLY unless Harness Rig later ships an equivalent distribution
```

Target owner:

```text
modules/context/knowledge-base
```

# Skill Kit Adaptive Engineering Harness disposition

```text
risk separate from reasoning difficulty:
  KEEP SEMANTICS

progressive verification / verification ladder:
  KEEP / ADAPT INTO Assurance

executable oracle emphasis:
  KEEP

independent review requirement:
  KEEP WHEN RISK/POLICY REQUIRES IT

prepared read-only roles:
  ADAPT; DO NOT REQUIRE MULTI-AGENT BY DEFAULT

canonical verifier discovery:
  KEEP / ADAPT

stop/completion gating:
  KEEP ONLY WHERE IT ENFORCES A REAL INVARIANT

legacy workspace snapshot / dirty-path state:
  REPLACE

legacy evidence/state coupling:
  REPLACE WITH M1 EXPERIMENTAL trust protocol after M3/M4 evidence

topology/routing overlap:
  REMOVE FROM Assurance during convergence
```

Target owner:

```text
modules/assurance
```

# More With Less

The canonical More With Less plugin remains a governance/source dependency, not an M2 runtime/history-import requirement for
the Harness Rig product.

Its role is:

```text
feature admission
complexity pressure
reuse before adding
verification proportionality
retirement/deletion criteria
```

Do not copy its method into multiple Harness Rig modules as competing policy implementations.

# M2 source-side migration inventory

The following inventory classes are now defined for post-import verification:

| Inventory class | AIBoarding | TacticSwitch | Skill Kit relevant paths |
|---|---|---|---|
| licenses/notices | source root MIT license | source root MIT license | source root MIT license |
| state files | `.aiboarding/`, lifecycle state | `.aiboarding/`, orchestration/capability state | plugin-specific state/hooks only |
| hooks | lifecycle hooks | host/package mechanisms where present | Adaptive Harness completion hook |
| host/plugin manifests | Claude/Codex plugin metadata | manifest/install/adapters | marketplace/plugin metadata |
| install/update | plugin/lifecycle install | Python install/verify/migration | marketplace/plugin install |
| generated distributions | templates/host packages | templates/manifests/checksum surface | packaged plugin copies |
| schemas/contracts | onboarding/state contracts | routing/control-packet/manifest contracts | KB metadata + Assurance rules |
| tests/evals | deterministic suite + bounded live evidence | tests/benchmarks/source verification | tests and plugin verification |
| OpenSpec | project specs/changes | project integration/spec material | repository OpenSpec material |
| agent/role definitions | skills/agent guidance | worker/verifier role packages | Adaptive Harness roles |
| legacy compatibility | old AIBOARDING lifecycle | deprecated alias/protocol surfaces | legacy plugin/package forms |

This source-side inventory is the M2 migration-surface baseline and is summarized in root `CHANGELOG.md`. Actual imported-prefix reconciliation is deferred to M11.

# Import-time deletion pressure

History preservation does **not** justify preserving every mechanism in the final architecture.

After import verification, convergence work should seek to delete:

```text
duplicate state identity mechanisms
duplicate evidence envelopes
duplicate Context truth/freshness stores
duplicate risk/routing ownership
duplicate host capability stores
obsolete installation aliases
obsolete hooks made redundant by native host behavior
generated copies without one canonical authored source
```

# Remaining blocker

Old→new commit mappings are no longer an M2 requirement. Full Git-history mapping and imported-prefix reconciliation are deferred to M11.

## Related

- [M2 history-import execution status](m11-git-history-qualification-status.md)
- [History migration and monorepo plan](history-migration-and-monorepo-plan.md)
- [Current system baseline](current-system-baseline.md)
