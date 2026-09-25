---
id: harness-rig-m7-trusted-repository-enforcement
title: M7 trusted repository enforcement
summary: Implemented r8.7 same-subject CI obligation resolution, strict required-verdict aggregation, merge-queue coverage, fork trust boundaries, and governance-sensitive path enforcement.
version: planning-baseline-2026-09-25-r8.7
updated: '2026-09-25'
provenance:
- Harness Rig M7 implementation and adversarial verification, 2026-09-25
- GitHub Actions workflow syntax documentation, rechecked 2026-09-25
- GitHub merge_group event documentation, rechecked 2026-09-25
- GitHub secure pull_request_target guidance, rechecked 2026-09-25
- GitHub required-status-check troubleshooting documentation, rechecked 2026-09-25
---
# Result

M7 completed with **PASS** at revision `r8.7` for the repository-local enforcement contract.

The milestone adds one deterministic obligation artifact and one final repository verdict. It does not add a general CI framework, remote attestation service, or second acceptance system.

```text
GitHub event subject + evaluated SHA + changed paths
    ↓
repository CI policy
    ↓
CI obligation artifact
    ↓
ordinary / KB-integrity / conditional governance results
    ↓
ci / required
```

A green `ci / required` means the validator observed exactly one acceptable result for every mandatory obligation in the artifact, and every result matched the same policy, event subject, evaluated SHA, expected producer and deterministic result identity.

# Obligation artifact

The application-level artifact schema is:

```text
harness-rig/ci-obligation-artifact/experimental-v1
```

It records only:

```text
policy identity + digest
evaluated SHA
event name + event subject
trust mode
changed paths
affected modules
mandatory obligation IDs
expected producer/result identities
```

This is CI/application evidence, not a Stable core contract. It has no provider-specific escape bag and no persistent service.

The r8.7 policy has three obligation classes:

- `ordinary` — always required; the canonical unittest suite;
- `kb-integrity` — always required; canonical KB/manifest/projection audit;
- `governance` — required when CI, policy, resolver, trust-oracle, fixture-source, or test-oracle paths change.

# Final required verdict

The final validator recomputes the mandatory obligation set from the checked policy and artifact changed paths. It rejects:

- malformed/tampered obligation artifacts;
- policy identity or digest mismatch;
- a mandatory obligation removed from the artifact;
- missing, duplicate, skipped, failed or blocked mandatory results;
- wrong evaluated SHA;
- wrong event or event subject;
- wrong producer;
- wrong deterministic result identity;
- unexpected results outside the mandatory set;
- privileged result shapes for untrusted-fork subjects.

The workflow job is named exactly `ci / required` and declares:

```yaml
needs: [resolve, ordinary, kb_integrity, governance]
if: ${{ always() }}
```

GitHub documents that jobs depending on a failed/skipped prerequisite are otherwise skipped unless a status-check condition such as `always()` is used. M7 therefore makes the final validator execute after prerequisite failure instead of silently converting failure into an absent aggregator.

# GitHub event subjects

The checked workflow covers:

- `pull_request`;
- `push` to `main`;
- `workflow_dispatch`;
- `merge_group` with `checks_requested` for `main`.

For `pull_request`, the evaluated revision is `github.sha`, so the obligation/result set applies to the merge revision actually exercised by the workflow. For merge queues, `github.sha` is the merge-group SHA and the event subject records the merge-group head reference.

GitHub currently documents `merge_group` as a separate required-check trigger. Repositories using a merge queue must include that event or the required status will not be produced for the merge group.

# Fork and privilege boundary

The M7 workflow uses `pull_request`, never `pull_request_target`, for untrusted PR code and declares only:

```yaml
permissions:
  contents: read
```

It does not reference repository secrets and does not contain privileged release/deploy actions.

The obligation artifact also records `untrusted_fork` versus `trusted`. The required validator rejects a privileged result for an untrusted-fork subject even if a policy were misconfigured to expect one.

GitHub's current documentation states that ordinary fork `pull_request` workflows normally receive a read-only `GITHUB_TOKEN` and no other secrets, while `pull_request_target` runs with elevated base-repository trust and becomes unsafe if it executes untrusted PR code. The Harness Rig workflow chooses the lower-trust path explicitly.

# Governance-sensitive surfaces

`governance/ci-policy.json` classifies the following classes as C3-sensitive for repository enforcement:

- `.github/workflows/`;
- repository CI policy and enforcement requirements;
- CI obligation resolver/validator;
- canonical KB integrity/audit oracle and known-bad fixture source;
- trust-decision and trust-identity modules;
- gate/OpenSpec/spec-engine security-sensitive adapter paths;
- the prototype test oracle.

Changing any classified path makes `governance` a mandatory result. This prevents the normal resolver from silently treating changes to its own enforcement machinery as ordinary application edits.

# Live repository protection boundary

The package cannot create or observe a remote branch protection/ruleset configuration by itself. The install-time requirements are retained in `governance/github-enforcement-requirements.json`:

- require `ci / required` for the protected branch/merge queue;
- bind the required status to the expected GitHub Actions source where repository/ruleset controls permit it;
- require code-owner or equivalent independent approval for governance-sensitive paths;
- do not enable secret/write-token exposure to untrusted fork workflows;
- enable the merge queue only with `merge_group` required-check coverage.

No CODEOWNERS identity is fabricated in r8.7 because the package does not know the destination repository's real owners. Therefore M7 claims executable repository-local enforcement semantics, not observed live GitHub ruleset qualification.

# Verification

M7 adversarial coverage includes:

```text
prerequisite FAIL -> ci / required still has an explicit blocking result path
mandatory SKIPPED -> BLOCKED
mandatory missing -> BLOCKED
merge_group same-subject PASS
untrusted fork + privileged result -> BLOCKED
resolver self-change -> governance mandatory
required-workflow self-change -> governance mandatory
wrong SHA -> BLOCKED
wrong producer -> BLOCKED
wrong event/subject -> BLOCKED
artifact/policy tamper -> BLOCKED
duplicate/unexpected result -> BLOCKED
canonical-source/generated-KB changes remain covered by KB integrity
```

The full r8.7 package suite and retained records are under `verification/m7-*`.

# Deliberate non-goals

M7 does not:

- configure a real remote GitHub ruleset or invent CODEOWNERS;
- qualify host capabilities (M8);
- implement the broader gate/Playwright provider platform (M9);
- finalize product CLI/release provenance (M10);
- perform M11 Git-history qualification;
- promote the CI obligation/result schemas into Stable core.
