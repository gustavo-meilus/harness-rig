---
id: harness-rig-source-register
title: Source register
summary: Primary repository sources and external references used to ground the Harness Rig architecture, governance, migration,
  and runtime-harness recommendations.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- Sources directly inspected or explicitly supplied during Harness Rig research through 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Harness Rig expected-feature synthesis, refreshed 2026-09-21
- Skill Kit llm-knowledge-base-maintainer v1.1.0, SKILL.md and DEFAULT_LAYOUT.md, inspected 2026-09-24
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
- Harness Rig M2 retry execution and source-surface inventory, 2026-09-25
- GitHub public repository pages for gustavo-meilus/aiboarding, tacticswitch, and skill-kit rechecked 2026-09-25
- Second local git ls-remote retry against GitHub failed at DNS resolution, 2026-09-25
- Harness Rig M2 retry 3 native-Git migration tooling implementation and synthetic verification, 2026-09-25
- Git 2.47.3 native plumbing used for synthetic history rewrite/verification, 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient migration-tooling rule retained, 2026-09-25
- Harness Rig M2 retry 4 import-orchestrator implementation and synthetic end-to-end verification, 2026-09-25
- Git 2.47.3 native bundle/clone/fsck/plumbing used for synthetic import-pipeline evidence, 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient migration-tooling doctrine retained, 2026-09-25
- Harness Rig M2 retry 5 verification-gate tooling implementation and synthetic adversarial verification, 2026-09-25
- AIBoarding public README rechecked 2026-09-25 for canonical offline check `bash tests/run.sh`
- TacticSwitch public README rechecked 2026-09-25 for install/verify commands and current evidence limits
- Skill Kit public repository rechecked 2026-09-25; tests/scripts surfaces confirmed but no complete deterministic filtered-plugin
  command inferred
- 'Harness Rig remediation sequencing decision: CHANGELOG-backed M2 and deferred Git-history qualification in M11, 2026-09-25'
- Harness Rig M3 experimental direct vertical-slice implementation and executable verification, 2026-09-25
- 'Local runtime evidence: Python 3.13.5 and Git 2.47.3, 2026-09-25'
---
# Current project sources

## AIBoarding

- Loop Engineering boundary: https://github.com/gustavo-meilus/aiboarding/blob/main/docs/LOOP-ENGINEERING.md
- Contribution policy: https://github.com/gustavo-meilus/aiboarding/blob/main/CONTRIBUTING.md
- Repository: https://github.com/gustavo-meilus/aiboarding

Key supported claims: durable context ownership; no agent dispatch or merge gating; deterministic/small hook preference; context freshness/compression/audit role.

## TacticSwitch

- Repository: https://github.com/gustavo-meilus/tacticswitch
- Governance: https://github.com/gustavo-meilus/tacticswitch/blob/main/docs/GOVERNANCE.md
- Contributing/evidence policy: https://github.com/gustavo-meilus/tacticswitch/blob/main/CONTRIBUTING.md
- Normative protocol: https://github.com/gustavo-meilus/tacticswitch/blob/main/templates/skills/tactic-work-protocol/references/protocol.md
- Control packets: https://github.com/gustavo-meilus/tacticswitch/blob/main/templates/skills/tactic-work-protocol/references/control-packets.md
- Durable state schema: https://github.com/gustavo-meilus/tacticswitch/blob/main/templates/skills/tactic-work-protocol/references/state.schema.json

Key supported claims: R0-R4 minimum topology; ownership; fresh verification; fail-closed independence; exact-state evidence; mutating validation rule; evidence-based support promotion.

## Skill Kit / Adaptive Engineering Harness

- Repository: https://github.com/gustavo-meilus/skill-kit
- Engineering discipline: https://github.com/gustavo-meilus/skill-kit/blob/main/plugins/engineering-harness-adaptive/skills/engineering-discipline/SKILL.md
- Shared hook helpers: https://github.com/gustavo-meilus/skill-kit/blob/main/plugins/engineering-harness-adaptive/hooks/harness_common.py
- Stop hook: https://github.com/gustavo-meilus/skill-kit/blob/main/plugins/engineering-harness-adaptive/hooks/stop_gate.py

