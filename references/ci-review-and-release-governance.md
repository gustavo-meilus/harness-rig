---
id: harness-rig-ci-review-and-release-governance
title: CI, review, versioning, and release governance
summary: Repository-wide CI aggregation, review roles, versioning, schema migrations, and provenance-aware release policy.
version: planning-baseline-2026-09-25-r8.7
updated: '2026-09-25'
provenance:
- GitHub Actions workflow syntax, accessed 2026-09-21
- GitHub rulesets documentation, accessed 2026-09-21
- GitHub CODEOWNERS documentation, accessed 2026-09-21
- Semantic Versioning 2.0.0, accessed 2026-09-21
- GitHub artifact attestations and immutable releases documentation, accessed 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- Harness Rig M7 repository enforcement implementation and verification, 2026-09-25
- GitHub Actions workflow/merge_group/security documentation rechecked 2026-09-25
---
# One canonical ordinary quality definition

Hosted CI should consume the same canonical ordinary quality command used locally.

Do not duplicate the ordinary correctness command list in workflow YAML.

# One required repository verdict

```text
changed files
    ↓
affected-module resolver
    ↓
relevant workflows/gates
    ↓
governance check
    ↓
ci / required
```

Only the final aggregate needs universal branch/ruleset enforcement after unified Harness Rig CI exists.


# M7 implemented repository verdict

M7/r8.7 implements the repository-local form of this design. `governance/ci-policy.json` emits a same-subject obligation set, each job emits an obligation result, and `ci / required` recomputes/validates the complete set. The aggregate rejects missing/skipped/failed jobs and mismatched SHA, event subject, producer, result identity, or policy.

The workflow includes `merge_group` and uses `if: ${{ always() }}` on the final job so failed prerequisites do not skip the repository verdict. Fork PR execution remains unprivileged (`pull_request`, `contents: read`, no secret references). See [M7 trusted repository enforcement](m7-trusted-repository-enforcement.md).

Live branch/ruleset and real CODEOWNERS installation remain repository-configuration responsibilities; r8.7 does not claim they were remotely configured or observed.

# OpenSpec CI posture

When OpenSpec is active/relevant:

```text
1. verify OpenSpec adapter/config health
2. run strict OpenSpec validation for affected authority
3. run normal project build/static/tests
4. run risk-specific integration/security/migration/etc.
5. optional OpenSpec semantic conformance review
6. permit archive only after required evidence
```

OpenSpec validation is one CI input, not CI itself.

Because the supplied analysis records current issue evidence where malformed config/rules can be ignored while validation exits successfully, independently verify expected effective rules/instructions until upstream behavior is sufficient.

# Archive control

Treat archive as a guarded state transition.

CI/release tooling may require:

```text
pre-archive authority fingerprint
change validation
required implementation evidence
archive operation
post-archive durable-spec fingerprint
postcondition check
```

Record results using ordinary Harness Rig evidence.

# Hosted triggers

Ordinary quality coverage should support appropriate:

```text
pull_request
push main
manual dispatch
```

Observe real emitted check identities before configuring required-check protection.

# Slow assurance

Use one proportional slow/manual entry point.

Run deterministic prerequisites first.

Run native/adversarial/semantic work only when it answers a current evidence question.

# Native smokes

Run native host smokes for adapter changes, release qualification, support promotion, stale evidence, or explicit requests.

Do not schedule every host by default.

# Review layers

Keep separate:

- Harness executable verification;
- spec-engine semantic conformance;
- repository governance review;
- human authorization for consequential actions.

# Versioning

Use one Harness Rig product version initially.

External engine compatibility is a tested capability profile, not a hard package dependency.

For OpenSpec, record tested versions/capabilities in Harness Rig compatibility data and detect installed version at runtime.

# Release provenance

Long-term flow:

```text
commit
  ↓
ci / required
  ↓
build distributions
  ↓
checksums
  ↓
artifact attestations
  ↓
immutable release
```

## Related

- [OpenSpec spec engine, authority, and brainstorming integration](openspec-spec-engine-and-authority.md)
- [Repository governance and change model](repository-governance-and-change-model.md)
- [Host adapters and capability negotiation](host-adapters-and-capabilities.md)
- [Acceptance evaluations and metrics](acceptance-evals-and-metrics.md)
