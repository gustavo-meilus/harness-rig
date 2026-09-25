# Harness Rig

Harness Rig is an evidence-producing control plane for AI-assisted software engineering. The current verified revision is **r8.10 / M10 PASS**. The remaining planned milestones are **M11** (RigYard disposition, full source-history qualification, field hardening) and **M12** (1.0 qualification and final simplification).

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

Then continue at **M11-T01** only.

## Host priority

Operational priority is:

1. **Codex Desktop/CLI first**: make Harness Rig genuinely operable and natively qualified on Codex before expanding host-specific machinery.
2. **Claude Code second**: qualify Claude as a secondary platform under M11-T08 without weakening or bypassing Codex-first guarantees.

Priority is not maturity. Host claims remain evidence-gated and fail closed when native behavior has not been observed.

## OpenSpec

OpenSpec remains external and first-class. The current checked baseline in this handoff is **OpenSpec 1.13.2**. After Git reconstruction, use OpenSpec to drive the remaining M11/M12 development work rather than creating a second planning framework. Recheck the installed/current OpenSpec version before relying on version-sensitive behavior.
