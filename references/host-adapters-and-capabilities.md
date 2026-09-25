---
id: harness-rig-host-adapters-and-capabilities
title: Host adapters and capability negotiation
summary: Capability-based integration model for Claude Code, Codex, Copilot, and future hosts without pretending their enforcement
  surfaces are identical.
version: planning-baseline-2026-09-25-r8.3
updated: '2026-09-25'
provenance:
- TacticSwitch protocol, governance, and adapter evidence policy, accessed 2026-09-21
- Skill Kit HOSTS.md conclusions referenced in prior project analysis, 2026-09-21
- User-supplied tacticswitch-openspec-proposals-v3.zip, supplied 2026-09-21
- User-supplied tacticswitch-openspec-loop-proposals.zip, supplied 2026-09-21
- Skill Kit more-with-less v1.0.2, plugins/more-with-less/skills/more-with-less/SKILL.md, inspected 2026-09-24
- OpenSpec v1.13.2 release baseline rechecked 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- Harness Rig progressive remediation M1 trust-protocol review, 2026-09-24
- User-supplied Harness Rig adversarial architecture review, 2026-09-24
- RigYard acceptance evidence, durable worker evidence, result acceptance, attempt capability, workspace baseline source/tests
  inspected 2026-09-24
- Skill Kit more-with-less v1.0.2 canonical skill and playbook inspected 2026-09-24
- Git official status/diff/submodule documentation rechecked 2026-09-24
- Node.js official child_process documentation rechecked 2026-09-24
---
# Principle

"Seamless" should mean one coherent abstraction over heterogeneous hosts, not pretending those hosts provide identical guarantees.

# Capability model

A host adapter should expose evidence-backed capabilities such as:

```text
native_skill_discovery
lifecycle_hooks
pre_tool_gate
post_edit_hook
stop_gate
isolated_worker
read_only_worker
worktree_worker
browser_control
permission_enforcement
worker_model_override
worker_effort_override
runtime_identity_observation
```

The Topology module consumes `CapabilitySet`.

If assurance requires a capability that the current host cannot provide, return `BLOCKED` unless the assurance requirement explicitly permits a weaker safe mode.

# Requested, resolved, and observed

Host integration must distinguish:

```text
requested
  portable intent

resolved
  adapter-selected/configured runtime

observed
  facts actually provable from the host/runtime
```

A configured worker-specific model or effort value must not be reported as observed if the host may silently inherit or fall back.

Unknown or ambiguous results remain `UNVERIFIED`.

Useful provisional resolution states include:

```text
PINNED
INHERITED
FALLBACK
UNSUPPORTED
UNVERIFIED
```

Final enum design requires cross-host evidence.

# Proportional execution constraints

Portable execution preferences may be:

```text
required
preferred
advisory
```

Missing required execution capability fails closed.

Missing preferred/advisory settings may use a safe native/default substitute when the actual resolution and reason are reported.

High change risk does not automatically create a required stronger-model or higher-effort constraint.

# Harness Doctor

Provide:

```text
harness-rig doctor
```

It should perform fresh-process conformance checks, not only inspect installed files.

Example:

```text
Host                     Claude Code
Context loading          VERIFIED
Lifecycle hooks          VERIFIED
Stop gate                VERIFIED
Fresh worker             VERIFIED
Read-only worker         VERIFIED
Worktree isolation       VERIFIED
Evidence receipt         VERIFIED
Fail-closed routing      VERIFIED
Worker model override    UNVERIFIED
Worker effort override   UNSUPPORTED

Capability level         DEGRADED/FULL as policy defines
```

Doctor should be able to show requested/resolved/observed facts where a native smoke is explicitly testing runtime execution resolution.

# Compatibility evidence

Promoting a host adapter should require evidence such as:

- host version/runtime identity;
- clean installation;
- discovery;
- invocation;
- generic-worker creation;
- isolation behavior;
- permission behavior;
- fail-closed behavior;
- concrete runtime-resolution evidence where claimed;
- interactive versus headless/ephemeral mode where separately claimed;
- uninstall or rollback where relevant.

Static parsing of package files is not enough to promote an adapter.

One successful mode does not prove an untested mode.

One smoke does not automatically promote support maturity.

# Native conformance smokes

Native smokes belong in the `0.6` host-platform milestone because Harness Rig cannot credibly claim a runtime capability without evidence from that runtime.

Default cadence:

```text
manual
release qualification
adapter change
support-promotion decision
stale-evidence revalidation
```

Do not schedule every adapter by default.

A recurring smoke requires:

- stable credentials/environment;
- explicit freshness need;
- repeated reliable runs;
- acceptable quota/cost;
- distinct evidence value.

# Adapter boundary

Adapters translate host mechanisms into Harness Rig contracts.

They should not define:

- project risk policy;
- security requirements;
- authority precedence;
- acceptance semantics;
- canonical knowledge storage;
- portable recurrence scheduler/persistence.

They may own host-specific:

- spawn mechanisms;
- runtime resolution;
- concurrency/idempotency primitives;
- native evidence collection.

# Machine-readable matrix

Store compatibility as data and generate documentation from it.

Example:

```yaml
hosts:
  claude:
    fresh_worker: verified
    read_only_worker: verified
    worker_model_override: unverified
  codex:
    fresh_worker: verified
    worker_effort_override: partial
  copilot:
    fresh_worker: experimental
```

## Related

- [Target architecture](target-architecture.md)
- [TacticSwitch loop and runtime-policy proposals disposition](tacticswitch-loop-proposals-disposition.md)
- [Roadmap](roadmap.md)

# Authorization versus technical permission

Host read/write/process/network capability is technical capability, not an AuthorizationGrant. "
    "Topology may request restrictions; adapters enforce/observe them; neither may broaden authorization. "
    "If required read-only isolation cannot be enforced, return `BLOCKED`.
