## Context

The initial M12 review found that the verifier could accept a BLOCKED or unvalidated record. A subsequent correction bound a local M7 JSON proof, but that proof is locally constructible and cannot demonstrate that hosted GitHub Actions accepted the source revision. No Git remote is configured in this checkout, so callers must supply the GitHub repository identity explicitly.

## Goals

- Bind v2 records to release source, artifact hashes, GitHub repository ID, run ID, run attempt, and the `ci / required` job ID.
- Fetch workflow-run and attempt-specific job data through authenticated, read-only `gh api` calls at creation and verification.
- Report artifact integrity separately from hosted eligibility and pass only when both pass.
- Keep repository ruleset and required-check source observation separate; a passing run cannot prove enforcement configuration.

## Non-goals

- No Git remote inference, push, workflow trigger during implementation, release publication, or upstream legacy-history edit.
- No local JSON artifact is accepted as hosted-run proof.

## Decisions

1. Record creation and verification require explicit `OWNER/REPO`. API-returned `repository.full_name` and numeric ID must agree with that input and the record.
2. Accepted evidence is one completed, successful `push` run on `main`, at the exact source SHA, from `.github/workflows/ci-required.yml`, plus exactly one completed successful `ci / required` job in the recorded attempt. The job's run ID and SHA must match. Verification requires the run's current attempt to remain the recorded attempt; reruns invalidate the old record.
3. Use `gh api` without shell evaluation. API errors, authentication failures, malformed/truncated responses, unavailable runs, or any mismatch produce BLOCKED. A missing run can still be recorded as an immutable BLOCKED candidate.
4. V2 holds only references/identities and artifact metadata, not M7 obligation or result payloads. Its digest detects edits only when the editor does not recompute it; GitHub's signed attestation over the exact record bytes is the trusted anchor.
5. Record creation emits an eligible `CANDIDATE`, never overall PASS. `attest` dispatches the exact candidate JSON to the manual `main` workflow with a 60,000-byte serialized-input ceiling. The workflow validates the candidate and live hosted CI, summarizes its artifact hashes, then uses the required-reviewer `release-provenance-attestation` environment before attesting the exact bytes.
6. Verification returns `artifact_integrity`, `hosted_ci`, and `attestation` separately. Overall PASS requires all three PASS. Invalid signatures and tampered records return FAIL; unavailable hosted checks or attestation verification return BLOCKED.
7. V1, BLOCKED, and unsigned candidates cannot pass. Ruleset and required-check source observation remain separate M12 gates.
8. Validate artifact metadata at record parsing/building boundaries, then render the environment approval summary through one tested encoder that treats every record-derived value as literal Markdown text.

## Risks and limits

- Verification requires network access and authenticated GitHub CLI access.
- Attestation detects edits after signing. It does not prove the listed artifacts were built by the hosted workflow; the environment approver authorizes the candidate's artifact hashes.
- The protected GitHub Environment must have at least one required reviewer configured. Referencing the environment in workflow YAML alone does not establish that setting.
- Artifact attestations require a GitHub plan/repository visibility combination that supports them.
- GitHub API availability, permissions, pagination limits, and actual repository enforcement remain external evidence requirements.
