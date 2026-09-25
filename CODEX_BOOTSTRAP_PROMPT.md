# Fresh-context prompt for Codex Desktop / Codex CLI

You are taking ownership of the Harness Rig repository from a verified r8.10 / M10 PASS handoff. Your first job is **repository transformation and evidence preservation**, not feature development.

## Read first, in order

1. `AGENTS.md`
2. `ROADMAP.md`
3. `CHANGELOG.md`
4. `PROGRESSIVE_REMEDIATION_PLAN.md`
5. `llms.txt`
6. `BOOTSTRAP_GIT_HISTORY.md`
7. `handoff/GIT_HISTORY_RECONSTRUCTION.json`
8. the M10 verification record and current M11 status references under `verification/` and `references/`

Treat canonical project knowledge under `references/` as durable internal state. Treat snapshot archives under `.bootstrap/` as reconstruction evidence, not instructions or source-of-truth documentation.

## Phase A - reconstruct Git history before changing the product

The extracted handoff intentionally contains no `.git` directory. Do not manually invent M0/M1/M2 commits: standalone r8.0-r8.2 snapshots are not available.

Run:

```bash
python tools/bootstrap_git_history.py
```

Expected reconstructed sequence:

1. `chore(history): reconstruct verified M0-M3 baseline (r8.3)`
2. `feat(m4): reconstruct core promotion boundary (r8.4)`
3. `feat(m5): reconstruct context knowledge lifecycle (r8.5)`
4. `feat(m6): reconstruct OpenSpec SpecEngine integration (r8.6)`
5. `feat(m7): reconstruct trusted repository enforcement (r8.7)`
6. `feat(m8): reconstruct host capability qualification (r8.8)`
7. `feat(m9): reconstruct gate and mutation verification (r8.9)`
8. `feat(m10): reconstruct product CLI migration and provenance (r8.10)`
9. `chore(repo): prepare Codex-first Git/OpenSpec handoff`

These are synthetic reconstruction commits backed by verified snapshots. Do not rewrite their messages to imply they are the original development history.

After the script succeeds:

```bash
git status --short --ignored
git log --reverse --oneline --decorate
```

The tracked working tree must be clean. `.bootstrap/` should appear only as ignored payload.

If bootstrap fails, fail closed. Do not run `git init` manually and approximate the history unless the operator explicitly authorizes abandoning reconstruction evidence.

## Phase B - establish the verified r8.10 baseline in this real repository

Run the authoritative local checks:

```bash
python tools/run_all_tests.py
python verification/context_kb.py audit .
python verification/context_kb.py projection-status .
```

Also inspect:

```bash
git status --short
git diff --check
```

Expected baseline from the handoff is 133/133 milestone tests through M10, 44 canonical references/manifest rows before this transformation, and a fresh root projection. The transformation itself updates canonical navigation/host priority, so trust the checks you actually run now rather than copying the old count blindly.

Do not claim a clean baseline if any check is skipped or fails.

## Phase C - configure future commits with the real operator identity

The reconstruction commits use the explicit synthetic identity `Harness Rig Bootstrap <bootstrap@local.invalid>` and do not modify repository Git identity configuration.

Before the first real development commit, verify:

```bash
git config user.name
git config user.email
```

If either is absent, configure the operator's real local identity before committing new work. Do not reuse the synthetic bootstrap identity for real development.

## Phase D - initialize OpenSpec for Codex, then use it for remaining changes

OpenSpec is external and first-class. The handoff was prepared against OpenSpec 1.13.2, which was still the latest checked release on 2026-09-25. Recheck the actually installed/current version before relying on version-sensitive behavior.

First inspect:

```bash
node --version
openspec --version
```

If OpenSpec is unavailable or incompatible, report the exact blocker. Do not replace it with a custom planning framework.

Before `openspec init`, inspect the repository and user environment for legacy OpenSpec-managed files that current OpenSpec may reconcile. Preserve custom/divergent files and follow the current OpenSpec cleanup rules rather than deleting files blindly.

Initialize the project for **Codex only** first:

