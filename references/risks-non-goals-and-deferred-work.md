---
id: harness-rig-risks-non-goals-and-deferred-work
title: Risks, non-goals, and deferred work
summary: Failure modes to actively avoid and features that should wait until the core control system is proven.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- Harness Rig architecture and governance analysis, 2026-09-21
- OpenAI Harness Engineering context-management findings, 2026-02-11
- TacticSwitch minimum-topology governance, accessed 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Skill Kit llm-knowledge-base-maintainer v1.1.0, SKILL.md and DEFAULT_LAYOUT.md, inspected 2026-09-24
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
---
# Primary risks

## Knowledge duplication

One owner per class:

```text
OpenSpec -> behavioral intent
Context KB -> durable project/engineering knowledge
code/generated artifacts -> implementation/interface facts
tests/gates -> executable evidence
telemetry -> operational observations
```

## Knowledge dumping

Keep `llms.txt` curated and canonical topics focused.

## Structurally valid but stale knowledge

Use provenance, targeted freshness, reconciliation, and audit.

## Unsupported claims become canonical

Preserve conflicts and evidence gaps.

## Context explosion

Use progressive disclosure.

## Hidden retrieval infrastructure returns

The expected project has no embedding/vector/RAG or semantic-index subsystem.

First improve canonical pages, IDs, links, indexes, and reconciliation.

## Orchestration complexity

One agent by default; bounded optional recurrence only if earned.

# Non-goals

Harness Rig should not:

- vendor OpenSpec;
- create a replacement spec system;
- create a test framework;
- add an embedding/vector/RAG knowledge subsystem;
- force multi-agent execution;
- build scheduler/queue/daemon infrastructure;
- build general telemetry/model-pricing platforms;
- build a plugin marketplace without demand.

# Decision test for new knowledge machinery

> Which repeated failure cannot be handled with canonical Markdown, stable IDs, provenance, `llms.txt`, `manifest.jsonl`, explicit links, repository/text search, and disciplined reconciliation?

Without a concrete answer, do not add another layer.

## Related

- [Skill Kit knowledge-base integration for the Harness Rig Context plane](skill-kit-knowledge-base-context.md)