Key supported claims: risk/difficulty separation; deterministic-first verification ladder; circular-oracle warning; current dirty-path state implementation; current pre-verifier snapshot behavior.


# User-supplied TacticSwitch proposal packages

## Earlier v3 package

Source artifact:

```text
tacticswitch-openspec-proposals-v3.zip
```

This is the earlier, narrower set that reduced runtime execution to post-route hints, kept recurrence pure/bounded, and avoided new control planes.

Use [TacticSwitch v3 extension disposition](tacticswitch-v3-extension-disposition.md) for its historical Harness Rig disposition.

## Richer loop/runtime package

Source artifact:

```text
tacticswitch-openspec-loop-proposals.zip
```

Reviewed source files include:

```text
README.md
VALIDATION.md
ALIGNMENT-REVIEW.md

openspec/changes/add-runtime-execution-policy/
  proposal.md
  design.md
  tasks.md
  specs/**

openspec/changes/add-loop-integration-contract/
  proposal.md
  design.md
  tasks.md
  specs/**

openspec/changes/operationalize-loop-assurance/
  proposal.md
  design.md
  tasks.md
  specs/**
```

Supported proposal facts:

- topology is selected before compute/runtime allocation;
- change risk is separate from reasoning difficulty;
- execution constraints can be required, preferred, or advisory;
- runtime facts distinguish requested, resolved, and observed states;
- adapter/runtime resolution uses explicit bounded statuses and preserves unknowns as evidence gaps;
- recurrence requires objective completion, finite budgets, progress/failure fingerprints, changed-action eligibility, least authority, explicit side-effect gates, compact continuation, and idempotency;
- recurrence leaves scheduling/event delivery/persistence backend ownership to the host;
- hosted ordinary correctness consumes one canonical quality command;
- required GitHub check identities should be observed from real runs before enforcement;
- slow/native assurance is demand-driven by default and may be scheduled only after demonstrated freshness need and stable value;
- native unavailable/blocked conditions remain evidence gaps;
- the archive still requires strict OpenSpec CLI validation in the authoritative repository.

Harness Rig intentionally does **not** copy every source requirement unchanged. Notably, the source proposal requires both finite cycle and wall-clock budgets; Harness Rig's current planning decision keeps finite cycles mandatory while treating wall-clock/token/cost accounting as optional or host-owned.

Use [TacticSwitch loop and runtime-policy proposals disposition](tacticswitch-loop-proposals-disposition.md) for the current architectural mapping.




# RigYard current supplied source snapshot

Primary supplied source inspected 2026-09-24:

```text
rigyard_current.zip
```

Current snapshot facts used by Harness Rig planning:

- package: `rigyard` `0.1.1`, TypeScript/Node.js 20+;
- 90 files under `src/`, 101 files under `test/`, and 360 files under `dist/`;
- 11 archived OpenSpec change directories;
- exactly 8 active OpenSpec change directories;
- retained formal `rigyard/codex-host-evidence/v1` evidence for the validated Codex/Linux v0.1 boundary;
- experimental/unqualified Claude Code and GitHub Copilot CLI readiness records;
- v0.3 isolated-writer implementation evidence plus an explicit statement that no formal
  `rigyard/codex-isolated-writer-host-evidence/v1` packet is retained;
- stale pre-release handoff/state documents retained as historical transition evidence.

The ZIP contains no `.git/` directory. It therefore supports source/proposal/evidence inspection but not independent
reconstruction of the current Git branch, repository history, or exact live repository state.

See [RigYard current source and verification baseline](rigyard-current-source-and-verification-baseline.md).

# RigYard / More-With-Less sources

## RigYard

Requested public repository:

```text
https://github.com/gustavo-meilus/rigyard/
```

Public-source recheck on 2026-09-21:

- repository fetch returned 404;
- raw `main/README.md` fetch returned 404;
- public GitHub search did not expose repository source.

Therefore no current implementation, dependency, test, release, or planned-change facts are asserted from RigYard source in this collection.

The canonical [RigYard premise and minimum-sufficient feature admission](rigyard-premise-and-feature-admission.md) page is explicitly an architecture/product premise pending future source reconciliation.

## More With Less

Current primary sources inspected 2026-09-21:

