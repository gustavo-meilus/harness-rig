## Context

See proposal.md for M11 scope. Existing M11 reports describe a history-rewrite experiment; retain them as historical evidence, not as the accepted import. Rewriting changed commit IDs, did not carry commit signatures, and changed annotated-tag object identity. Complete source bundles already exist and passed preflight. Source repositories must remain untouched.

## Goals / Non-Goals

**Goals:**
- Preserve exact source commits and tags in full source submodules pinned under `legacy/aiboarding`, `legacy/tacticswitch`, and `legacy/skill-kit`.
- Track the complete source bundles as verification evidence so all advertised refs and objects remain available beyond the single gitlink pin.
- Prove source pins, bundle integrity, signature evidence, import-only superproject commits, legacy checks, and surfaced operational content.
- Keep the TacticSwitch checksum repair isolated in a separately reviewed adapter applied only to a disposable worktree.

**Non-Goals:**
- Change Harness Rig product behavior, rewrite source history, or amend source commits/tags.
- Treat submodule pins as proof of complete ref coverage without bundle/ref verification.
- Claim field-host qualification or signature validity without retained evidence.

## Decisions

1. **Use native source history.** Add one complete source repository per approved legacy prefix, each pinned to the audited `refs/heads/main` commit. Keep complete source bundles in `verification/m11-source-bundles/`; verify bundle object integrity and retain the complete advertised ref inventory. The Skill Kit submodule contains the full repository because path filtering would require rewriting its history.
2. **Use one aggregate one-parent import commit.** Add the three gitlinks and `.gitmodules` entries together in one reviewable commit. The verifier confirms the changed paths are exactly `.gitmodules` and the three approved gitlink paths, every gitlink mode is `160000`, each object ID equals the audited source main, and no other path changes. No synthetic imported-history parent or old-to-new commit map is required.
3. **Verify original objects.** Require the retained upstream GitHub signature report to show `verified: true` and `reason: valid` for every signed commit, and confirm each exact commit object and signature header exists in its tracked source bundle. Verify every tag ref resolves to the exact bundle object; no signed tag objects were found. Local `git verify-commit` is supplementary and may remain blocked by missing local keys; never change global signing configuration. Block if upstream verification is absent, invalid, or does not match the bundled object IDs.
4. **Keep verification adaptations separate from source history.** Preserve
   every source gitlink at its audited upstream commit. Store the TacticSwitch
   one-file `MANIFEST.sha256` regeneration and AIBoarding's root-held Windows adapter (five test-portability paths, the
   lifecycle cwd parser, and its regression test) under `verification/m11-adaptations/`. Apply each only
   to a disposable copy, verify its changed-path set, and report raw and
   adapted outcomes separately. The AIBoarding adapter is applied only to disposable verification copies; the lifecycle fix restores intended Windows cwd handling and adds no Harness Rig product code or upstream history.
5. **Retain field gates.** Use `codex doctor` and endpoint-specific network
   diagnostics before retrying the Codex CLI pilot. Do not bypass network
   policy. Complete the required Codex pilot and V04 review. Claude native
   qualification is out of scope for now and is not a blocker.
6. **No behavior delta spec.** Keep `skip_specs: true`; this is repository history and qualification evidence, not a product behavior change.

## Risks / Trade-offs

- [Submodules are not populated by ordinary clone] -> Document `git clone --recurse-submodules` or `git submodule update --init`; bundles remain available for offline object/ref verification.
- [A gitlink pins only one commit] -> Retain and verify the full source bundle and complete advertised refs separately.
- [Local signer trust may not be available] -> Use per-run trust files only; block if exact original signatures cannot be independently verified.
- [The TacticSwitch source check remains red] -> Report raw-source failure and adapter result separately; do not mutate the pinned source.
- [Field pilots may require network/native hosts] -> Record only observed results and leave M11 blocked until required pilots complete.
