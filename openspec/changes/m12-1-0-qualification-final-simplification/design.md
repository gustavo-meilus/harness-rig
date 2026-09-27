## Context

M11 is archived as complete at baseline
`bccbfcb7c4d03df843d7bc5a1a87a343d0b6c7d7`. M12 qualifies that final product
scope using the existing M3-M11 test modules, `scripts/check.py`, Context
audit, CI obligation workflow, host doctor, and release provenance CLI.

The current host evidence qualifies `local-subprocess` for a narrow set of
capabilities. It does not qualify the Codex adapter as Stable. Repository
governance also requires the accepted hosted `ci / required` verdict before a
release record can pass; local tests must not impersonate that verdict.

## Goals / Non-Goals

**Goals:**

- Revalidate the supported 1.0 claims against the final source revision.
- Retain deterministic results and exact revision binding for each gate.
- Make the final decision fail closed when hosted evidence or authorized
  independent review is unavailable.
- Retire unsupported or speculative scope without weakening trust guarantees.

**Non-Goals:**

- Change product behavior or introduce new dependencies or qualification
  infrastructure.
- Publish a release, push a branch, create tags, or claim external signing or
  attestation.
- Qualify Claude Code, Codex Desktop/CLI adapters, or unsupported isolation
  capabilities as Stable.

## Decisions

1. **Use existing checks.** Run the repository's canonical suite and the
   existing targeted suites for P0 trust, OpenSpec, repository enforcement,
   gates, migration, and release provenance. Add no second test runner.
2. **Bind evidence to the current commit.** Record the source SHA, exact
   commands, outcomes, and evidence paths. Regenerate Context outputs only
   after canonical references change, then run the canonical verifier last.
3. **Do not fabricate hosted acceptance.** Run local obligation and release
   checks, but mark hosted verdict dependent results blocked unless an accepted
   verdict exists for this exact source revision.
4. **Respect review boundaries.** M12-T10 requires a fresh independent
   architecture review. Do not send repository contents to a provider without
   explicit user authorization. Record the task as blocked if no authorized
   independent context is available.
5. **Keep current maturity claims narrow.** Re-run the local `doctor` path and
   retain only capabilities it observes. Do not transfer local-process
   evidence to Codex or another host adapter.
6. **Keep this change evidence-only.** If a product defect appears, stop and
   revise the proposal/design/tasks before making product changes.

## Risks / Trade-offs

- [No hosted verdict for the current commit] -> Local success is insufficient
  for release eligibility; retain the exact missing evidence and keep M12
  blocked.
- [Independent review payload is not authorized] -> Do not transmit repository
  content; leave M12-T10 blocked and request narrowly scoped authorization.
- [Native environment differs from prior qualification] -> Re-run doctor and
  record only current observed facts.
- [Evidence files drift from their source revision] -> Bind records to the
  exact SHA and re-run the canonical suite after evidence and Context updates.