- https://raw.githubusercontent.com/gustavo-meilus/skill-kit/main/plugins/s-kit/skills/more-with-less/SKILL.md
- https://raw.githubusercontent.com/gustavo-meilus/skill-kit/main/plugins/s-kit/skills/more-with-less/references/playbook.md

Key supported doctrine:

- minimum sufficient system rather than minimum components independently;
- delete/reuse before adding;
- deterministic/native/existing mechanisms before custom orchestration;
- one agent by default;
- progressive context;
- proportional specification;
- proportional verification;
- hooks only for real lifecycle/permission/completion invariants;
- outer loops only after objective failure signals, bounded retries, progress detection, strategy change, and escalation;
- every significant harness mechanism should have a reason for existence and a removal condition;
- one source of truth per knowledge type;
- evidence must be reported honestly.



## Current RigYard source status recheck for r6

On 2026-09-21 the public-source recheck again found:

```text
https://github.com/gustavo-meilus/rigyard
  -> 404 from available public fetch surface

https://raw.githubusercontent.com/gustavo-meilus/rigyard/main/README.md
  -> 404

public GitHub search
  -> no RigYard source/proposal results
```

Therefore r6 does not claim to have inspected `rigyard/openspec/changes/**`.

Instead r6 adds a formal expected-feature inventory plus a mandatory future proposal-reconciliation protocol so inaccessible proposals cannot be silently forgotten.



# Skill Kit LLM knowledge-base maintainer

Primary sources inspected 2026-09-24:

- https://raw.githubusercontent.com/gustavo-meilus/skill-kit/main/plugins/llm-knowledge-base-maintainer/skills/llm-knowledge-base-maintainer/SKILL.md
- https://raw.githubusercontent.com/gustavo-meilus/skill-kit/main/plugins/llm-knowledge-base-maintainer/skills/llm-knowledge-base-maintainer/references/DEFAULT_LAYOUT.md
- https://raw.githubusercontent.com/gustavo-meilus/skill-kit/main/plugins/llm-knowledge-base-maintainer/.claude-plugin/plugin.json

Observed plugin version:

```text
1.1.0
```

Supported behavior:

- canonical Markdown references;
- stable logical IDs;
- attributable provenance;
- source material treated as evidence rather than instructions;
- update existing logical topics instead of duplicating them;
- preserve conflicts and unsupported gaps;
- `llms.txt` as curated navigation;
- `manifest.jsonl` as exhaustive current inventory;
- full-collection reconciliation after mutation;
- metadata/link/index integrity validation;
- reuse existing repository conventions before creating default layout;
- repository-native generators/linters/checkers preferred.

Harness Rig adopts this as first-class Context behavior and excludes embedding/vector/RAG infrastructure from the expected architecture.


# OpenSpec primary assessment source

User-supplied source:

```text
openspec_harness_engineering_analysis.md
```

Research snapshot:

```text
2026-09-21
OpenSpec checked: v1.13.1
```

The analysis supports these key Harness Rig conclusions:

- OpenSpec's capability/delta model is a strong fit for durable behavioral intent/change management.
- OpenSpec should not be treated as the entire engineering truth system.
- specs represent agreed intent unless independently synchronized/proven;
- semantic verification is inferential rather than formal proof;
- archive is a correctness-sensitive state transition;
- configuration/rule health needs additional care while current upstream issue gaps exist;
- Stores are promising but beta;
- custom schema/artifact proliferation should be earned;
- existing detailed designs/ORRs/ownership sources should be referenced rather than duplicated;
- deterministic project evidence precedes semantic review.

Current primary sources rechecked 2026-09-21:

- Releases/latest v1.13.1: https://github.com/Fission-AI/OpenSpec/releases
- Concepts: https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md
- Overview: https://github.com/Fission-AI/OpenSpec/blob/main/docs/overview.md
- Default spec-driven schema: https://github.com/Fission-AI/OpenSpec/blob/main/schemas/spec-driven/schema.yaml
- CLI / Stores beta: https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md
- Issue #1892, malformed config can exit successfully: https://github.com/Fission-AI/OpenSpec/issues/1892
- Issue #1891, malformed rules can be dropped: https://github.com/Fission-AI/OpenSpec/issues/1891
- Issue #1890, archive hardening proposal: https://github.com/Fission-AI/OpenSpec/issues/1890
- Issue #1436, Store repository topology: https://github.com/Fission-AI/OpenSpec/issues/1436

