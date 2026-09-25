---
id: harness-rig-repository-governance-and-change-model
title: Repository governance and change model
summary: Governance model for a modular monorepo that can add features without turning core contracts into a moving monolith.
version: planning-baseline-2026-09-25-r8.7
updated: '2026-09-25'
provenance:
- TacticSwitch docs/GOVERNANCE.md and CONTRIBUTING.md, accessed 2026-09-21
- AIBoarding CONTRIBUTING.md, accessed 2026-09-21
- Kubernetes Enhancement Proposal process, accessed 2026-09-21
- GitHub CODEOWNERS and rulesets documentation, accessed 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- Harness Rig M7 repository enforcement implementation and verification, 2026-09-25
---
# Governance objective

The monorepo should make high-impact changes durable and reviewable without requiring heavy design process for routine module work.

# Root governance

Maintain one root `GOVERNANCE.md` covering:

- authority;
- project roles;
- change classes;
- feature maturity;
- schema governance;
- compatibility;
- review;
- security escalation;
- release authority;
- deprecation;
- emergency changes.

Modules may have owners and local contribution notes, but they should not develop competing mini-constitutions.

# Change classes

| Class | Meaning | Examples | Required process |
|---|---|---|---|
| C0 | Editorial/internal | typo, comment, non-semantic fixture | focused CI |
| C1 | Module-local | bug fix behind an existing contract | module CI + owner review |
| C2 | Cross-module/public behavior | host adapter, new public gate behavior | integration CI + affected owners + change note |
| C3 | Constitutional | core contract, persistent schema, trust/security boundary, governance | HRP + compatibility evidence + approver |

Classification should be machine-assisted from changed paths and declared metadata, not solely self-declared by the author.

# Harness Rig Proposals

Use an **HRP** only for changes with durable architectural or public impact.

Require an HRP for:

- new module;
- core contract change;
- persistent schema change;
- cross-module lifecycle change;
- new trust or authority boundary;
- Stable feature graduation;
- stronger public compatibility promise;
- security model change;
- incompatible removal or deprecation.

A proposal should record:

```text
problem
motivation
affected boundaries
alternatives
compatibility
security/authority implications
schema implications
test strategy
rollback
graduation criteria
author
reviewers
approvers
status
```

The Kubernetes KEP process is a useful structural precedent: durable proposal metadata, distinct reviewers/approvers, historical states, and explicit implementation readiness. Harness Rig should use the pattern without Kubernetes-scale bureaucracy.

# ADRs

Use ADRs for accepted architectural decisions and rationale.

Distinguish:

- HRP: should a capability or change exist?
- ADR: what architectural decision was made and why?

# Ownership

Use `.github/CODEOWNERS` for review routing.

Do not rely on CODEOWNERS as the complete governance engine. Critical cross-module or constitutional requirements should be checked by Harness Rig's own governance CI because path ownership and required-review semantics do not express every required combination of approvals or evidence.

# M7 governance-sensitive enforcement

M7 makes CI/resolver/policy/trust-oracle changes machine-detectable C3-sensitive paths. Such changes require an explicit `governance` CI obligation in addition to ordinary and KB-integrity obligations. The exact current path policy is `governance/ci-policy.json`.

This local mechanism complements, but cannot replace, protected-branch/ruleset review controls. A deployed repository should require `ci / required` and real code-owner or equivalent approval for those paths. r8.7 intentionally does not invent a CODEOWNERS identity.

# Feature maturity

Every externally meaningful capability can be:

```text
experimental
beta
stable
deprecated
```

Promotion requires explicit graduation evidence.

A product release can be Stable while individual adapters or gates remain Experimental, provided their maturity is clear.

# Core admission rule

Adding behavior behind an existing contract is easier than changing core.

A core change should answer:

> Which concrete requirement cannot be represented through existing contracts?

If no concrete requirement exists, keep the behavior outside core.



# Feature-admission and retirement governance

Every C2/C3 feature that adds a new:

```text
concept
persistent state
interface
dependency
tool
hook
agent role
handoff
orchestration layer
always-loaded context
```

must document:

```text
concrete repeated failure
existing mechanism considered/rejected
minimum sufficient proposed mechanism
new authority/tool/state surface
verification/evaluation plan
degraded behavior
retirement/downgrade condition
```

A feature can be rejected even if technically useful when its total maintenance/coordination cost exceeds the demonstrated gap.

## Core admission

Core additions require an HRP unless they are a non-semantic implementation refactor of an accepted contract.

The proposal must explain why adapter/module/gate ownership is insufficient.

## Complexity review

Before Stable graduation and periodically afterward, ask:

```text
Does this mechanism still catch a distinct failure?
Can another now-stable mechanism replace it?
Can it become optional?
Can it be deleted?
Can context/state/interfaces be collapsed?
```

Feature maturity is therefore allowed to move:

```text
experimental -> beta -> stable
```

and also:

```text
stable -> deprecated -> removed
```

when the failure it addressed no longer justifies its cost.


# Specification-engine governance

OpenSpec/custom schema decisions can change engineering process policy.

Treat these as higher-governance changes when they materially alter:

- which artifacts must exist before implementation;
- which planning rules are injected;
- what counts as apply-ready;
- authority fingerprint semantics;
- archive postconditions;
- shared Store/repository planning policy.

Do not require an HRP for ordinary OpenSpec changes representing product work.

Consider an HRP/C3 change for a new organization-wide OpenSpec schema or Harness Rig `SpecEngine` contract change.

Do not make beta OpenSpec Store/file formats part of Harness Rig's stable public API.

## Related

- [CI, review, versioning, and release governance](ci-review-and-release-governance.md)
- [Decision log](decision-log.md)
