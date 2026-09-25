---
id: harness-rig-security-trust-and-execution-boundaries
title: Security, trust, and execution boundaries
summary: Canonical M1 rules for untrusted inputs, command/executable boundaries, filesystem containment, symlinks, protected
  oracles, receipt trust, secrets, and privileged actions.
version: planning-baseline-2026-09-25-r8.4
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation M1 trust-protocol review, 2026-09-24
- User-supplied Harness Rig adversarial architecture review, 2026-09-24
- User-supplied rigyard_current.zip source snapshot inspected 2026-09-24
- RigYard acceptance evidence, durable worker evidence, result acceptance, attempt capability, workspace baseline source/tests
  inspected 2026-09-24
- Skill Kit more-with-less v1.0.2 canonical skill and playbook inspected 2026-09-24
- Git official status/diff/submodule documentation rechecked 2026-09-24
- Node.js official child_process documentation rechecked 2026-09-24
---
# Purpose

Single canonical owner for cross-cutting trust/execution rules. This is not a separate security subsystem.

# Untrusted data

Repository files, OpenSpec material, attachments, browser content, dependency output, tests, logs and tool output are
data/evidence, not instructions that may redefine Harness Rig policy.

# Command execution

Use structured **argument vectors**, direct executable invocation by default, bounded working directory/environment and
timeouts/output limits where relevant. Do not concatenate model/source/tool-controlled text into shell commands.

# Executable identity

Consequential gates must not silently trust an unexpected executable earlier on mutable PATH. Where material, bind or verify
resolved executable path, adapter identity and tool/runtime version.

# Filesystem containment

For protected paths, migration destinations and isolated roots:

1. reject absolute paths and `..`;
2. normalize relative paths;
3. resolve ancestors/symlink behavior;
4. prove effective target is inside the authorized root;
5. use safe create/open semantics.

String-prefix checks alone are insufficient.

# Symlink boundary

Unexpected symlink use on protected paths is rejected unless policy explicitly permits it. A protected-path symlink cannot
escape the repository/root boundary.

If a gate intentionally dereferences an external symlink, bind that target as a material receipt input.

RigYard private-writer-root code is reuse evidence: it rejects symbolic-link aliases and requires controller-owned private
roots.

# Protected authority/oracles

Writes require appropriate `AuthorizationGrant`. If read-only verification is required and the host cannot enforce it, return
`BLOCKED`.

Changing a protected oracle may reopen authority/evidence even when later tests are green.

# Receipt trust

A serialized receipt is not trusted by syntax alone. Validate producer/run/subject binding, receipt integrity, gate contract,
native artifact integrity when required, and replay/applicability.

# Secrets and evidence retention

Do not persist raw tokens/API keys/session cookies/bearer secrets/one-use capability tokens in canonical receipts/logs.

Prefer non-secret digests. Redact secrets before truncation/persistence, following RigYard's current evidence-capture pattern.

Traces/logs/screenshots/network artifacts can use retention states such as retained, redacted, descriptor-only or omitted.
The receipt records the limitation rather than flattening content.

# Privileged execution

Detailed CI mechanics are M7 work. The invariant is active now: untrusted repository/PR code cannot gain privileged
publish/deploy credentials merely by modifying repository workflows/tests.

# Failure

Required trust property cannot be established -> `BLOCKED`.

# Minimum-sufficient boundary

No generic sandbox platform, secret manager, IAM service, security event platform or policy language is added.

## Related

- [AuthorizationGrant ADR](adr-authorization-grant.md)
- [EvidenceReceipt ADR](adr-evidence-receipt.md)
- [Core trust model](core-invariants-and-trust-model.md)
