from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .acceptance import AcceptanceVerdict, evaluate_acceptance
from .assurance import AssurancePlan, AssuranceRequirement
from .authority import DirectAuthority
from .authorization import AuthorizationGrant
from .evidence import EvidenceReceipt
from .gate import CommandGate, GateRequest
from .state import capture_state
from .topology import DirectTopology


@dataclass(frozen=True)
class VerticalSliceRequest:
    repo: Path
    repository_id: str
    authority_path: str
    subject_ref: str
    claim_id: str
    argv: tuple[str, ...] | None
    run_id: str
    producer_id: str
    principal: str
    decision_for: str
    resource: str
    now: str
    grant: AuthorizationGrant | None
    input_paths: tuple[str, ...] = ()
    artifact_paths: tuple[str, ...] = ()
    expected_executable: str | None = None


@dataclass(frozen=True)
class VerticalSliceResult:
    topology: DirectTopology
    receipt: EvidenceReceipt
    verdict: AcceptanceVerdict


def run_vertical_slice(req: VerticalSliceRequest) -> VerticalSliceResult:
    authority = DirectAuthority.from_file(req.repo, req.authority_path, req.subject_ref)
    topology = DirectTopology.direct(req.principal)
    requirement = AssuranceRequirement(
        claim_id=req.claim_id,
        gate_id="command/test",
        gate_contract_version="experimental-v1",
        decision_for=req.decision_for,
        require_authorization=True,
    )
    assurance = AssurancePlan.single(subject_ref=req.subject_ref, requirement=requirement)

    receipt = CommandGate.run(GateRequest(
        repo=req.repo,
        repository_id=req.repository_id,
        claim_id=req.claim_id,
        subject_ref=req.subject_ref,
        authority=authority,
        run_id=req.run_id,
        producer_id=req.producer_id,
        argv=req.argv,
        input_paths=req.input_paths,
        artifact_paths=req.artifact_paths,
        expected_executable=req.expected_executable,
    ))
    current_state = capture_state(req.repo, req.repository_id)
    verdict = evaluate_acceptance(
        repo=req.repo,
        authority=authority,
        current_state=current_state,
        plan=assurance,
        receipt=receipt,
        grant=req.grant,
        principal=req.principal,
        run_id=req.run_id,
        now=req.now,
        trusted_issuers={"local-authority"},
        resource=req.resource,
    )
    return VerticalSliceResult(topology=topology, receipt=receipt, verdict=verdict)
