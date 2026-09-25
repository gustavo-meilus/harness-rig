---
id: harness-rig-north-star-and-product-boundary
title: Harness Rig north star and product boundary
summary: The product thesis, defensible guarantee, merge decision, and boundaries that prevent Harness Rig from becoming an
  all-owning framework.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- Current project baseline and prior Harness Rig architecture analysis, 2026-09-21
- OpenAI Harness Engineering, 2026-02-11
- TacticSwitch governance and protocol sources, accessed 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied openspec_harness_engineering_analysis.md, research snapshot 2026-09-21
- Harness Rig expected-feature synthesis, refreshed 2026-09-21
- Skill Kit llm-knowledge-base-maintainer v1.1.0, SKILL.md and DEFAULT_LAYOUT.md, inspected 2026-09-24
- Harness Rig knowledge-base-first Context synthesis, refreshed 2026-09-24
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
---
# Product thesis

Harness Rig is the minimum-sufficient control plane that binds behavioral intent, authority, authorization, canonical project knowledge, assurance, execution topology, exact source state, executable/runtime evidence, and acceptance.

# Context thesis

The Context plane combines:

```text
AIBoarding lifecycle/freshness
+
Skill Kit LLM knowledge-base maintainer
```

Durable project knowledge uses canonical Markdown, stable IDs, provenance, `llms.txt`, `manifest.jsonl`, reconciliation, and deterministic integrity.

# Truth ownership

```text
OpenSpec
  agreed behavioral intent

Context knowledge base
  durable project/engineering knowledge

code + gates
  implementation evidence

runtime + telemetry
  operational reality
```

# Non-negotiable boundaries

- no hard external dependency;
- OpenSpec is default spec engine, not bundled;
- Skill Kit KB semantics are first-class Context behavior;
- no embedding/vector/RAG knowledge subsystem in the expected project;
- one source of truth per knowledge class;
- Assurance determines proof;
- Topology determines minimum formation;
- one agent is default;
- significant mechanisms need retirement criteria.

## Related

- [Skill Kit knowledge-base integration for the Harness Rig Context plane](skill-kit-knowledge-base-context.md)
- [Expected Harness Rig feature set and RigYard reconciliation contract](expected-harness-rig-feature-set.md)
