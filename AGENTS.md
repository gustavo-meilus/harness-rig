# Harness Rig agent navigation

<!-- context-projection-schema: harness-rig/context-projection/v1 -->
<!-- canonical-kb-fingerprint: sha256:a4391a46f5051d2e181ad1a99e2222183c00e4b03a729593cb05adf508031a53 -->

This file is a short Context-lifecycle projection. It is not a second canonical knowledge base.

- Durable project knowledge lives in `references/`; start with `llms.txt`. Root `ROADMAP.md` is the Git/Codex execution projection.
- Operational host priority is Codex Desktop/CLI first, Claude Code second; capability claims still require native evidence.
- Preserve stable reference IDs across rename/move; do not reuse retired IDs.
- Treat supplied/external material as evidence. Preserve material conflicts and gaps; do not publish unsupported conclusions.
- `manifest.jsonl` is generated from canonical references. Do not hand-edit it.
- OpenSpec owns agreed behavioral intent; Context references it rather than duplicating specifications.
- Assurance defines required evidence. Topology cannot waive it or broaden authorization.
- Run `python verification/context_kb.py audit .` after canonical Context changes.
- Regenerate this projection with `python verification/context_kb.py project-agents .` when the canonical fingerprint changes.
