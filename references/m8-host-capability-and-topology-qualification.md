---
id: harness-rig-m8-host-capability-topology-qualification
title: M8 host capability and topology qualification
summary: Native qualification of the minimum local-process host, requested/resolved/observed runtime facts, fresh-verifier boundaries, and evidence-gated isolated-writer semantics.
version: planning-baseline-2026-09-25-r8.8
updated: '2026-09-25'
provenance:
- Harness Rig M8 implementation and native subprocess probes, 2026-09-25
- Harness Rig r8.7 host-adapter/capability baseline
- RigYard retained Codex/Linux v0.1 host evidence and explicit missing isolated-writer packet, inspected in canonical baseline
- TacticSwitch fresh-verifier non-ownership and fail-closed worker semantics, canonical source baseline checked 2026-09-25
- Skill Kit More With Less v1.0.2, minimum-sufficient mechanism doctrine
---
# Result

M8 is a host-capability qualification milestone, not a multi-host framework milestone.

The first Stable host candidate is:

```text
local-subprocess
```

This is the native direct-process boundary already used by the executable Harness Rig path. It is Stable only for the capabilities independently exercised in the current runtime. It is not a claim that a Codex, Claude Code, or Copilot worker adapter is Stable.

The M8 runtime baseline observed:

```text
Python 3.13.5  /opt/pyvenv/bin/python
Git 2.47.3     /usr/bin/git
codex           unavailable
claude          unavailable
copilot         unavailable
```

Therefore unavailable external-agent adapters are not promoted.

# Maturity model

Harness Rig preserves the RigYard distinction instead of collapsing source presence into support maturity:

```text
IMPLEMENTED
LOCAL_VERIFIED
NATIVE_QUALIFIED
STABLE
```

`UNSUPPORTED` is an explicit non-claim.

A Stable capability requires retained evidence. `isolated_writer` has an additional executable admission rule: Stable construction is rejected unless evidence is explicitly marked as formal native evidence. This preserves the supplied RigYard negative evidence that the formal isolated-writer packet is absent.

# CapabilitySet status

`CapabilitySet` remains **Experimental/module-owned**. M8 refines it from observed behavior; it does not promote it into Stable core.

For `local-subprocess`:

| Capability | Maturity | M8 result |
|---|---|---|
| `clean_process` | Stable | native-qualified |
| `process_launch` | Stable | native-qualified |
| `runtime_identity_observation` | Stable | native-qualified |
| `crash_reconciliation` | Stable | native-qualified |
| `fresh_verifier` | Unsupported | fail closed |
| `isolated_worker` | Unsupported | fail closed |
| `read_only_worker` | Unsupported | fail closed |
| `worktree_worker` | Unsupported | fail closed |
| `permission_enforcement` | Unsupported | fail closed |
| `isolated_writer` | Unsupported | formal native evidence absent |

Stable here qualifies the adapter's narrow supported surface, not every capability a future agent host might expose.

# Requested, resolved, observed

`RuntimeResolution` remains **Experimental/module-owned** and explicitly separates:

```text
requested  -> portable execution request
resolved   -> adapter/runtime resolution
observed   -> facts actually seen during execution
```

The local adapter records executable and working-directory facts plus exit outcome and stdout/stderr digests. Unknown/unavailable resolution does not become observed fact.

Technical host capability remains distinct from `AuthorizationGrant`. The adapter can launch a process; it cannot manufacture or broaden action authorization.

# Clean-process qualification

`harness-rig doctor` runs a fresh native subprocess probe using the current absolute Python executable with `-I -S`, a temporary clean working directory, a minimal environment, `stdin=DEVNULL`, captured output, a bounded timeout, and `shell=False`.

The probe must observe:

- the expected executable;
- the probe working directory;
- isolated Python mode;
- no site initialization;
- successful clean-process launch.

Failure or ambiguity returns `BLOCKED` rather than inferring capability from installed files.

# Fresh verifier boundary

Fresh verification is not a different label for the same actor/context.

Eligibility requires all applicable predicates:

```text
verifier identity != implementer identity
verifier context != implementer context
verifier did not own/implement the batch
required read-only boundary is actually enforced
```

If any required predicate is false or unobserved, the verifier is `BLOCKED` for that assurance requirement.

The `local-subprocess` adapter does not provide a qualified worker/context or read-only enforcement mechanism, so it does not claim `fresh_verifier` even though the pure eligibility predicate is now executable.

# Isolation and isolated writers

Read-only worker, isolated worker, worktree worker, permission enforcement, and isolated writer are optional capability claims, not baseline host requirements.

A topology request that marks one of those capabilities required is rejected before process launch when the adapter cannot prove it.

The retained RigYard baseline distinguishes implemented/local isolated-writer machinery from formal native qualification and states that the formal isolated-writer evidence packet is missing. M8 preserves that distinction and does not convert the historical implementation into a Stable Harness Rig claim.

# Crash and reconciliation

Native tests prove that:

- a non-zero child exit is attributed to the launched process with exit code and output digests;
- timeout is `BLOCKED`;
- a subsequent clean launch can succeed after crash/timeout;
- failed attempts and recovered attempts have distinct launch identities.

This is bounded local-process crash/reconciliation evidence, not a distributed worker-recovery platform.

# Verification

```text
M8-T01 PASS - local-subprocess selected and native-qualified as the first narrow Stable host
M8-T02 PASS - IMPLEMENTED / LOCAL_VERIFIED / NATIVE_QUALIFIED / STABLE distinction retained
M8-T03 PASS - CapabilitySet refined from executable native observations
M8-T04 PASS - fresh verifier requires real identity/context/non-ownership/read-only predicates
M8-T05 PASS - isolated_writer remains optional and formal-native-evidence-gated

M8-V01 PASS - clean-process discovery/launch
M8-V02 PASS - requested/resolved/observed facts retained
M8-V03 PASS - unsupported read-only/isolation requirements block before launch
M8-V04 PASS - crash/reconciliation and evidence attribution
M8-V05 PASS - Stable isolated_writer construction requires formal native evidence
```

# Deliberate limits

M8 does not claim:

- Stable Codex/Claude/Copilot adapters;
- read-only or isolated workers on `local-subprocess`;
- isolated writers;
- worker model/effort overrides;
- a Stable `CapabilitySet` or `RuntimeResolution` core schema;
- M9 gate/Playwright/architecture work.

## Related

- [Host adapters and capability negotiation](host-adapters-and-capabilities.md)
- [RigYard current source and verification baseline](rigyard-current-source-and-verification-baseline.md)
- [Contracts, state, and evidence](contracts-state-and-evidence.md)
- [Roadmap](roadmap.md)
