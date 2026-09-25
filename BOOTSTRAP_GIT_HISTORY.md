# Git history bootstrap

This handoff ships verified Harness Rig milestone snapshots under `.bootstrap/` and a deterministic reconstruction helper at `tools/bootstrap_git_history.py`.

## What the history means

The generated commits are **synthetic reconstruction commits**. They preserve the sequence and file states represented by the retained verified milestone packages, but they are not the original development commits and must never be represented as such.

Available exact package snapshots begin at r8.3. There are no standalone r8.0/r8.1/r8.2 package snapshots in this handoff. Therefore:

1. commit 1 is the consolidated verified M0-M3 / r8.3 baseline;
2. commits 2-8 apply r8.4 through r8.10 sequentially;
3. commit 9 adds this Git/Codex/OpenSpec environment transformation without advancing M11.

Each reconstructed milestone commit also places that milestone's progressive remediation plan at root as `PROGRESSIVE_REMEDIATION_PLAN.md`.

## Run

From the extracted repository root, before any `.git` directory exists:

```bash
python tools/bootstrap_git_history.py
```

The helper:
- verifies every shipped package/plan SHA-256 before use;
- initializes `main` in an isolated temporary repository;
- reconstructs and commits each retained milestone snapshot in sequence;
- adds the post-r8.10 environment-transformation commit;
- checks that the final committed tree matches the extracted handoff tree, excluding ignored `.bootstrap/` payload;
- moves the reconstructed `.git` directory into the extracted repository only after validation passes.

The bootstrap commits use the explicit synthetic identity `Harness Rig Bootstrap <bootstrap@local.invalid>` so they cannot be mistaken for original human authorship. Future real commits should use the operator's normal Git identity.

After success:

```bash
git log --reverse --oneline --decorate
git status --short --ignored
python tools/run_all_tests.py
python verification/context_kb.py audit .
python verification/context_kb.py projection-status .
```

`.bootstrap/` is ignored. It may be retained for audit/reconstruction or deleted after Git history has been independently backed up.
