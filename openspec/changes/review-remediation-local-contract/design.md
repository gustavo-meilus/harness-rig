# Design: local 1.0 review remediation

## Context

See proposal.md. The reviewed checkout has an untracked review packet, three
tracked and preflighted M11 source bundles, and a passing 151-test baseline.
Current release records use v2; no 1.0 release has been instantiated.

## Goals / Non-Goals

**Goals:**

- Remove authorization-shaped results from the product's local commands.
- Make CI report only work GitHub actually ran on the evaluated revision.
- Qualify one exact clean source candidate and artifact under a revised scope.

**Non-Goals:**

- Add an identity provider, independent reviewer, GitHub App, or organization.
- Claim that the solo-owned GitHub workflow is an independent acceptance oracle.
- Reconstruct source histories already present in tracked M11 bundles.

## Decisions

1. The CLI will invoke the existing command gate for `verify` and `direct`
   without issuing a grant or evaluating an authorized lifecycle verdict.
   Existing receipt data remains the local result. The raw compatibility
   command remains available but its former verdict shape is retired.
2. Guarded archive retains readiness, exact-state, mutation, transition, and
   postcondition checks. It uses an evidence-only requirement with no grant,
   and the CLI requires `--confirm-local-archive` before calling it. CLI output
   reports the local outcome and evidence, without exposing an authenticated
   acceptance verdict.
3. The Stable grant schema and loader remain for serialized compatibility.
   Documentation distinguishes grant integrity and field matching from issuer
   authentication. The local CLI does not consume grants.
4. CI always runs ordinary tests and Context audit. The final job uses
   `needs` results and `always()` to fail on failure, skip, or cancellation.
   Retire the experimental obligation resolver, policy, and conditional
   governance job. Keep `pull_request`, `push`, `workflow_dispatch`, and
   `merge_group` triggers with read-only permissions.
5. Release records advance to v3 with `source_revision` in place of
   `accepted_source_revision`. V1/v2 remain historical and ineligible.
   Verification still requires exact artifact hashes, current hosted-run
   facts, and exact-byte attestation. A Git bundle from the final tag supplies
   the source artifact, checked independently with native Git.
6. `PRODUCT_REVISION` remains the single product revision value and becomes
   `r8.12`; `status` reads it rather than repeating a literal. Migration to
   r8.10 remains historical. The final release is the exact-SHA `v1.0.0` tag.

## Risks / Trade-offs

- Candidate workflow changes can yield a misleading green check. The revised
  scope states this plainly; release provenance treats the run as observation.
- A local operator can archive without provider authorization. The command
  requires explicit confirmation and retains all readiness/state checks.
- Native Git bundle and hosted release evidence are unavailable until a clean
  final commit is pushed. Keep qualification BLOCKED until each is verified.

## Migration Plan

1. Land the revised behavior and docs with M12 marked REWORK.
2. Run local and native checks, then review one clean candidate commit.
3. Push that candidate, obtain its hosted run and live ruleset observation.
4. Tag the accepted commit, build and verify the Git bundle, attest the v3
   release record, and publish only after exact-SHA independent verification.
5. If any check fails, leave the release unpublished and M12 blocked; no
   rollback of historical v2 records is needed.
