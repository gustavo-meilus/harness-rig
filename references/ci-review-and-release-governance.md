---
id: harness-rig-ci-review-and-release-governance
title: CI, review, versioning, and release governance
summary: Repository-wide CI aggregation, review roles, versioning, schema migrations, and provenance-aware release policy.
version: review-remediation-2026-09-28-r8.12
updated: '2026-09-28'
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
- Harness Rig M10 release-record/checksum implementation and verification, 2026-09-25
- Harness Rig M12 live hosted-CI release-provenance correction, 2026-09-27
- GitHub Actions workflow/merge_group/security documentation rechecked 2026-09-25
- Harness Rig final review and local-contract OpenSpec remediation, 2026-09-28
---
# One canonical ordinary quality definition

Hosted CI runs the ordinary Python test suite and Context audit. The workflow
lists those two commands directly.

# One required repository verdict

```text
ordinary tests + Context audit
    ↓
ci / required
```

The final job fails if either prerequisite fails, skips, or is cancelled.
It runs for pull requests, main pushes, manual dispatches, and merge groups.
The candidate can edit the workflow, so this is project CI evidence, not an
independent acceptance oracle. Live ruleset source binding is observed
separately.


# M7 implemented repository verdict

M7/r8.7 originally implemented a repository-local obligation resolver. The
r8.12 review found it candidate-controlled and unable to establish an
independent verdict. It was removed in the local-contract remediation.

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


# M10 release-record implementation

M10 introduced `harness-rig/release-record/v1`; v2 was the earlier hosted-run
correction. New records use `harness-rig/release-record/v3` in
`verification/release_provenance.py`. V3 binds the explicit GitHub repository,
API-returned repository ID, factual `source_revision`, Actions run ID and
attempt, required job ID, artifact size/SHA-256,
and creation time. Eligible records remain unsigned CANDIDATEs. Creation and
verification use authenticated read-only `gh api` lookups. The accepted run must be a
completed successful `push` on `main` for the exact source SHA from
`.github/workflows/ci-required.yml`, with one successful `ci / required` job
in the recorded attempt. A rerun, unavailable API, or mismatch blocks.

`verification/release_provenance.py attest` submits the exact candidate JSON to
the protected manual attestation workflow. Verification reports artifact
integrity, hosted CI, and attestation separately; all three must pass. The
signing workflow validates the candidate and CI run, then requires approval
through the `release-provenance-attestation` environment before attesting the
exact manifest bytes. This binds the approved artifact hashes but does not
prove the signing workflow built the artifacts. Local mocked tests do not
establish a hosted run, environment protection, or repository ruleset. The
checkout's repository identity must be supplied explicitly; live ruleset and
required-check source observation remains a separate M12 gate. V1 and v2
records are ineligible for the new release. Provenance PASS does not establish
independent source acceptance or separation of duties.
