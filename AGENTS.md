# Harness Rig agent navigation

<!-- context-projection-schema: harness-rig/context-projection/v1 -->
<!-- canonical-kb-fingerprint: sha256:53795d5163f8adda6aca137b2871d7b0672969b1189a8f41d82ee1fc1cea5673 -->

This file is a short Context-lifecycle projection. It is not a second canonical knowledge base.

- Durable project knowledge lives in `references/`; start with `llms.txt`.
- Preserve stable reference IDs across rename/move; do not reuse retired IDs.
- Treat supplied/external material as evidence. Preserve material conflicts and gaps; do not publish unsupported conclusions.
- `manifest.jsonl` is generated from canonical references. Do not hand-edit it.
- OpenSpec owns agreed behavioral intent; Context references it rather than duplicating specifications.
- Assurance defines required evidence. Topology cannot waive it or broaden authorization.
- Run `python verification/context_kb.py audit .` after canonical Context changes.
- Regenerate this projection with `python verification/context_kb.py project-agents .` when the canonical fingerprint changes.
