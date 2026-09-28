# Harness Rig

Harness Rig is an evidence-producing control plane for AI-assisted software engineering. The product revision is **r8.12**. M11 source-history qualification passed with recorded limits. M12 and the 1.0 release are **REWORK** while the local-contract remediation in `openspec/changes/review-remediation-local-contract/` is applied and verified.

## Fresh repository start

For a new Codex Desktop/CLI context, read in this order:

1. `CODEX_BOOTSTRAP_PROMPT.md`
2. `AGENTS.md`
3. `ROADMAP.md`
4. `CHANGELOG.md`
5. `PROGRESSIVE_REMEDIATION_PLAN.md`
6. `llms.txt`

The handoff archive contains ignored snapshot payload under `.bootstrap/`. Run:

```bash
python tools/bootstrap_git_history.py
```

This reconstructs an evidence-backed Git history from the retained verified package snapshots. The history is explicitly **synthetic reconstruction history**, not a claim that these commits are the original development commits.

After reconstruction, verify the baseline:

```bash
python tools/run_all_tests.py
python verification/context_kb.py audit .
python verification/context_kb.py projection-status .
```

For current work, follow `ROADMAP.md` and the active OpenSpec change.

## Host priority

Operational priority is:

1. **Codex Desktop/CLI first**: make Harness Rig genuinely operable and natively qualified on Codex before expanding host-specific machinery.
2. **Claude Code second**: native qualification is deferred under the current scope.

Priority is not maturity. Host claims remain evidence-gated and fail closed when native behavior has not been observed.

## OpenSpec

OpenSpec remains external and first-class. The product adapter targets its checked 1.13.2 contract. The planning CLI version may differ; recheck version-sensitive behavior before relying on it.
