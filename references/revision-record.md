---
id: harness-rig-progressive-revision-record
title: Harness Rig progressive revision record
summary: Current progressive-remediation milestone status, verification result, evidence limits, and next permitted milestone.
version: planning-baseline-2026-09-25-r8.8
updated: '2026-09-25'
provenance:
- Harness Rig progressive remediation M0-M7 execution and verification, 2026-09-24 through 2026-09-25
- Skill Kit more-with-less v1.0.2 minimum-sufficient engineering doctrine, applied 2026-09-25
- Harness Rig retained RigYard host-evidence maturity baseline
- Harness Rig M8 native local-process qualification and adversarial verification, 2026-09-25
---
# Current revision

```text
milestone: M8
package revision: r8.8
result: PASS
date: 2026-09-25
next allowed milestone: M9
resume task: M9-T01
```

# M8 implemented boundary

M8 qualifies one deliberately narrow host adapter instead of inventing a multi-host framework:

```text
local-subprocess
  Stable: clean_process
  Stable: process_launch
  Stable: runtime_identity_observation
  Stable: crash_reconciliation
  Unsupported: fresh_verifier/read_only_worker/isolated_worker/worktree_worker/permission_enforcement/isolated_writer
```

`CapabilitySet` and `RuntimeResolution` remain Experimental/module-owned.

# Maturity and topology rules

M8 preserves `IMPLEMENTED -> LOCAL_VERIFIED -> NATIVE_QUALIFIED -> STABLE` as distinct support maturity states. A Stable capability needs retained evidence. A Stable isolated-writer claim additionally requires explicitly marked formal native evidence.

Fresh verifier eligibility is now an executable boundary: different worker identity, different context identity, non-ownership of the implementation batch, and actually enforced read-only access when required. A label change alone is not freshness.

Technical host capability remains separate from `AuthorizationGrant`.

# Verification

```text
M3: 22/22 PASS
M4: 15/15 PASS
M5: 14/14 PASS
M6: 16/16 PASS
M7: 14/14 PASS
M8: 14/14 PASS
combined: 95/95 PASS
M8-V01 ... M8-V05: PASS
```

Native doctor evidence is retained in `verification/m8-host-qualification.json`; the runtime baseline records Python 3.13.5, Git 2.47.3, and unavailable Codex/Claude/Copilot executables.

# Evidence limit

M8 does not claim Stable external-agent adapters, read-only/isolated workers, isolated writers, or worker model/effort controls. The retained RigYard isolated-writer implementation remains below Stable because its formal native packet is explicitly absent.

# Deferred

M8 does not perform M9 gate/Playwright/architecture/mutation work, M10 product CLI/release provenance finalization, M11 history qualification, or M12/1.0 qualification.
