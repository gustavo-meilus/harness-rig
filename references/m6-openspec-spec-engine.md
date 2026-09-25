---
id: harness-rig-m6-openspec-spec-engine
title: M6 OpenSpec first-class SpecEngine implementation
summary: Implemented r8.6 OpenSpec adapter, authority fingerprint profile, referenced-spec handling, effective health checks, guarded archive transition, and verification boundaries.
version: planning-baseline-2026-09-25-r8.6
updated: '2026-09-25'
provenance:
- Harness Rig M6 implementation and adversarial verification, 2026-09-25
- OpenSpec v1.13.2 release page, package metadata, CLI docs, and agent contract rechecked 2026-09-25
- Harness Rig M1-M5 trust, core-promotion, and Context verification evidence
- Skill Kit more-with-less v1.0.2 minimum-sufficient engineering doctrine
---
# Status

M6 completed with **PASS** at revision `r8.6`.

OpenSpec is now the first-class external `SpecEngine` for behavior-changing work while remaining optional to base Harness Rig. The compatibility profile implemented in M6 is intentionally narrow: OpenSpec `1.13.2` and its current public machine-readable CLI contracts.

# Implemented boundary

```text
DirectAuthorityProvider
  -> Stable AuthorityRef v1

OpenSpecAdapter (Experimental provider adapter)
  -> OpenSpec 1.13.2 CLI JSON surfaces
  -> Stable AuthorityRef v1
```

The shared `SpecEngine` surface remains Experimental and contains only operations used by current consumers:

```text
available
health
resolve authority
archive
```

No registry, plugin SDK, dependency-injection framework, vendored OpenSpec parser, copied schema implementation, or OpenSpec package dependency was introduced.

# Authority fingerprint profile

M6 profile identifier:

```text
harness-rig/openspec-authority-profile/v1
```

Authority-bearing inputs are:

- repo-local OpenSpec root identity;
- selected change identity and schema identity;
- the effective artifact graph;
- content digests of completed non-task planning artifacts;
- explicit skipped-artifact markers such as `skip_specs`;
- effective project planning context;
- per-authority-artifact rules;
- full machine-readable content of resolved referenced specifications that are referenced by authority-bearing artifacts.

Normally non-authority-bearing inputs are:

- task/checklist content in the default `tasks` artifact;
- timestamps and creation bookkeeping;
- incidental `.openspec.yaml` metadata that does not change the effective graph;
- the OpenSpec executable version itself.

The engine version is nevertheless a compatibility/health predicate. An unsupported version blocks the workflow rather than silently changing authority semantics.

Unknown custom planning artifacts are treated conservatively as authority-bearing. M6 does not attempt to infer arbitrary task-like semantics from custom artifact names.

# Referenced authority

Authority-bearing references are taken from the current OpenSpec instruction surface. For each resolved referenced spec, Harness Rig asks OpenSpec for the full structured spec representation and binds its semantic content into the authority fingerprint.

An unresolved, truncated, malformed, or unreadable reference used by an authority-bearing artifact produces `BLOCKED`.

An unresolved reference present only on the default task artifact does not alter authority and does not block authority resolution. This is deliberate: only references that can change agreed behavior/constraints belong in authority identity.

# Effective health

M6 health requires more than process exit zero. The adapter checks:

```text
compatible OpenSpec version
repo-local root resolution and doctor health
planning/artifact graph completeness
strict change validation
current apply instructions
current archive instructions
effective context/rule shapes
authority-bearing reference resolution
```

For archive, task completion is also required.

`skip_specs` can satisfy a planning artifact when OpenSpec reports it as skipped, but it never bypasses health, strict validation, authorization, state binding, transition checks, or Harness Rig acceptance.

Primary OpenSpec Store roots are intentionally not archive-qualified in M6 because Stable `StateIdentity` currently observes the repository Git worktree, not an external primary store. Read-only referenced stores are supported as authority inputs. Broader primary-store/state semantics must earn a later extension.

# Semantic review boundary

OpenSpec strict validation is not treated as semantic proof.

When Assurance requires an independent semantic-coherence predicate, the guarded archive accepts only explicit `PASS`; `FAIL` or unknown blocks before mutation. M6 does not invent an OpenSpec semantic-verification API where the public machine contract does not provide one.

# Guarded archive

The experimental CLI surface is:

```text
harness-rig spec archive
```

The transition is:

```text
(A0, S0)
  -> OpenSpec readiness receipt
  -> bounded AuthorizationGrant for spec_archive
  -> AcceptanceVerdict
  -> openspec archive <change> --yes --json
  -> filesystem/list postconditions
  -> (A1, S1)
  -> transition EvidenceReceipt
  -> explicit recheck of pre-archive receipt/grant against A1/S1
```

A successful archive must leave the selected change absent from the active OpenSpec list and the reported archive path present. Command failure, partial mutation, unreadable post-state, or postcondition mismatch returns `BLOCKED`.

The post-transition recheck must not accept pre-archive evidence/authorization as fresh for `(A1,S1)`. The current Experimental receipt/verdict schemas are reused; M6 does not promote them.

Capability-retirement cases whose affected main spec disappears are fail-closed in the M6 post-state reader rather than inferred from warning text. A later extension may support retirement only when exact machine-readable retirement identity is available and tested.

# Verification

M6 adversarial coverage includes:

- OpenSpec absent while base Direct Authority remains operational;
- OpenSpec-required path unavailable -> `BLOCKED`;
- supported-version/effective-health PASS;
- tasks-only and incidental metadata edits do not change authority;
- proposal/spec/design/context/rule/referenced-spec changes do change authority;
- custom artifact graph consumption without freezing default paths;
- `skip_specs` without verification bypass;
- unresolved authority-bearing reference -> `BLOCKED`;
- malformed effective rules -> `BLOCKED`;
- strict validation failure -> `BLOCKED`;
- unhealthy root and unsupported primary store -> `BLOCKED`;
- required semantic-coherence failure -> `BLOCKED` before mutation;
- missing bounded authorization -> `BLOCKED`;
- archive partial mutation and postcondition mismatch -> `BLOCKED`;
- successful archive transition receipt plus final stale-precondition rejection;
- subprocess invocation uses explicit argv with `shell=False`.

M6 does not advance repository enforcement, host qualification, Playwright/gate platform work, product CLI finalization, Git-history qualification, or M7+ concerns.

Runtime-evidence limit: the verification sandbox did not have a local `openspec` executable. Adapter semantics were exercised against deterministic fixtures matching the rechecked 1.13.2 public machine contract, plus an explicit subprocess argv/`shell=False` boundary test. Live clean-process OpenSpec qualification is not claimed by M6.
