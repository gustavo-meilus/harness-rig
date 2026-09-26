## Context

See proposal.md for the M11 motivation and milestone scope. Existing M11 tooling covers bundle preflight, source-history rewrite, independent tree and topology verification, import-bundle generation, target-ref staging, and import-only checks. The checked-in preflight report points to absent /mnt/data bundles, while local source repositories have previously been found. Synthetic tooling results do not qualify real source histories.

The target repository contains a reconstructed Git timeline through M10. Source repositories must remain untouched. Imports, if qualified, go under the prefixes and tag namespaces in verification/m11-history-import-spec.json. Rewriting changes commit IDs, and current tooling does not preserve commit signatures or annotated-tag object identity.

## Goals / Non-Goals

**Goals:**
- Qualify actual source histories and preserve source refs, object integrity, and immutable input evidence before importing.
- Reuse the existing rewriter and independent verifier; stage imported refs without silently merging or changing active product files.
- Reconcile every M11 task and verification item with retained evidence or a precise BLOCKED disposition.

**Non-Goals:**
- Change Harness Rig product behavior or rewrite existing M0-M10 history.
- Treat synthetic evidence, a local clone's existence, or a passing verifier as proof of complete upstream ref coverage.
- Claim field-host qualification, pilot outcomes, signature fidelity, or legacy checks without evidence.

## Decisions

1. **Snapshot, then qualify.** Build source bundles from read-only local clones in an ignored temporary input directory. Record each clone's origin, HEAD, shallow status, refs, object-integrity result, bundle digest, and bundle verification. Compare the local ref inventory with authoritative upstream refs when accessible. If completeness cannot be established, stop that source's import and record BLOCKED.
   - Alternative: import directly from mutable working repositories. Rejected because runs would not be anchored to immutable inputs.

2. **Reuse prepared migration tooling.** Run the existing preflight, import orchestrator, independent rewrite and reproducibility verifiers, and target staging helper in isolated temporary locations. Preserve source-to-rewritten commit and tag maps and tree/topology reports.
   - Alternative: add a migration dependency or reimplement history rewriting. Rejected because existing tooling covers the flow and has synthetic evidence.

3. **Stage before merge.** Fetch verified bundles only into namespaced remote refs and tags. Review imported surfaces, legacy checks, import-only proof, licenses, hooks, installation surfaces, and changelog reconciliation before any merge. Keep merges limited to import-only content under approved legacy prefixes.
   - Alternative: let import automation merge. Rejected because that would obscure whether commits only import history.

4. **Treat fidelity and unavailable evidence as gates.** Inspect signed commits, signed or annotated tags, and release provenance before accepting rewritten identity changes. If required cryptographic fidelity cannot be preserved or independently proven, retain original bundles/maps and mark the affected criterion BLOCKED.
   - Alternative: assume signatures are irrelevant. Rejected because the proposal and import spec require an explicit fidelity disposition.

5. **No behavior delta spec.** Keep skip_specs true; M11 is evidence qualification and history migration only. Any discovered product behavior change requires a separate reviewed spec before implementation.

## Risks / Trade-offs

- [Local clones may omit upstream refs or objects] -> Compare against upstream ref inventory where accessible; otherwise scope evidence to captured refs and do not claim full-history qualification.
- [Rewriting changes commit IDs and drops signatures or annotated-tag object identity] -> Preserve original bundles and maps; block acceptance where required provenance cannot be reconstructed.
- [Legacy checks may need unavailable dependencies or host capabilities] -> Record the exact command, environment, and failure; do not convert unavailable checks to PASS.
- [An import may contain behavior or unrelated files] -> Verify filtered trees and import-only commits before merging; stop on unexpected paths or content.
- [Field pilots and native host evidence may need user-operated hosts] -> Record only evidence actually collected; keep required criteria BLOCKED when observations are unavailable.