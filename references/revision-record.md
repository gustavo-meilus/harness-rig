---
id: harness-rig-progressive-revision-record
title: Harness Rig progressive revision record
summary: Current progressive-remediation milestone status, verification result, evidence limits, and next permitted milestone.
version: planning-baseline-2026-09-25-r8.7
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation M0-M6 execution and verification, 2026-09-24 through 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient engineering doctrine, applied 2026-09-25
- GitHub Actions workflow, merge_group, fork-token, required-check and pull_request_target security documentation rechecked 2026-09-25
- Harness Rig M7 trusted repository enforcement implementation and adversarial verification, 2026-09-25
---
# Current revision

```text
milestone: M7
package revision: r8.7
result: PASS
date: 2026-09-25
next allowed milestone: M8
resume task: M8-T01
```

# M7 implemented boundary

M7 adds one repository-local CI obligation resolver and one strict final required-verdict validator. These schemas remain Experimental application evidence and are not promoted into Stable core.

```text
event subject + evaluated SHA + changed paths
  -> ci obligation artifact
  -> ordinary / kb-integrity / conditional governance results
  -> ci / required
```

The final verdict recomputes mandatory obligations from the current checked policy and requires exactly one `PASS` result per mandatory obligation with matching SHA, event subject, producer and deterministic result identity.

# GitHub workflow boundary

The retained workflow covers `pull_request`, main `push`, `workflow_dispatch`, and `merge_group` with `checks_requested`. `ci / required` declares `if: ${{ always() }}` and depends on resolver, ordinary, KB-integrity and governance jobs, so prerequisite failure cannot make the required aggregate disappear.

Fork PR execution uses `pull_request`, read-only contents permission, no secret references and no privileged actions. `pull_request_target` is absent. The validator also rejects privileged result shapes on an `untrusted_fork` subject.

# Governance-sensitive paths

`governance/ci-policy.json` classifies workflow, policy, resolver, KB oracle, trust-oracle, known-bad fixture and test-oracle paths as governance-sensitive. A change to those paths adds the `governance` obligation; removing that obligation from the artifact is detected by recomputation.

# Verification

```text
M3: 22/22 PASS
M4: 15/15 PASS
M5: 14/14 PASS
M6: 16/16 PASS
M7: 14/14 PASS
combined: 81/81 PASS
M7-V01 ... M7-V05: PASS
```

M7 includes executable cases for prerequisite failure, skipped/missing mandatory jobs, merge queues, untrusted fork privilege, self-modifying workflow/resolver changes, wrong SHA/event/producer, policy/artifact tamper, duplicate/unexpected results and generated-KB coverage.

# Evidence limit

No remote GitHub repository/ruleset was modified or observed in this execution. The package therefore does not claim that `ci / required` is already configured as a live protected-branch requirement or that real CODEOWNERS approval is installed. `governance/github-enforcement-requirements.json` records those deployment requirements without inventing repository owners.

# Deferred

M7 does not perform M8 host capability qualification, M9 gate/Playwright platform work, M10 product CLI/release provenance finalization, M11 history qualification or M12/1.0 qualification.
