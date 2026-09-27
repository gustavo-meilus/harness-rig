## Why

M11 is the remaining qualification milestone before M12. The roadmap defers final disposition of RigYard proposals, Codex-first field evidence, and full source-history preservation for AIBoarding, TacticSwitch, and Skill Kit. M11 must close these gaps with retained evidence or record a precise BLOCKED result; synthetic migration-tooling evidence alone cannot qualify the real source histories.

## What Changes

- Record one evidence-backed Harness Rig disposition for each active RigYard proposal and explicit triggers for deferred work.
- Keep Codex Desktop/CLI as the primary operational target and retain its native field evidence.
- Treat Claude Code native qualification as out of scope for now; it is not an
  M11 acceptance gate.
- Run representative field pilots and simplify or remove mechanisms that show no distinct value.
- Preserve each source repository's original Git objects in a pinned submodule under its isolated legacy prefix; retain and verify the complete source-ref bundles.
- Reconcile the pinned source refs with CHANGELOG.md, licenses, state, hooks, installation surfaces, and original commit/tag signature evidence; prove the aggregate import commit changes only the three approved gitlinks and `.gitmodules` entries.
- Keep the TacticSwitch source snapshot unchanged; qualify a separately reviewed, one-file `MANIFEST.sha256` adapter on a disposable copy.
- If any required source history is unavailable or unverifiable, retain the evidence, mark M11 BLOCKED, and do not advance to M12.

## Capabilities

### New Capabilities

None. This milestone qualifies existing boundaries and records migration and field evidence; it does not authorize new product behavior.

### Modified Capabilities

None. No OpenSpec product capability specifications exist to modify, and the milestone contract changes no externally observable product requirement. The change opts out of delta specs with skip_specs: true; any behavior change discovered during M11 requires its own reviewed specification before implementation.

## Impact

Affected records include the root roadmap, progressive remediation plan,
CHANGELOG.md, canonical references, manifest and navigation projections, M11
verification evidence, and existing history preflight/import tooling. Inputs
are the complete AIBoarding, TacticSwitch, and Skill Kit bundles. Each complete
source repository is retained as a submodule under the approved legacy prefix;
no history rewrite or path filtering is used. Codex claims remain
evidence-gated; Claude native qualification is out of scope for now.