Harness Rig intentionally strengthens the source conclusion:

> OpenSpec is the default external SpecEngine for behavior-changing work, but Harness Rig must never take a hard package/runtime dependency on it.

# OpenSpec brainstorming source

User-supplied archive:

```text
openspec-brainstorming-improved.zip
```

Relevant conclusions incorporated:

- recover existing context before questioning;
- distinguish observed facts, decisions, assumptions, and open questions;
- normalize the smallest coherent behavior change;
- obtain approval before materializing planning artifacts;
- use the spec engine's actual artifact graph/instructions;
- strict validation is separate from semantic coherence review;
- planning approval is separate from implementation/apply authorization.


# Packaging standards

- LLM Knowledge Base Maintainer: https://github.com/gustavo-meilus/skill-kit/tree/main/plugins/llm-knowledge-base-maintainer/skills/llm-knowledge-base-maintainer
- Lite Writing: https://github.com/gustavo-meilus/skill-kit/tree/main/plugins/lite-writing/skills/lite-writing

This collection follows their stable-ID, canonical-reference, provenance, `llms.txt`, `manifest.jsonl`, concise-prose, and integrity-check conventions.

# Harness engineering

- OpenAI, Harness engineering: https://openai.com/index/harness-engineering/
- Google Developers Blog, Anatomy of Harness Engineering: https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents/

Use: repository knowledge as system of record; application legibility; enforceable controls; evaluation of the harness itself.

# Repository governance and release sources

- GitHub CODEOWNERS: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- GitHub rulesets: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- GitHub Actions workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Artifact attestations: https://docs.github.com/en/actions/concepts/security/artifact-attestations
- Immutable releases: https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases
- Semantic Versioning: https://semver.org/
- Kubernetes Enhancement Proposal process: https://github.com/kubernetes/enhancements/blob/master/keps/sig-architecture/0000-kep-process/README.md
- git-filter-repo documentation: https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt

Use: CODEOWNERS/ruleset boundaries; proposal/reviewer/approver structure; history-preserving monorepo imports; 0.x/1.0 API semantics; release provenance.

# Runtime and architecture sources

- Playwright coding agents: https://playwright.dev/docs/getting-started-cli
- Playwright test agents: https://playwright.dev/docs/test-agents
- Robert C. Martin, The Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

Use: browser-runtime evidence; Planner/Generator/Healer boundary; architecture dependency direction and testability.

# Earlier verification research corpus

- Alexander Hinojosa, The Tests Were Green. They Were Lying.: https://www.linkedin.com/pulse/tests-were-green-lying-alexander-hinojosa-eeolc
- AI Coding Partner Field Guide: https://alexanderhinojosa.com/ai-coding-partner-field-guide/
- Multi-Agent Coding Playbook: https://alexanderhinojosa.com/multi-agent-coding-playbook/
- Anthropic Claude Code best practices: https://www.anthropic.com/engineering/claude-code-best-practices

These are useful operational sources. Treat Hinojosa's model-diversity and review-round recommendations as practitioner experience, not universal controlled results.

# Evidence boundary

Repository code and current official documentation should be rechecked before implementing version-sensitive behavior.

Prepared OpenSpec artifacts remain proposals until applied and verified.

This register is a provenance map, not a substitute for reading the cited source when a material implementation or compatibility decision depends on it.

## Related

- [Research foundations](research-foundations.md)
- [TacticSwitch v3 extension disposition](tacticswitch-v3-extension-disposition.md)
- [Usage and scope](usage-and-scope.md)

# M1 trust-protocol primary sources

"
    "- Skill Kit More With Less canonical skill/playbook;
"
    "- supplied RigYard core acceptance evidence, durable worker evidence, result acceptance, one-use attempt capability, "
    "workspace baseline source/tests;
"
    "- Git official status/diff/submodule documentation;
"
    "- Node.js official child_process documentation.

"
    "Reviewer findings were treated as candidate failure analysis, not authority.


# M2 history-import source status

Rechecked 2026-09-24:

