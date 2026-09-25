from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .authority import AuthorityRef
from .canonical import file_digest, sha256_bytes
from .evidence import ArtifactRef, EvidenceReceipt, InputBinding, artifact_path, bind_path
from .state import capture_state


GATE_CLAIM_SCHEMA = "harness-rig/gate-claim/experimental-v1"
GATE_OUTCOME_SCHEMA = "harness-rig/gate-outcome/experimental-v1"
GATE_OUTCOMES = frozenset({"PASS", "FAIL", "BLOCKED", "NOT_RUN", "MUTATED"})


@dataclass(frozen=True)
class GateClaim:
    """Minimum provider-neutral claim identity used by gate adapters.

    Provider-native diagnostics remain provider-owned. This value only states
    what is being claimed and which gate contract is expected to decide it.
    """

    schema: str
    claim_id: str
    kind: str
    gate_id: str
    gate_contract_version: str
    required: bool = True

    @classmethod
    def create(
        cls, *, claim_id: str, kind: str, gate_id: str,
        gate_contract_version: str = "experimental-v1", required: bool = True,
    ) -> "GateClaim":
        values = (claim_id, kind, gate_id, gate_contract_version)
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError("invalid-gate-claim")
        if not isinstance(required, bool):
            raise ValueError("invalid-gate-claim-required")
        return cls(
            GATE_CLAIM_SCHEMA, claim_id, kind, gate_id,
            gate_contract_version, required,
        )


@dataclass(frozen=True)
class GateOutcome:
    """Minimum common gate outcome. Provider details stay outside this shape."""

    schema: str
    outcome: str
    reasons: tuple[str, ...] = ()
    attempt_count: int = 0
    flaky: bool = False

    @classmethod
    def create(
        cls, outcome: str, *, reasons: tuple[str, ...] = (),
        attempt_count: int = 0, flaky: bool = False,
    ) -> "GateOutcome":
        if outcome not in GATE_OUTCOMES:
            raise ValueError("invalid-gate-outcome")
        if not isinstance(attempt_count, int) or attempt_count < 0:
            raise ValueError("invalid-gate-attempt-count")
        if not isinstance(flaky, bool):
            raise ValueError("invalid-gate-flaky")
        if outcome == "PASS" and reasons:
            raise ValueError("passing-gate-outcome-cannot-have-reasons")
        if outcome != "PASS" and not reasons:
            raise ValueError("nonpassing-gate-outcome-requires-reason")
        if any(not isinstance(reason, str) or not reason for reason in reasons):
            raise ValueError("invalid-gate-outcome-reason")
        return cls(GATE_OUTCOME_SCHEMA, outcome, tuple(reasons), attempt_count, flaky)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class GateRequest:
    repo: Path
    repository_id: str
    claim_id: str
    subject_ref: str
    authority: AuthorityRef
    run_id: str
    producer_id: str
    argv: tuple[str, ...] | None
    gate_id: str = "command/test"
    gate_contract_version: str = "experimental-v1"
    input_paths: tuple[str, ...] = ()
    artifact_paths: tuple[str, ...] = ()
    expected_executable: str | None = None
    cwd: str = "."
    timeout_seconds: float = 30.0