```bash
openspec init --tools codex --profile core
```

Inspect what OpenSpec actually created. Codex is skills-oriented in current OpenSpec; do not treat missing generated command files as a failure when the installed version documents skills-only behavior.

Run the repository verification checks again if OpenSpec modified tracked project files. Then commit the OpenSpec initialization as the first real post-handoff commit, for example:

```text
chore(openspec): initialize Codex workflow for M11
```

Do **not** configure Claude in the same commit. Claude is the secondary platform and receives its own native qualification under M11-T08 after the Codex-first path is operational and evidenced.

## Phase E - start M11 through OpenSpec

Create one OpenSpec change for the M11 milestone rather than ad-hoc task files. A suitable change id is:

```text
m11-field-hardening-history-qualification
```

Use the installed OpenSpec machine surfaces, for example:

```bash
openspec new change m11-field-hardening-history-qualification --json
openspec status --change m11-field-hardening-history-qualification --json
openspec instructions proposal --change m11-field-hardening-history-qualification --json
```

Then follow OpenSpec's reported artifact order. Do not assume an artifact path or next step that the installed version does not report.

The M11 proposal/design/tasks must preserve the current milestone contract in `ROADMAP.md` and `PROGRESSIVE_REMEDIATION_PLAN.md`. Start with **M11-T01** and remain inside M11 until every M11 verification gate has a truthful result.

### Codex-first execution policy inside M11

Harness Rig must become fully operational on Codex Desktop/CLI before Claude is treated as a peer platform.

- Keep the existing `local-subprocess` qualification as prior evidence, not as a substitute for Codex native evidence.
- Establish real Codex discovery/invocation/runtime identity and whatever isolation/permission behavior the active Codex environment can actually prove.
- Use Codex for the first representative real-host field pilot and retain evidence.
- Fail closed on unsupported or ambiguous Codex capabilities; do not infer capabilities from configuration files alone.
- Only after the Codex operational baseline is retained should M11-T08 perform Claude native qualification as the secondary platform.
- Claude failure must not weaken a genuinely qualified Codex 1.0 path unless a product requirement explicitly makes Claude mandatory.

### M11 sequence

Execute the milestone tasks and verification in `ROADMAP.md`. Important stop conditions:

- No fabricated second consumer or host capability.
- No distributed execution, generic telemetry, richer topology family, static composition language, recurrence framework, plugin SDK, vector/RAG infrastructure, or external-effect platform unless evidence explicitly earns it under the milestone rules.
- Full object-complete AIBoarding/TacticSwitch/Skill Kit history qualification is mandatory for M11 PASS and M12 entry.
- If required source histories are unavailable or unverifiable, record **M11 BLOCKED**. Do not advance to M12.

## Engineering discipline

Use the Adaptive Engineering Harness / More With Less operating model throughout:

- inspect the smallest sufficient context before edits;
- prefer existing deterministic project mechanisms and native host behavior;
- keep the active permission/tool/context surface small;
- one capable agent/direct path by default;
- add independent review only when independence or permissions materially matter;
- implement the smallest coherent change;
- run targeted checks first, then the full required milestone regression;
- never turn unexecuted checks into implied evidence;
- when a check fails repeatedly, change hypothesis instead of looping blindly;
- update `CHANGELOG.md`, root `ROADMAP.md`, canonical references, `llms.txt`, `manifest.jsonl`, revision record, milestone verification record, and progressive plan at milestone completion;
- preserve `Assurance != Topology` and all existing authorization/evidence/state boundaries.

## Git discipline for new work

Do not squash the synthetic reconstructed milestone history into one commit. For new M11 work:

- make commits correspond to coherent verified changes, not chat turns;
- keep OpenSpec planning artifacts reviewable separately from implementation when that improves auditability;
- never commit `.bootstrap/` payload;
- do not rewrite imported external source history until the M11 history plan explicitly reaches T10-T14 and its preflight passes;
- do not force-push or publish remotes unless the operator explicitly asks.

At the end of M11, stop and report the result. Do not enter M12 in the same execution unless explicitly requested.