- public AIBoarding repository page: `main`, 89 commits visible;
- public TacticSwitch repository page: `main`, 11 commits visible;
- public Skill Kit repository page: `main`, 14 commits visible;
- local Git executable: `git 2.47.3`;
- local Git fetch/ls-remote to GitHub: unavailable because the execution environment cannot resolve/reach `github.com`;
- no complete Git bundle/mirror/.git object store for the three mandatory source repositories is attached.

Public page visibility proves that histories exist; it does not make those histories importable or reproducibly mappable.

See [M2 history-import execution status](m11-git-history-qualification-status.md).


# M2 retry 2 source observations

Rechecked 2026-09-25:

- AIBoarding public root exposes lifecycle/plugin/hooks/OpenSpec/tests/tools surfaces and MIT licensing;
- TacticSwitch public root exposes routing templates, tests, benchmarks, OpenSpec material, install/migration scripts,
  checksum manifest, host capability state, and MIT licensing;
- Skill Kit public root exposes plugins, tests, OpenSpec material, marketplace metadata, and MIT licensing;
- relevant Skill Kit plugins are publicly listed as Adaptive Engineering Harness and LLM Knowledge Base Maintainer;
- no GitHub repository connector is available in this execution context;
- local Git transport to GitHub remains unavailable due DNS/network resolution;
- GitHub browser access is sufficient for source-surface inventory, not for history-preserving import.

See [M2 source-surface inventory and capability dispositions](m2-source-surface-inventory-and-dispositions.md).


# M2 retry 3 migration-tooling evidence

Implemented and executed 2026-09-25 using Git 2.47.3 native plumbing:

- `verification/m2-history-rewriter.py`;
- `verification/m2-verify-rewrite.py`;
- `verification/m2-synthetic-migration-tooling-evidence.json`.

Synthetic tests cover a branch/merge/tag full-prefix rewrite, a filtered Skill-Kit-style multi-path rewrite, and deliberate
mapping tampering. The tooling passed those tests.

This evidence validates the migration helper only; it is not evidence that AIBoarding/TacticSwitch/Skill Kit histories have
been imported.

# M2 retry 4 prepared-pipeline evidence

Implemented and synthetically verified 2026-09-25: strict preflight v2, three-source import orchestrator, verified import-bundle generation, target staging, mode/symlink preservation, Skill Kit filtering, and explicit tag-fidelity limits. Machine evidence: `verification/m2-import-orchestrator-synthetic-evidence.json`. This is tooling evidence, not real source-import evidence.


# M2 retry 5 verification-gate evidence

Rechecked/implemented 2026-09-25:

- AIBoarding public README explicitly documents `bash tests/run.sh` as its deterministic suite;
- TacticSwitch public README documents Python install/verify commands and current support/evidence limits;
- Skill Kit public root confirms tests/scripts and both relevant plugins, but no complete filtered-plugin check command was
  inferred from the inspected root page;
- M2 reproducibility, legacy-check, import-only and surface-inventory helpers passed synthetic/adversarial fixtures.

Machine evidence:

`verification/m2-verification-tooling-synthetic-evidence.json`

These are migration-verification-tool facts, not proof of completed real imports.


# Migration traceability sequencing

Decision effective 2026-09-25:

- M2 uses root `CHANGELOG.md` plus canonical source/provenance records as the source-consolidation ledger.
- Complete Git histories are no longer required for M2 progression.
- Existing native-Git migration tooling is retained for M11.
- M11 must reconcile the CHANGELOG against actual source histories before M12 / 1.0 qualification.

This is a sequencing change, not a claim that CHANGELOG carries the same evidence as Git history.


# M3 executable implementation evidence

Executed 2026-09-25:

- local Python 3.13.5;
- local Git 2.47.3;
- `prototype/harness_rig/` Experimental implementation;
- `prototype/tests/test_m3_vertical_slice.py`;
- 22/22 unittest cases passed;
- all M1-F01 through M1-F16 mapped to passing executable tests;
- direct CLI smoke produced command-gate `PASS` and merge `ACCEPTED`.

Machine evidence:

```text
verification/m3-unittest-output.txt
verification/m3-fixture-results.json
verification/m3-verification-record.json
verification/m3-cli-smoke.json
```

This is local direct-provider evidence. It is not evidence for OpenSpec, hosted CI, remote hosts, or Stable contract maturity.