class CommandGate:
    """One deterministic command/test gate for the direct trust path."""

    @staticmethod
    def run(req: GateRequest) -> EvidenceReceipt:
        repo = req.repo.resolve()
        state_before = capture_state(repo, req.repository_id)
        bindings = tuple(bind_path(repo, p) for p in req.input_paths)
        artifacts_before: tuple[ArtifactRef, ...] = ()

        started = _now()

        if req.argv is None:
            finished = _now()
            return EvidenceReceipt.create(
                claim_id=req.claim_id,
                subject_ref=req.subject_ref,
                authority_id=req.authority.authority_id,
                state_before_id=state_before.state_id,
                state_after_id=state_before.state_id,
                certified_state_id=None,
                input_bindings=bindings,
                producer_id=req.producer_id,
                run_id=req.run_id,
                gate_id=req.gate_id,
                gate_contract_version=req.gate_contract_version,
                executable_identity=None,
                tool_version=None,
                outcome="NOT_RUN",
                started_at=started,
                finished_at=finished,
                artifacts=artifacts_before,
            )

        executable = shutil.which(req.argv[0])
        if executable is None:
            finished = _now()
            return EvidenceReceipt.create(
                claim_id=req.claim_id,
                subject_ref=req.subject_ref,
                authority_id=req.authority.authority_id,
                state_before_id=state_before.state_id,
                state_after_id=state_before.state_id,
                certified_state_id=None,
                input_bindings=bindings,
                producer_id=req.producer_id,
                run_id=req.run_id,
                gate_id=req.gate_id,
                gate_contract_version=req.gate_contract_version,
                executable_identity=None,
                tool_version=None,
                outcome="BLOCKED",
                started_at=started,
                finished_at=finished,
                artifacts=(),
            )

        resolved_exe = str(Path(executable).resolve())
        if req.expected_executable is not None:
            expected = str(Path(req.expected_executable).resolve())
            if resolved_exe != expected:
                finished = _now()
                return EvidenceReceipt.create(
                    claim_id=req.claim_id,
                    subject_ref=req.subject_ref,
                    authority_id=req.authority.authority_id,
                    state_before_id=state_before.state_id,
                    state_after_id=state_before.state_id,
                    certified_state_id=None,
                    input_bindings=bindings,
                    producer_id=req.producer_id,
                    run_id=req.run_id,
                    gate_id=req.gate_id,
                    gate_contract_version=req.gate_contract_version,
                    executable_identity=resolved_exe,
                    tool_version=None,
                    outcome="BLOCKED",
                    started_at=started,
                    finished_at=finished,
                    artifacts=(),
                )

        cwd = (repo / req.cwd).resolve()
        if repo not in [cwd, *cwd.parents]:
            outcome = "BLOCKED"
            p = None
        else:
            try:
                p = subprocess.run(
                    [resolved_exe, *req.argv[1:]],
                    cwd=cwd,
                    capture_output=True,
                    text=False,
                    shell=False,
                    timeout=req.timeout_seconds,
                )
                outcome = "PASS" if p.returncode == 0 else "FAIL"
            except subprocess.TimeoutExpired as exc:
                p = None
                outcome = "BLOCKED"

        state_after = capture_state(repo, req.repository_id)
        if state_after.state_id != state_before.state_id:
            outcome = "MUTATED"

        artifact_refs = []
        for rel in req.artifact_paths:
            path = repo / rel
            if path.exists() and path.is_file():
                artifact_refs.append(artifact_path(repo, rel))

        # Capture stdout/stderr digests as native diagnostic artifacts without making
        # receipt correctness depend on persisted plaintext.
        if p is not None:
            artifact_refs.append(ArtifactRef("stdout-digest", "inline:stdout", sha256_bytes(p.stdout)))
            artifact_refs.append(ArtifactRef("stderr-digest", "inline:stderr", sha256_bytes(p.stderr)))

        finished = _now()
        return EvidenceReceipt.create(
            claim_id=req.claim_id,
            subject_ref=req.subject_ref,
            authority_id=req.authority.authority_id,
            state_before_id=state_before.state_id,
            state_after_id=state_after.state_id,
            certified_state_id=state_before.state_id if outcome == "PASS" else None,
            input_bindings=bindings,
            producer_id=req.producer_id,
            run_id=req.run_id,
            gate_id=req.gate_id,
            gate_contract_version=req.gate_contract_version,
            executable_identity=resolved_exe,
            tool_version=None,
            outcome=outcome,
            started_at=started,
            finished_at=finished,
            artifacts=tuple(artifact_refs),
        )
